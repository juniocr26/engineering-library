"""Owned failure-injection observation at existing helper/job seam; no production patch."""
import contextlib,datetime,hashlib,json,sys,subprocess
from pathlib import Path
from unittest.mock import patch
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
sys.path.insert(0,str(ROOT/'agent/tools'))
import documentation_retrieval as retrieval
import documentation_job_budget as jobs
from documentation_workspace import directory,write_new
protocol=json.loads((P/'cached-helper-job-seam-protocol-v1.json').read_text())
for f in protocol['source_files']:
    assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
BASE=P/'cached-helper-job-seam-v1'
BASE.mkdir(exist_ok=False)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def snapshot(folder):return {f.name:sha(f.read_bytes()) for f in sorted(folder.iterdir()) if f.is_file()}
def persist(path,obj):
    with path.open('x') as f:json.dump(obj,f,indent=2,ensure_ascii=False);f.write('\n')
class DeliveryAdapter:
    def __init__(self,helper,delivery_root,fail_write=False):
        self.helper=helper;self.delivery_root=delivery_root;self.fail_write=fail_write;self.last_delivery=None
    def __getattr__(self,name):return getattr(self.helper,name)
    def request(self,request):
        try:result=self.helper.request(request)
        except subprocess.SubprocessError as error:
            result={'version':retrieval.VERSION,'status':'INCONCLUSIVE','source_executed':False,
                    'runtime_bindings_verified':False,'owner_approved':False,
                    'reason':'Research adapter: cached revalidation subprocess fault; '+type(error).__name__+'; no retry or cached-result overwrite.',
                    'request_id':request['request_id'],'fault_class':type(error).__name__,
                    'research_only_not_production':True}
        encoded=jobs.canonical(result);name='helper-result-'+sha(encoded)+'.json'
        if self.fail_write:raise OSError('Owned injected delivery persistence failure')
        with directory(self.delivery_root) as fd:write_new(fd,name,encoded)
        self.last_delivery=self.delivery_root/name
        return result
