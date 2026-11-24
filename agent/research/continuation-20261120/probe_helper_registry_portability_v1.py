import copy,datetime,hashlib,importlib.util,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;cut=json.loads((P/'recovery-delta-receipt-v3.json').read_text());root=Path(cut['restored_root']);rp=root/'agent/research/continuation-20261120'
sys.path.insert(0,str(root/'agent/tools'))
import documentation_retrieval as retrieval
assert Path(retrieval.__file__).resolve().is_relative_to(root)
registry=json.loads((rp/'helper-public-registry-v1.json').read_text());journal=rp/'helper-journal-public-v1';request=json.loads((journal/'facade-compile.request.json').read_text())
before={f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in journal.iterdir()if f.is_file()}
old=retrieval.HelperRetrieval(registry,str(journal),max_steps=1,max_quote_bytes=1);original=old.request(request)
assert original['status']=='DUPLICATE'and not Path(registry['jmespath']['root']).is_relative_to(root)
rebased=copy.deepcopy(registry);source=Path(registry['jmespath']['root']);live_root=P.parents[2];relative=source.relative_to(live_root);rebased['jmespath']['root']=str(root/relative)
new=retrieval.HelperRetrieval(rebased,str(journal),max_steps=1,max_quote_bytes=1);relocated=new.request(request)
assert relocated['status']=='REFUSED'and'receipt'in relocated['reason']
after={f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in journal.iterdir()if f.is_file()};assert before==after
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'producer_loaded_from_restored_tree':True,'original_source_root':registry['jmespath']['root'],'relocated_source_root':rebased['jmespath']['root'],'original_registry_sha256':old.registry_sha256,'relocated_registry_sha256':new.registry_sha256,'unrebased_result':original,'rebased_result':relocated,'journal_unchanged':True,'new_retrieval_steps':old.steps+new.steps,'new_quote_bytes_injected':0,'source_executed':False,'model_calls':0,'new_distinct_public_evaluation_cases':0,'interpretation':'Loading restored tool source alone is insufficient proof of relocated-source consumption. Refusal after root rebind preserves the original receipt contract; no in-place migration or automatic budget reset is authorized by this probe.'}
with(P/'helper-registry-portability-host-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'unrebased':original['status'],'unrebased_source_outside_restore':True,'rebased':relocated['status'],'journal_unchanged':True})
