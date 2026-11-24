"""Verify previous/new source controls once after the scope repair."""
import datetime,hashlib,importlib.util,json
from pathlib import Path
P=Path(__file__).resolve().parent;OLD=P.parent/'documentation-intelligence-20261120'
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
obs=load(P/'architecture_fact_observer_v3.py','reg_obs');compiler=load(P/'architecture_claim_compiler_v4.py','reg_compiler');base={n:(obs.SOURCE/n).read_bytes()for n in obs.FILES};rows=[];input_sets=[]
for case in json.loads((OLD/'architecture-counterexample-oracle-v1.json').read_text())['definitions']:
 sources=dict(base)
 if case['file']:
  before=case['old'].encode();assert sources[case['file']].count(before)==1;sources[case['file']]=sources[case['file']].replace(before,case['new'].encode())
 input_sets.append({'id':'prior:'+case['id'],'expected':case['expected'],'sources':sources})
for case in json.loads((P/'architecture-boundary-oracle-v1.json').read_text())['rows']:input_sets.append({'id':'boundary:'+case['id'],'expected':case['expected'],'sources':{n:t.encode()for n,t in case['sources'].items()}})
def identity(sources):return hashlib.sha256(json.dumps({n:hashlib.sha256(b).hexdigest()for n,b in sources.items()},sort_keys=True,separators=(',',':')).encode()).hexdigest()
for case in input_sets:
 try:compiler.derive(obs.extract(case['sources']));actual='DERIVED';reason=None
 except (ValueError,KeyError)as error:actual='REFUSED';reason=str(error)
 assert actual==case['expected'],case['id'];rows.append({'id':case['id'],'expected':case['expected'],'actual':actual,'matches':True,'reason':reason,'complete_source_set_sha256':identity(case['sources'])})
scope=json.loads((P/'architecture-scope-results-v4.json').read_text());scope_oracle=json.loads((P/'architecture-scope-oracle-v1.json').read_text());assert scope['correct']==scope['n']==8
scope_identities=[identity({n:t.encode()for n,t in case['sources'].items()})for case in scope_oracle['rows']]
old=load(OLD/'prepare_architecture_claims_v2.py','reg_previous');a=compiler.derive(obs.extract(base));b=old.derive(obs.previous.extract(base));assert a['claims']==b['claims']and a['evidence']==b['evidence']
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'current_compiler':'architecture_claim_compiler_v4.py','current_compiler_sha256':hashlib.sha256((P/'architecture_claim_compiler_v4.py').read_bytes()).hexdigest(),'regression_rows':rows,'regression_observations_passed':len(rows),'prior_scope_receipt':'architecture-scope-results-v4.json','scope_observations_passed':8,'combined_observations':len(rows)+8,'distinct_complete_source_sets':len(set([r['complete_source_set_sha256']for r in rows]+scope_identities)),'original_six_claims_and_evidence_exactly_preserved':True,'source_executed':False,'model_calls':0,'permanent_tests_changed':False,'production_component_changed':False,'general_architecture_semantics_proven':False}
with(P/'architecture-v4-regressions-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items()if k!='regression_rows'}))