rows=[]
for case in protocol['cases']:
    for condition in ['baseline','research_adapter']:
        folder=BASE/case['id']/condition;folder.mkdir(parents=True)
        source=folder/'source';journal=folder/'helper-journal';jobroot=folder/'job-journal';delivery=folder/'delivery'
        for d in [source,journal,jobroot,delivery]:d.mkdir()
        raw=protocol['owned_source'].encode();src=source/'owned.go';src.write_bytes(raw)
        source_before={'sha256':sha(src.read_bytes()),'mtime_ns':src.stat().st_mtime_ns}
        registry={'owned':{'root':str(source),'revision':'1'*40,'files':{'owned.go':{'sha256':sha(raw),'language':'go','selectors':['Helper']}}}}
        helper=retrieval.HelperRetrieval(registry,journal,max_steps=4,max_quote_bytes=24576)
        request={'request_id':'owned1','source_id':'owned','revision':'1'*40,'path':'owned.go','qualified_symbol':'Helper','expected_sha256':sha(raw)}
        seed=None
        if case['cached']:
            seed=helper.request(request);assert seed['status']=='FOUND',seed;persist(folder/'seed-result.json',seed)
        if case.get('corrupt_receipt'):
            receipt=journal/'owned1.receipt.json';pre=receipt.read_bytes();(folder/'seed-receipt-pre-corruption.json').write_bytes(pre)
            value=json.loads(pre);value['result_sha256']='0'*64;receipt.write_bytes(jobs.canonical(value))
        before=snapshot(journal);steps_before=helper.steps;quotes_before=helper.quote_bytes
        now=[datetime.datetime(2026,11,21,15,0,tzinfo=datetime.timezone.utc)]
        config={'job_id':'owned-job','registry_sha256':helper.registry_sha256,'max_steps':1,'max_quote_bytes':6144,'deadline_utc':(now[0]+datetime.timedelta(seconds=60)).isoformat()}
        budget=jobs.HelperJobBudget(jobroot,config,clock=lambda:now[0])
        adapted=DeliveryAdapter(helper,delivery,case.get('delivery_write_failure',False)) if condition=='research_adapter' else helper
        bound=jobs.JobBoundRetrieval(adapted,budget)
        original_extract=retrieval.extract
        def inject(*args,**kwargs):
            name=case['fault']
            if name is None:return original_extract(*args,**kwargs)
            if case.get('advance_clock_seconds'):now[0]+=datetime.timedelta(seconds=case['advance_clock_seconds'])
            if name=='TimeoutExpired':raise subprocess.TimeoutExpired(['owned-go-parser'],20)
            if name=='CalledProcessError':raise subprocess.CalledProcessError(9,['owned-go-parser'])
            if name=='SubprocessError':raise subprocess.SubprocessError('owned injected subprocess fault')
            if name=='ValueError':raise ValueError('owned injected cache validation value error')
            if name=='RuntimeError':raise RuntimeError('owned unexpected programming fault')
            raise AssertionError('Unknown frozen fault')
        with patch.object(retrieval,'extract',side_effect=inject) as observed:
            result=bound.request(request);first_calls=observed.call_count
            second=bound.request(request);second_calls=observed.call_count-first_calls
        after=snapshot(journal);source_after={'sha256':sha(src.read_bytes()),'mtime_ns':src.stat().st_mtime_ns}
        expected=case['reference_baseline_job'] if condition=='baseline' else case['reference_adapter_job']
        if result['status']!=expected:raise AssertionError((case['id'],condition,result,expected))
        completed=list(jobroot.glob('step-*-completed.json'));reservations=list(jobroot.glob('step-*-reserved.json'))
        assert len(reservations)==1 and second_calls==0 and source_before==source_after
        if case['cached']:assert before==after and helper.steps==steps_before and helper.quote_bytes==quotes_before
        assert not helper._request_lock.locked()
        helper_result=result.get('helper_result');delivery_info=None
        if condition=='research_adapter' and adapted.last_delivery:
            encoded=adapted.last_delivery.read_bytes();body=json.loads(encoded)
            assert body.get('source_executed') is False and body.get('runtime_bindings_verified') is False and body.get('owner_approved') is False
            if body['status']!='FOUND':assert 'evidence' not in body and body.get('quote_bytes',0)==0
            if completed:
                completion=json.loads(completed[0].read_text());assert completion['result_sha256']==sha(encoded)
            delivery_info={'path':str(adapted.last_delivery),'sha256':sha(encoded),'helper_status':body['status'],'fsynced_before_job_completion':True,'job_completion_hash_matches_body':bool(completed)}
            if case['reference_adapter_helper'] is not None:assert body['status']==case['reference_adapter_helper']
        if condition=='research_adapter' and case['reference_adapter_helper'] is None:assert delivery_info is None
        row={'case':case['id'],'condition':condition,'actual_result':result,'second_job_request':second,'expected_job_status':expected,'status_agrees':True,'extract_calls_in_observed_dispatch':first_calls,'extract_calls_in_second_job_request':second_calls,'source_before':source_before,'source_after':source_after,'cached_journal_before':before,'cached_journal_after':after,'cached_bytes_unchanged':before==after if case['cached'] else None,'helper_steps_before':steps_before,'helper_steps_after':helper.steps,'quote_bytes_before':quotes_before,'quote_bytes_after':helper.quote_bytes,'helper_lock_released':not helper._request_lock.locked(),'job_reservation_count':len(reservations),'job_completion_count':len(completed),'delivery_body':delivery_info,'not_source_execution':True,'not_production_fix':True}
        persist(folder/'observation.json',row);rows.append(row)
summary={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':'cached-helper-job-seam-protocol-v1.json','case_count':len(protocol['cases']),'condition_observations':len(rows),'all_frozen_status_expectations_match':all(r['status_agrees'] for r in rows),'cached_journals_unchanged':all(r['cached_bytes_unchanged'] is not False for r in rows),'all_source_hashes_and_mtimes_unchanged':all(r['source_before']==r['source_after'] for r in rows),'all_locks_released':all(r['helper_lock_released'] for r in rows),'automatic_redispatches':sum(r['extract_calls_in_second_job_request'] for r in rows),'all_job_reservations_once':all(r['job_reservation_count']==1 for r in rows),'observations':rows,'key_boundary':'Known cached SubprocessError can be delivered as accounted INCONCLUSIVE with immutable delivery body and job completion, without changing the prior FOUND cache. This is completed accounting of a failure, not retrieval success. Unexpected programming faults, persistence failure and late completion stay distinguishable.','production_helper_unchanged':True,'permanent_tests_added':False,'original_fault_is_simulated':True,'not_neural_adapter_recovery':True,'model_calls':0,'optimizer_updates':0,'gold':0}
persist(P/'cached-helper-job-seam-results-v1.json',summary)
print(json.dumps({k:v for k,v in summary.items() if k!='observations'},indent=2))
