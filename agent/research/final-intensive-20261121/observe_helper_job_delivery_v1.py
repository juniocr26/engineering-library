"""Observe real opt-in helper/job journals with injected faults, without production startup."""
from pathlib import Path
import argparse,datetime,hashlib,json,sys,subprocess
parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--output-root',type=Path,required=True);args=parser.parse_args();ROOT=args.root.resolve();P=ROOT/'agent/research/final-intensive-20261121';folder=args.output_root.resolve();folder.mkdir(mode=0o700)
sys.path.insert(0,str(ROOT/'agent/tools'));import documentation_retrieval as h;import documentation_job_budget as j
sha=lambda b:hashlib.sha256(b).hexdigest();source=b'package owned\n\nfunc Value() int { return 7 }\n';now=datetime.datetime.now(datetime.timezone.utc)
cases=[{'id':'intact-cached','cached':True,'fault':None,'expected_status':'COMPLETED','expected_helper_status':'DUPLICATE','expected_repeat':'DUPLICATE_COMPLETED'}]
for kind in ['TimeoutExpired','CalledProcessError','SubprocessError','OSError']:
 for cached in [False,True]:
  unknown=cached and kind!='OSError';cases.append({'id':('cached-' if cached else 'fresh-')+kind,'cached':cached,'fault':kind,'expected_status':'UNKNOWN_COMPLETION' if unknown else 'COMPLETED','expected_helper_status':None if unknown else ('REFUSED' if cached else 'INCONCLUSIVE'),'expected_repeat':'UNKNOWN_COMPLETION' if unknown else 'DUPLICATE_COMPLETED'})
protocol={'at':now.isoformat(),'hypothesis':'Real JobBoundRetrieval converts cached Go subprocess errors into durable unresolved reservations with no automatic redispatch after coordinator reconstruction, while returned helper INCONCLUSIVE/REFUSED is a completed job result.','implementation_hashes':{x:sha((ROOT/'agent/tools'/x).read_bytes()) for x in ['documentation_retrieval.py','documentation_job_budget.py','documentation_workspace.py']},'source_sha256':sha(source),'cases':cases,'scope':'Real optional Python helper/job classes, new owned source/journals and fault injection only. Not target Go execution, native timeout, background service, neural inference, production workflow, process-crash durability or cross-platform behavior.','no_production_or_permanent_tests_modified':True}
(folder/'protocol.json').write_bytes(j.canonical(protocol))
def snapshot(path):return {f.name:sha(f.read_bytes()) for f in sorted(path.iterdir()) if f.is_file()}
records=[];failure=None
try:
 for case in cases:
  base=folder/case['id'];base.mkdir(mode=0o700);src=base/'source';hj=base/'helper-journal';jj=base/'job-journal'
  for f in [src,hj,jj]:f.mkdir(mode=0o700)
  (src/'owned.go').write_bytes(source);registry={'owned':{'root':str(src),'revision':'1'*40,'files':{'owned.go':{'sha256':sha(source),'language':'go','selectors':['Value']}}}};request={'request_id':'observation','source_id':'owned','revision':'1'*40,'path':'owned.go','qualified_symbol':'Value','expected_sha256':sha(source)}
  config={'job_id':'owned-delivery','registry_sha256':sha(h.canonical(registry)),'max_steps':2,'max_quote_bytes':12288,'deadline_utc':(now+datetime.timedelta(hours=1)).isoformat()}
  (base/'registry.json').write_bytes(h.canonical(registry));(base/'request.json').write_bytes(h.canonical(request));(base/'job-config.json').write_bytes(j.canonical(config))
  helper=h.HelperRetrieval(registry,hj);bootstrap=None
  if case['cached']:
   bootstrap=helper.request(request);assert bootstrap['status']=='FOUND';(base/'bootstrap.json').write_bytes(h.canonical(bootstrap))
  helper_before=snapshot(hj);budget=j.HelperJobBudget(jj,config,clock=lambda:now);coord=j.JobBoundRetrieval(helper,budget);calls=[];original=h.subprocess.run
  def inject(*a,**kw):
   calls.append({'command':a[0] if a else kw.get('args'),'timeout':kw.get('timeout')});kind=case['fault']
   if kind=='TimeoutExpired':raise subprocess.TimeoutExpired('owned-job-fault',20)
   if kind=='CalledProcessError':raise subprocess.CalledProcessError(17,'owned-job-fault')
   if kind=='SubprocessError':raise subprocess.SubprocessError('owned-job-fault')
   raise OSError('owned-job-fault')
  try:
   if case['fault']:h.subprocess.run=inject
   result=coord.request(request)
  finally:h.subprocess.run=original
  (base/'first-result.json').write_bytes(j.canonical(result));job_after=snapshot(jj);helper_after=snapshot(hj)
  # Reconstruct real classes using unchanged roots/config; an owned guard records any unexpected dispatch.
  resumed_helper=h.HelperRetrieval(registry,hj);resumed_budget=j.HelperJobBudget(jj,config,clock=lambda:now);resumed=j.JobBoundRetrieval(resumed_helper,resumed_budget);redispatch=[]
  def forbidden(req):redispatch.append(req);raise AssertionError('unexpected automatic dispatch')
  resumed_helper.request=forbidden
  repeated=resumed.request(request);(base/'resumed-result.json').write_bytes(j.canonical(repeated));helper_status=result.get('helper_result',{}).get('status');matched=result['status']==case['expected_status'] and helper_status==case['expected_helper_status'] and repeated['status']==case['expected_repeat'] and not redispatch and snapshot(jj)==job_after and snapshot(hj)==helper_after
  record={**case,'result':result,'resumed_result':repeated,'injected_subprocess_calls':calls,'unexpected_redispatch_count':len(redispatch),'helper_before':helper_before,'helper_after':helper_after,'cached_helper_journal_unchanged':helper_before==helper_after if case['cached'] else None,'job_after':job_after,'job_unchanged_on_resume':snapshot(jj)==job_after,'helper_unchanged_on_resume':snapshot(hj)==helper_after,'matched':matched};records.append(record);(base/'observation.json').write_bytes(j.canonical(record))
except Exception as error:failure={'type':type(error).__name__,'text':str(error)}
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':sha((folder/'protocol.json').read_bytes()),'records':records,'matched':sum(r['matched'] for r in records),'case_count':len(records),'expected_case_count':len(cases),'failure':failure,'new_model_calls':0,'target_source_executed':False,'job_classes_executed':True,'actual_OS_fault_induced':False,'process_crash_tested':False,'production_modified':False,'accuracy_metric':None}
(folder/'results.json').write_bytes(j.canonical(result));print(json.dumps({k:v for k,v in result.items() if k!='records'}));print(json.dumps([{'id':r['id'],'status':r['result']['status'],'helper_status':r['result'].get('helper_result',{}).get('status'),'resume':r['resumed_result']['status'],'redispatch':r['unexpected_redispatch_count'],'matched':r['matched']} for r in records]));assert failure is None and len(records)==len(cases) and all(r['matched'] for r in records)
