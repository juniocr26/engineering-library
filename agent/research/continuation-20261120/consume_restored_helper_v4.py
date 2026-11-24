"""Use the sealed current helper implementation, never import the live helper."""
import datetime,hashlib,json,os,subprocess,sys,time
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];receipt_path=P/'recovery-delta-receipt-v4.json';receipt=json.loads(receipt_path.read_text());restored=Path(receipt['restored_root'])
worker=r'''
import copy,hashlib,json,pathlib,sys
sys.dont_write_bytecode=True
root=pathlib.Path(sys.argv[1]);original=pathlib.Path(sys.argv[2]);p=root/'agent/research/continuation-20261120';sys.path.insert(0,str(root/'agent/tools'))
import documentation_retrieval as helper
import documentation_workspace as workspace
assert helper.VERSION=='0.1.4'
for module in [helper,workspace]:assert pathlib.Path(module.__file__).resolve().is_relative_to(root),module.__file__
owned=pathlib.Path('/private/tmp/el-current-helper-consumption-v4-20261120');owned.mkdir(exist_ok=False);(owned/'public-cache').mkdir()
registry=json.loads((p/'helper-public-registry-v1.json').read_text())
for entry in registry.values():entry['root']=str(root/pathlib.Path(entry['root']).relative_to(original))
request=json.loads((p/'helper-journal-public-v1/facade-compile.request.json').read_text());public=helper.HelperRetrieval(registry,str(owned/'public-cache'),max_steps=1,max_quote_bytes=6144).request(request);assert public['status']=='FOUND'
old=json.loads((p/'helper-journal-public-v1/facade-compile.result.json').read_text());assert public['evidence']['quote_sha256']==old['evidence']['quote_sha256']
# Repeat one existing adversarial case to exercise the restored current lexical guard.
case=next(row for row in json.loads((p/'helper-cached-lexical-unit-oracle-v1.json').read_text())['cases']if row['id']=='another-physical-callable');source=owned/'synthetic-source';cache=owned/'synthetic-cache';source.mkdir();cache.mkdir();raw=case['source'].encode();assert hashlib.sha256(raw).hexdigest()==case['source_sha256'];(source/'owned.py').write_bytes(raw)
reg={'owned':{'root':str(source),'revision':'a'*40,'files':{'owned.py':{'sha256':case['source_sha256'],'language':'python','selectors':['selected','other']}}}};req={'request_id':'selected-callable','source_id':'owned','revision':'a'*40,'path':'owned.py','qualified_symbol':'selected','expected_sha256':case['source_sha256']};instance=helper.HelperRetrieval(reg,str(cache));first=instance.request(req);assert first['status']=='FOUND'
result=copy.deepcopy(first);result['evidence']=helper.python_unit(case['source'],'other');result['evidence']['selector']='selected';result['quote_bytes']=len(result['evidence']['quote'].encode());result['cumulative_quote_bytes']=result['quote_bytes'];encoded=helper.canonical(result);(cache/'selected-callable.result.json').write_bytes(encoded);(cache/'selected-callable.receipt.json').write_bytes(helper.canonical(helper.receipt_for(encoded,helper.canonical(req),instance.registry_sha256,case['source_sha256'],result['extractor_identity'])))
refused=helper.HelperRetrieval(reg,str(cache)).request(req);assert refused['status']=='REFUSED'and'complete selected lexical callable'in refused['reason'];assert hashlib.sha256((source/'owned.py').read_bytes()).hexdigest()==case['source_sha256']
print(json.dumps({'status':'VERIFIED_RESTORED_CURRENT_HELPER_CONSUMPTION','helper_version':helper.VERSION,'loaded_source_root':str(root),'helper_sha256':hashlib.sha256(pathlib.Path(helper.__file__).read_bytes()).hexdigest(),'workspace_sha256':hashlib.sha256(pathlib.Path(workspace.__file__).read_bytes()).hexdigest(),'public_quote_result':public,'coordinated_other_callable_refusal':refused,'source_executed':False,'new_distinct_source_cases':0,'model_calls':0,'published_files_written':False,'legacy_journal_migrated':False,'owned_control_root':str(owned)}))
'''
start=time.monotonic();r=subprocess.run([sys.executable,'-c',worker,str(restored),str(ROOT)],capture_output=True,text=True,cwd=restored,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',GIT_OPTIONAL_LOCKS='0'),timeout=60);(P/'restored-helper-consumption-v4.stdout').write_text(r.stdout);(P/'restored-helper-consumption-v4.stderr').write_text(r.stderr);record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':r.returncode,'wall_seconds':time.monotonic()-start,'source_cut_receipt_sha256':hashlib.sha256(receipt_path.read_bytes()).hexdigest()}
if r.returncode==0:
 record.update(json.loads(r.stdout));manifest=json.loads((ROOT/receipt['input_manifest']['path']).read_text())
 for name,expected in manifest['effective_expected_files'].items():assert hashlib.sha256((restored/name).read_bytes()).hexdigest()==expected['sha256'],name
 record['all_20849_expected_input_hashes_unchanged']=True
with(P/'restored-helper-consumption-v4.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
assert r.returncode==0,r.stderr;print({k:v for k,v in record.items()if k not in ['public_quote_result','coordinated_other_callable_refusal']})
