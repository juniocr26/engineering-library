import copy,datetime,hashlib,importlib.util,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent
oracle_path=P/'closed-helper-control-oracle-v1.json';oracle=json.loads(oracle_path.read_text());phase=sys.argv[1];assert phase in ['baseline','candidate'];filename='closed_keyword_lifecycle_v1.py'if phase=='baseline'else'closed_helper_lifecycle_v1.py';spec=importlib.util.spec_from_file_location('measured_closed_helper_'+phase,P/filename);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
rows=[]
for case in oracle['cases']:
 packet=copy.deepcopy(case['packet']);before=json.dumps(packet,sort_keys=True,ensure_ascii=False);result=module.decision(packet);unchanged=json.dumps(packet,sort_keys=True,ensure_ascii=False)==before;rows.append({'id':case['id'],'expected_action':case['expected_action'],'result':result,'input_unchanged':unchanged,'matches':result['action']==case['expected_action']and unchanged and result.get('source_executed')is False and result.get('owner_approved')is False})
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase':phase,'producer':filename,'producer_sha256':hashlib.sha256((P/filename).read_bytes()).hexdigest(),'oracle_sha256':hashlib.sha256(oracle_path.read_bytes()).hexdigest(),'rows':rows,'correct':sum(row['matches']for row in rows),'n':len(rows),'classification':'OWNED_CLOSED_GRAMMAR_AND_ADMISSION_CONTROLS_NOT_GENERAL_PROSE_OR_NEURAL_HOLDOUT','permanent_tests_changed':False,'source_executed':False,'model_calls':0,'production_routing_changed':False}
with(P/('closed-helper-controls-'+phase+'-v1.json')).open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'phase':phase,'correct':record['correct'],'n':len(rows),'misses':[(r['id'],r['result']['action'],r['result'].get('reason'))for r in rows if not r['matches']]})
