import datetime,json,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent
program=r'''
import copy,hashlib,json,pathlib,sys
sys.dont_write_bytecode=True
root=pathlib.Path('/tmp/el-continuation-20261120-linux-restore-v3');p=root/'agent/research/continuation-20261120';sys.path.insert(0,str(root/'agent/tools'));import documentation_retrieval as helper
assert pathlib.Path(helper.__file__).resolve().is_relative_to(root)and helper.VERSION=='0.1.3'
registry=json.loads((p/'helper-public-registry-v1.json').read_text());journal=p/'helper-journal-public-v1';request=json.loads((journal/'facade-compile.request.json').read_text());before={f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in journal.iterdir()if f.is_file()}
try:helper.HelperRetrieval(registry,str(journal),max_steps=1,max_quote_bytes=1)
except OSError as error:original={'status':'CONSTRUCTION_REFUSED','reason':str(error)}
else:raise AssertionError('original macOSroot unexpectedly available')
rebased=copy.deepcopy(registry);suffix='/agent/research/continuation-20261120/new-public-sources-v1/';old=registry['jmespath']['root'];assert suffix in old;rebased['jmespath']['root']=str(root/'agent/research/continuation-20261120/new-public-sources-v1')+'/'+old.split(suffix,1)[1]
result=helper.HelperRetrieval(rebased,str(journal),max_steps=1,max_quote_bytes=1).request(request);assert result['status']=='REFUSED'and'receipt'in result['reason']
after={f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in journal.iterdir()if f.is_file()};assert before==after
print(json.dumps({'original_registry_result':original,'rebased_registry_result':result,'tool_version':helper.VERSION,'tool_loaded_from_restore':True,'journal_unchanged':True,'source_executed':False,'source_root':rebased['jmespath']['root'],'model_calls':0,'new_distinct_public_evaluation_cases':0}))
'''
r=subprocess.run(['docker','exec','engineering-library-backend-1','python3','-c',program],capture_output=True,text=True,timeout=30)
(P/'helper-registry-portability-linux-v1.stdout').write_text(r.stdout);(P/'helper-registry-portability-linux-v1.stderr').write_text(r.stderr)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':r.returncode}
if r.returncode==0:record.update(json.loads(r.stdout))
with(P/'helper-registry-portability-linux-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
assert r.returncode==0,r.stderr;print({'original':record['original_registry_result']['status'],'rebased':record['rebased_registry_result']['status'],'unchanged':record['journal_unchanged']})
