"""Evaluate the frozen complete-statement profile, without source execution."""
import datetime,hashlib,importlib.util,json
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('prefix_controls_observer',P/'keyword_prefix_observer_v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
protocol=json.loads((P/'keyword-prefix-control-oracle-v1.json').read_text());rows=[]
for case in protocol['rows']:
 source=case['source'];digest=hashlib.sha256(source.encode()).hexdigest();result=m.observe({'path':'owned_prefix.py','revision':'owned-sha256:'+digest,'source':source,'sha256':digest},'remap','trace')
 actual=('RECOGNIZED'if result['keyword_recognized_by_direct_pop']else'NOT_RECOGNIZED')if result['status']=='WRITTEN_KEYWORD_PREFIX_FACTS'else'INCONCLUSIVE'
 rows.append({'id':case['id'],'expected':case['expected'],'actual':actual,'matches':actual==case['expected'],'result':result})
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':rows,'correct':sum(r['matches']for r in rows),'n':len(rows),'source_executed':False,'model_calls':0,'permanent_tests_changed':False,'producer_sha256':hashlib.sha256((P/'keyword_prefix_observer_v1.py').read_bytes()).hexdigest()}
with(P/'keyword-prefix-control-results-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print(json.dumps({'correct':record['correct'],'n':record['n'],'failures':[{'id':r['id'],'actual':r['actual'],'reason':r['result'].get('reason')}for r in rows if not r['matches']]}))
