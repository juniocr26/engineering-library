import copy,datetime,hashlib,importlib.util,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;version=int(sys.argv[1]);assert version in [1,2];path=P/('closed_helper_lifecycle_v'+str(version)+'.py');oracle_path=P/'closed-helper-flow-control-oracle-v1.json';oracle=json.loads(oracle_path.read_text());spec=importlib.util.spec_from_file_location('closed_helper_flow_'+str(version),path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);rows=[]
for case in oracle['cases']:
 result=module.decision(copy.deepcopy(case['packet']));rows.append({'id':case['id'],'expected_action':case['expected_action'],'result':result,'matches':result['action']==case['expected_action']and result.get('source_executed')is False})
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'producer':path.name,'producer_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'oracle_sha256':hashlib.sha256(oracle_path.read_bytes()).hexdigest(),'rows':rows,'correct':sum(row['matches']for row in rows),'n':len(rows),'source_executed':False,'model_calls':0,'production_routing_changed':False,'permanent_tests_changed':False}
with(P/('closed-helper-flow-results-v'+str(version)+'.json')).open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'version':version,'correct':r['correct'],'n':len(rows),'misses':[row['id']for row in rows if not row['matches']]})
