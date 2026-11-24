"""Run only frozen scope mutations through research extract/derive functions."""
import argparse,datetime,hashlib,importlib.util,json
from pathlib import Path
P=Path(__file__).resolve().parent
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,P/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('version',choices=['3','4']);args=parser.parse_args()
 observer=load('scope_obs','architecture_fact_observer_v3.py');compiler=load('scope_compiler','architecture_claim_compiler_v'+args.version+'.py');oracle=json.loads((P/'architecture-scope-oracle-v1.json').read_text());rows=[]
 for case in oracle['rows']:
  sources={n:t.encode()for n,t in case['sources'].items()};assert all(hashlib.sha256(b).hexdigest()==case['sha256'][n]for n,b in sources.items())
  try:compiler.derive(observer.extract(sources));actual='DERIVED';reason=None
  except (ValueError,KeyError)as error:actual='REFUSED';reason=str(error)
  rows.append({'id':case['id'],'expected':case['expected'],'actual':actual,'matches':actual==case['expected'],'reason':reason})
 record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'version':args.version,'rows':rows,'correct':sum(r['matches']for r in rows),'n':len(rows),'compiler_sha256':hashlib.sha256(Path(compiler.__file__).read_bytes()).hexdigest(),'source_executed':False,'production_changes':False,'model_calls':0}
 with(P/('architecture-scope-results-v'+args.version+'.json')).open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
 print(json.dumps(record))
