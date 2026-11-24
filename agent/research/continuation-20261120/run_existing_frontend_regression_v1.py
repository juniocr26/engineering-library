"""Fresh existing frontend baseline; verify container source bytes before testing."""
import datetime,hashlib,json,os,subprocess,time
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];baseline=json.loads((P/'baseline.json').read_text());files=[]
for name,entry in baseline['tracked_identity'].items():
 path=Path(name)
 if name.startswith('frontend/')and path.suffix in ['.ts','.tsx','.js','.mjs','.cjs','.json','.css']:
  raw=(ROOT/path).read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['sha256'];files.append({'path':str(path.relative_to('frontend')),'sha256':entry['sha256']})
program="""const fs=require('node:fs'),crypto=require('node:crypto');const rows=JSON.parse(fs.readFileSync(0,'utf8')).map(e=>{const p='/app/frontend/'+e.path;let hash=null;try{hash=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex')}catch{}return {...e,observed_sha256:hash,matches:hash===e.sha256}});process.stdout.write(JSON.stringify({node:process.version,rows,all_match:rows.every(e=>e.matches)}));"""
pre=subprocess.run(['docker','exec','-i','engineering-library-frontend-1','node','-e',program],input=json.dumps(files).encode(),capture_output=True,timeout=20);assert pre.returncode==0,pre.stderr.decode();preflight=json.loads(pre.stdout)
with(P/'frontend-source-identity-before-regression-v1.json').open('x')as f:f.write(json.dumps(preflight,indent=2)+'\n')
assert preflight['all_match'],'container source identity differs; do not run or claim current baseline'
tests=sorted('tests/'+path.name for path in (ROOT/'frontend/tests').glob('*.test.ts'));command=['docker','exec','-w','/app/frontend','engineering-library-frontend-1','node','--experimental-strip-types','--test',*tests]
start=time.monotonic();result=subprocess.run(command,capture_output=True,text=True,timeout=120);(P/'frontend-regression-v1.stdout').write_text(result.stdout);(P/'frontend-regression-v1.stderr').write_text(result.stderr)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':command,'exit_code':result.returncode,'wall_seconds':time.monotonic()-start,'source_identity_files':len(files),'all_container_source_hashes_match_baseline':True,'test_files':len(tests),'permanent_tests_modified':False,'new_permanent_tests':0,'browser_or_server_started':False,'model_calls':0}
with(P/'frontend-regression-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print(record);print(result.stdout[-700:]);raise SystemExit(result.returncode)
