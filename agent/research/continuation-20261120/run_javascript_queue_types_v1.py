import datetime,hashlib,json,subprocess,time
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];oracle_path=P/'javascript-queue-type-consumer-oracle-v1.json';oracle=json.loads(oracle_path.read_text());files=[]
for entry in oracle['declaration_and_manifest_sources']:
 file=P/entry['path'];raw=file.read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['sha256'];files.append({'path':'/sources/engineering-library/'+str(file.relative_to(ROOT)),'sha256':entry['sha256']})
start=time.monotonic();r=subprocess.run(['docker','exec','-i','-e','NODE_PATH=/app/frontend/node_modules','-w','/app/frontend','engineering-library-frontend-1','node','/sources/engineering-library/agent/research/continuation-20261120/check_javascript_queue_types_v1.cjs'],input=json.dumps({'oracle':oracle,'files':files}).encode(),capture_output=True,timeout=90)
(P/'javascript-queue-type-consumers-v1.stdout').write_bytes(r.stdout);(P/'javascript-queue-type-consumers-v1.stderr').write_bytes(r.stderr);record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':r.returncode,'wall_seconds':time.monotonic()-start,'oracle_sha256':hashlib.sha256(oracle_path.read_bytes()).hexdigest()}
if r.returncode==0:record.update(json.loads(r.stdout))
with(P/'javascript-queue-type-consumers-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
assert r.returncode==0,r.stderr.decode();print({'correct':record['correct'],'n':record['n'],'failed':[row['id']for row in record['rows']if not row['matches']],'standard_library_files':len(record['standard_library_files']),'source_executed':False})
