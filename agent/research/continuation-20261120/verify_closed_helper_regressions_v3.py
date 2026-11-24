import copy,datetime,hashlib,importlib.util,json
from pathlib import Path
P=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('closed_helper_prior_regressions',P/'closed_helper_lifecycle_v3.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);cases=[];inputs={}
for name,key in [('keyword-router-control-oracle-v1.json','new_cases'),('closed-declaration-control-oracle-v1.json','cases'),('positive-parameter-control-oracle-v1.json','new_cases')]:
 path=P/name;inputs[name]=hashlib.sha256(path.read_bytes()).hexdigest();data=json.loads(path.read_text())
 for case in data[key]:cases.append((name,case))
rows=[]
for origin,case in cases:
 result=module.decision(copy.deepcopy(case['packet']));expected=case.get('expected',case.get('expected_action'));rows.append({'origin':origin,'id':case['id'],'expected':expected,'action':result['action'],'matches':result['action']==expected and result.get('source_executed')is False,'reason':result.get('reason'),'fallback_used':result.get('helper_admission_fallback',False)})
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputs':inputs,'rows':rows,'correct':sum(r['matches']for r in rows),'n':len(rows),'new_distinct_cases':0,'source_executed':False,'model_calls':0,'permanent_tests_changed':False,'production_routing_changed':False}
with(P/'closed-helper-prior-regressions-v3.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'correct':record['correct'],'n':len(rows),'new_distinct_cases':0,'misses':[r['id']for r in rows if not r['matches']]})
