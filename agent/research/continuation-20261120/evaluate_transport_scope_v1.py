"""Evaluate only frozen local/import binding metadata; inspected code never runs."""
import argparse,datetime,hashlib,importlib.util,json
from pathlib import Path
P=Path(__file__).resolve().parent
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('version',choices=['1','2']);args=parser.parse_args()
 path=P/('transport_mapping_observer_v'+args.version+'.py');spec=importlib.util.spec_from_file_location('scope_map_profile',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 cases=json.loads((P/'transport-scope-control-oracle-v1.json').read_text())['rows'];rows=[]
 for case in cases:
  registry={name:{'source':source,'sha256':hashlib.sha256(source.encode()).hexdigest(),'revision':'owned-sha256:'+hashlib.sha256(source.encode()).hexdigest()}for name,source in case['sources'].items()}
  result=m.observe(registry);rows.append({'id':case['id'],'expected':case['expected'],'actual':result['status'],'matches':case['expected']==result['status'],'result':result})
 record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'version':args.version,'rows':rows,'correct':sum(r['matches']for r in rows),'n':len(rows),'source_executed':False,'model_calls':0,'production_component_changed':False,'producer_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 with(P/('transport-scope-results-v'+args.version+'.json')).open('x')as stream:stream.write(json.dumps(record,indent=2)+'\n')
 print(json.dumps({'correct':record['correct'],'n':record['n'],'failures':[r['id']for r in rows if not r['matches']]}))
