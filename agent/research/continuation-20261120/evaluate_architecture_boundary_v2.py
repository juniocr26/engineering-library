"""Evaluate frozen source mutations without executing the inspected source."""
import argparse,datetime,hashlib,importlib.util,json
from pathlib import Path
P=Path(__file__).resolve().parent;OLD=P.parent/'documentation-intelligence-20261120'
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['baseline','candidate']);args=parser.parse_args()
 observer=load(OLD/'assemble_architecture_facts_v2.py'if args.phase=='baseline'else P/'architecture_fact_observer_v3.py','observer')
 compiler=load(OLD/'prepare_architecture_claims_v2.py'if args.phase=='baseline'else P/'architecture_claim_compiler_v3.py','compiler')
 oracle=json.loads((P/'architecture-boundary-oracle-v1.json').read_text());rows=[]
 for case in oracle['rows']:
  sources={n:t.encode()for n,t in case['sources'].items()}
  assert all(hashlib.sha256(b).hexdigest()==case['source_sha256'][n]for n,b in sources.items())
  try:
   result=compiler.derive(observer.extract(sources));status='DERIVED';detail={'claims':result['claims']}
  except (ValueError,KeyError)as error:status='REFUSED';detail={'reason':str(error)}
  rows.append({'id':case['id'],'expected':case['expected'],'actual':status,'matches':status==case['expected'],**detail})
 result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase':args.phase,'correct':sum(r['matches']for r in rows),'n':len(rows),'rows':rows,'source_files_written':0,'inspected_source_executed':False,'model_calls':0,'compiler_sha256':hashlib.sha256(Path(compiler.__file__).read_bytes()).hexdigest(),'observer_sha256':hashlib.sha256(Path(observer.__file__).read_bytes()).hexdigest()}
 with(P/('architecture-boundary-'+args.phase+'-v1.json')).open('x')as f:f.write(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'correct':result['correct'],'n':result['n'],'misses':[r['id']for r in rows if not r['matches']]}))
