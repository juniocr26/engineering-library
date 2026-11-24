"""Retain previous six cases and compare the original six claim values exactly."""
import datetime,hashlib,importlib.util,json
from pathlib import Path
P=Path(__file__).resolve().parent;OLD=P.parent/'documentation-intelligence-20261120'
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
observer=load(P/'architecture_fact_observer_v3.py','new_observer');compiler=load(P/'architecture_claim_compiler_v3.py','new_compiler');old=load(OLD/'prepare_architecture_claims_v2.py','previous_compiler')
base={n:(observer.SOURCE/n).read_bytes()for n in observer.FILES};oracle=json.loads((OLD/'architecture-counterexample-oracle-v1.json').read_text());rows=[]
for case in oracle['definitions']:
 sources=dict(base)
 if case['file']:
  before=case['old'].encode();after=case['new'].encode();assert sources[case['file']].count(before)==1;sources[case['file']]=sources[case['file']].replace(before,after)
 try:compiler.derive(observer.extract(sources));actual='DERIVED';reason=None
 except (ValueError,KeyError)as error:actual='REFUSED';reason=str(error)
 rows.append({'id':case['id'],'expected':case['expected'],'actual':actual,'matches':actual==case['expected'],'reason':reason})
new=compiler.derive(observer.extract(base));previous=old.derive(observer.previous.extract(base))
assert new['claims']==previous['claims'] and new['evidence']==previous['evidence']
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':rows,'correct':sum(r['matches']for r in rows),'n':len(rows),'original_six_claim_values_and_evidence_unchanged':True,'source_executed':False,'model_calls':0,'production_files_modified':False}
with(P/'architecture-previous-controls-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
