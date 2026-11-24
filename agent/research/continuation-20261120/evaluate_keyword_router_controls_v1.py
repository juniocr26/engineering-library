"""Exercise the new router and unchanged previous declaration controls once."""
import datetime,hashlib,importlib.util,json
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('router_controls',P/'closed_keyword_lifecycle_v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
old=json.loads((P/'closed-declaration-control-oracle-v1.json').read_text())['cases'];positive=json.loads((P/'positive-parameter-control-oracle-v1.json').read_text())['new_cases'];protocol=json.loads((P/'keyword-router-control-oracle-v1.json').read_text());cases=[('prior-declaration',r)for r in old]+[('prior-positive',r)for r in positive]+[('new-keyword',r)for r in protocol['new_cases']];rows=[]
for group,case in cases:
 result=m.decision(case['packet']);rows.append({'group':group,'id':case['id'],'expected':case['expected'],'actual':result['action'],'matches':result['action']==case['expected'],'result':result})
assert Path(protocol['noexec_marker']).exists()==protocol['marker_present_before']
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':rows,'correct':sum(r['matches']for r in rows),'n':len(rows),'new_cases':len(protocol['new_cases']),'prior_cases_reused':len(old)+len(positive),'noexec_marker_unchanged':True,'source_executed':False,'permanent_tests_changed':False,'core_planner_changed':False,'training_excluded':True,'model_calls':0,'producer_sha256':hashlib.sha256((P/'closed_keyword_lifecycle_v1.py').read_bytes()).hexdigest()}
with(P/'keyword-router-control-results-v1.json').open('x')as f:f.write(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'correct':record['correct'],'n':record['n'],'new_cases':record['new_cases'],'prior_reused':record['prior_cases_reused'],'failures':[{'id':r['id'],'actual':r['actual'],'reason':r['result'].get('reason')}for r in rows if not r['matches']]}))
