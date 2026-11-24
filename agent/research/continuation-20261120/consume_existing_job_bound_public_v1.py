"""Prove existing durable wrapper consumption of current helper, no new coordinator."""
import datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];OUT=P/'helper-job-bound-public-v1';OUT.mkdir();(OUT/'cache').mkdir();(OUT/'job').mkdir()
registry=json.loads((P/'helper-public-registry-v1.json').read_text());canonical=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode();config={'job_id':'jmespath-current-helper-public-v1','registry_sha256':hashlib.sha256(canonical(registry)).hexdigest(),'max_steps':4,'max_quote_bytes':24576,'deadline_utc':(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(minutes=10)).isoformat()}
plans=[('facade-compile','jmespath/__init__.py','compile'),('facade-search','jmespath/__init__.py','search'),('parser-cache','jmespath/parser.py','Parser.parse'),('parser-errors','jmespath/parser.py','Parser._do_parse'),('outside-total-budget','jmespath/parser.py','ParsedResult.search')];entry=registry['jmespath'];requests=[{'request_id':key,'source_id':'jmespath','revision':entry['revision'],'path':path,'qualified_symbol':selector,'expected_sha256':entry['files'][path]['sha256']}for key,path,selector in plans]
protocol={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'registry':registry,'config':config,'requests':requests,'expected_first_process':'oneCOMPLETED/FOUND,rawhelpersteps1','expected_resumed_process':'DUPLICATE_COMPLETEDwithoutdispatch;threeCOMPLETED/FOUND;fifthBUDGET_EXHAUSTEDbeforedispatch','current_helper_version':'0.1.4','existing_budget_version':'0.1.0','new_distinct_source_cases':0,'source_executed':False,'model_calls':0,'not_a_new_capability':'Use unmodified existing HelperJobBudget/JobBoundRetrieval; do not integrate research legacyjournal audit.'}
with(OUT/'protocol.json').open('x')as f:f.write(json.dumps(protocol,indent=2)+'\n')
worker=r'''
import datetime,hashlib,json,pathlib,sys
sys.dont_write_bytecode=True
root=pathlib.Path(sys.argv[1]);out=pathlib.Path(sys.argv[2]);phase=sys.argv[3];sys.path.insert(0,str(root/'agent/tools'))
from documentation_retrieval import HelperRetrieval,VERSION
from documentation_job_budget import HelperJobBudget,JobBoundRetrieval
assert VERSION=='0.1.4';protocol=json.loads((out/'protocol.json').read_text());helper=HelperRetrieval(protocol['registry'],str(out/'cache'),max_steps=4,max_quote_bytes=24576);job=HelperJobBudget(str(out/'job'),protocol['config']);wrapper=JobBoundRetrieval(helper,job);rows=[]
indices=[0]if phase=='first'else[0,1,2,3,4]
for index in indices:
 before=helper.steps;result=wrapper.request(protocol['requests'][index]);expected='DUPLICATE_COMPLETED'if phase=='resume'and index==0 else'BUDGET_EXHAUSTED'if index==4 else'COMPLETED';assert result['status']==expected,result
 if expected=='COMPLETED':assert result['helper_result']['status']=='FOUND'
 else:assert helper.steps==before and'helper_result'not in result
 rows.append({'request_id':protocol['requests'][index]['request_id'],'result':result,'raw_helper_steps_before':before,'raw_helper_steps_after':helper.steps})
print(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase':phase,'rows':rows,'raw_helper_steps':helper.steps,'raw_helper_quote_bytes':helper.quote_bytes,'source_executed':False,'owner_approved':False}))
'''
results=[]
for phase in ['first','resume']:
 r=subprocess.run([sys.executable,'-c',worker,str(ROOT),str(OUT),phase],capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',GIT_OPTIONAL_LOCKS='0'),timeout=30);(OUT/(phase+'.stdout')).write_text(r.stdout);(OUT/(phase+'.stderr')).write_text(r.stderr);assert r.returncode==0,r.stderr;result=json.loads(r.stdout);results.append(result)
assert results[0]['raw_helper_steps']==1 and results[1]['raw_helper_steps']==3 and sum(r['raw_helper_quote_bytes']for r in results)==1603
reservations=sorted((OUT/'job').glob('step-*-reserved.json'));completions=sorted((OUT/'job').glob('step-*-completed.json'));assert len(reservations)==len(completions)==4 and not(OUT/'cache/outside-total-budget.request.json').exists()
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':results,'existing_budget_version':'0.1.0','current_helper_version':'0.1.4','durable_reservations':4,'durable_completions':4,'conservative_quote_reservation_bytes':4*6144,'actual_found_quote_bytes':1603,'same_first_request_not_redispatched_after_process_restart':True,'fifth_request_not_dispatched':True,'new_coordinator_implemented':False,'new_distinct_source_cases':0,'new_model_calls':0,'source_executed':False,'owner_approved':False,'training_gold':False,'scope':'Two fresh processes consume the real existing optional job wrapper and current helper against four already-exposed publicsource selectors; no automatic Ruby/model routing or novel globalbudget claim.'}
with(P/'existing-job-bound-public-consumption-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'first_helper_steps':1,'resumed_helper_steps':3,'durable_steps':4,'actual_quote_bytes':1603,'duplicate_not_dispatched':True,'fifth_not_dispatched':True,'new_capability_claimed':False})
