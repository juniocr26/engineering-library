"""Preserve one chosen baseline/candidate renderer observation, never source execution."""
import argparse,datetime,json,subprocess,time
from pathlib import Path
P=Path(__file__).resolve().parent
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('phase');parser.add_argument('--protocol',default='returned-map-renderer-protocol-v1.json');args=parser.parse_args()
 protocol=json.loads((P/args.protocol).read_text());start=time.monotonic()
 process=subprocess.run(['docker','exec','-i','-e','RAILS_ENV=test','-e','DATABASE_URL=sqlite3::memory:','-w','/app/backend','engineering-library-backend-1','bundle','exec','ruby','/sources/engineering-library/agent/research/continuation-20261120/probe_returned_map_renderer_v1.rb'],input=json.dumps(protocol),text=True,capture_output=True,timeout=180)
 prefix='returned-map-renderer-'+args.phase
 (P/(prefix+'.stdout')).write_text(process.stdout);(P/(prefix+'.stderr')).write_text(process.stderr)
 record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':process.returncode,'wall_seconds':time.monotonic()-start,'protocol':args.protocol}
 if process.returncode==0:
  record.update(json.loads(process.stdout));record['matches']=sum(r['status']==case['expected_status']for r,case in zip(record['rows'],protocol['cases'],strict=True));record['n']=len(protocol['cases'])
 with(P/(prefix+'.json')).open('x')as f:f.write(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in record.items()if k!='rows'}));raise SystemExit(process.returncode)
