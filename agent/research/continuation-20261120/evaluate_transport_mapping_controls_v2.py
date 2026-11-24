"""Frozen map/hierarchy controls; no inspected source is imported or executed."""
import datetime,hashlib,importlib.util,json
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('mapping_controls',P/'transport_mapping_observer_v2.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
protocol=json.loads((P/'transport-mapping-control-oracle-v1.json').read_text());rows=[]
for case in protocol['rows']:
 registry={name:{'source':source,'sha256':hashlib.sha256(source.encode()).hexdigest(),'revision':'owned-sha256:'+hashlib.sha256(source.encode()).hexdigest()}for name,source in case['sources'].items()}
 result=m.observe(registry);rows.append({'id':case['id'],'expected':case['expected'],'actual':result['status'],'matches':case['expected']==result['status'],'result':result})
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':rows,'correct':sum(r['matches']for r in rows),'n':len(rows),'source_executed':False,'model_calls':0,'production_changes':False,'producer_sha256':hashlib.sha256((P/'transport_mapping_observer_v2.py').read_bytes()).hexdigest()}
with(P/'transport-mapping-control-results-v2.json').open('x')as stream:stream.write(json.dumps(record,indent=2)+'\n')
print(json.dumps({'correct':record['correct'],'n':record['n'],'failures':[{'id':r['id'],'actual':r['actual'],'reason':r['result'].get('reason')}for r in rows if not r['matches']]}))
