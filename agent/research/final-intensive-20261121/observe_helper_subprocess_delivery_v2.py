"""Owned fault-injection observation of real helper/journal boundaries; no target Go execution."""
from pathlib import Path
import sys,json,hashlib,datetime,subprocess,argparse
parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--output-root',type=Path,required=True);args=parser.parse_args();ROOT=args.root.resolve();P=ROOT/'agent/research/final-intensive-20261121';sys.path.insert(0,str(ROOT/'agent/tools'))
import documentation_retrieval as helper
sha=lambda b:hashlib.sha256(b).hexdigest()
source=b'package owned\n\nfunc Value() int { return 7 }\n'
expected=[]
for error in ['TimeoutExpired','CalledProcessError','SubprocessError','OSError']:
 expected += [{'id':'fresh-'+error,'cached':False,'fault':error,'expected_delivery':'RETURNED','expected_status':'INCONCLUSIVE'}, {'id':'cached-'+error,'cached':True,'fault':error,'expected_delivery':'RETURNED' if error=='OSError' else 'RAISED','expected_status':'REFUSED' if error=='OSError' else None}]
protocol={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hypothesis':'Current real helper catches subprocess failures during fresh extraction but equivalent failures during cached Go evidence validation can escape request(), while OSError control returns REFUSED. No production code change.','implementation':str((ROOT/'agent/tools/documentation_retrieval.py').relative_to(ROOT)),'implementation_sha256':sha((ROOT/'agent/tools/documentation_retrieval.py').read_bytes()),'source':source.decode(),'source_sha256':sha(source),'cases':expected,'control':'Real native syntax parser creates valid FOUND journal before cached fault injection; intact fresh/duplicate control must pass first.','injection':'Temporarily replace only subprocess.run in this isolated observer process with an owned raising callable, restore in finally. No actual OS resource fault is induced.','scope':'Dynamic real HelperRetrieval/request/journal observation with injected transport exceptions. Not actual timeout, target execution, Linux/Windows behavior, caller job execution, generic accuracy or permanent tests.'}
frozen=json.loads((P/'helper-subprocess-delivery-protocol-v1.json').read_text());assert frozen['implementation_sha256']==protocol['implementation_sha256'];assert frozen['cases']==expected and frozen['source_sha256']==sha(source)
folder=args.output_root.resolve();folder.mkdir(mode=0o700);(folder/'protocol-used.json').write_bytes(helper.canonical(protocol))

def state(path):return {f.name:sha(f.read_bytes()) for f in sorted(path.iterdir()) if f.is_file()}
def prepare(ident):
 root=folder/ident;root.mkdir(mode=0o700);src=root/'source';src.mkdir(mode=0o700);journal=root/'journal';journal.mkdir(mode=0o700);(src/'owned.go').write_bytes(source)
 registry={'owned':{'root':str(src),'revision':'1'*40,'files':{'owned.go':{'sha256':sha(source),'language':'go','selectors':['Value']}}}}
 h=helper.HelperRetrieval(registry,journal);req={'request_id':'observation','source_id':'owned','revision':'1'*40,'path':'owned.go','qualified_symbol':'Value','expected_sha256':sha(source)}
 (root/'request.json').write_bytes(helper.canonical(req));(root/'registry.json').write_bytes(helper.canonical(registry));return root,journal,h,req
records=[];control={};failure=None
try:
 root,journal,h,req=prepare('intact-control');first=h.request(req);second=h.request(req);control={'first':first,'second':second,'matched':first['status']=='FOUND' and second['status']=='DUPLICATE','journal':state(journal)};(root/'first-response.json').write_bytes(helper.canonical(first));(root/'second-response.json').write_bytes(helper.canonical(second));assert control['matched'],control
 for case in expected:
  root,journal,h,req=prepare(case['id']);bootstrap=None
  if case['cached']:
   bootstrap=h.request(req);(root/'bootstrap-response.json').write_bytes(helper.canonical(bootstrap));assert bootstrap['status']=='FOUND',bootstrap
  before=state(journal);calls=[];original=helper.subprocess.run
  def injected(*args,**kwargs):
   calls.append({'command':args[0] if args else kwargs.get('args'),'timeout':kwargs.get('timeout'),'input_sha256':sha(kwargs.get('input',b''))})
   kind=case['fault']
   if kind=='TimeoutExpired':raise subprocess.TimeoutExpired('owned-fault-injection',20)
   if kind=='CalledProcessError':raise subprocess.CalledProcessError(17,'owned-fault-injection',stderr=b'owned injected failure')
   if kind=='SubprocessError':raise subprocess.SubprocessError('owned injected subprocess error')
   raise OSError('owned injected OS error')
  observation={**case,'before_journal':before,'bootstrap_status':bootstrap['status'] if bootstrap else None}
  try:
   helper.subprocess.run=injected
   try:
    returned=h.request(req);observation.update(delivery='RETURNED',status=returned['status'],response=returned)
   except Exception as error:observation.update(delivery='RAISED',status=None,exception_type=type(error).__name__,exception_text=str(error))
  finally:helper.subprocess.run=original
  observation['calls']=calls;observation['after_journal']=state(journal);observation['journal_unchanged']=before==observation['after_journal'];observation['request_lock_released']=not h._request_lock.locked();observation['matched']=observation['delivery']==case['expected_delivery'] and observation['status']==case['expected_status'];assert observation['request_lock_released'];records.append(observation)
  (root/'observation.json').write_bytes(helper.canonical(observation))
except Exception as error:failure={'type':type(error).__name__,'text':str(error)}
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':sha((P/'helper-subprocess-delivery-protocol-v1.json').read_bytes()),'control':control,'records':records,'setup_or_observer_failure':failure,'expected_cases':len(expected),'observed_cases':len(records),'matched':sum(r['matched'] for r in records),'source_executed':False,'native_parser_used_for_owned_syntax_bootstrap':True,'actual_OS_fault_induced':False,'production_modified':False,'new_model_calls':0,'independent_accuracy_metric':None}
with (folder/'delivery-results.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['control','records']}));print(json.dumps([{'id':r['id'],'delivery':r['delivery'],'status':r['status'],'journal_unchanged':r['journal_unchanged'],'matched':r['matched']} for r in records]))

assert failure is None and len(records)==8 and all(r['matched'] for r in records),result
