import datetime,hashlib,json,subprocess,time
from pathlib import Path
P=Path(__file__).resolve().parent
protocol_path=P/'javascript-queue-confined-protocol-v1.json';protocol=json.loads(protocol_path.read_text());sources={}
for name,expected in protocol['source_files'].items():
 raw=(P/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
 if name.endswith('/index.js'):sources[name]=raw.decode()
start=time.monotonic()
r=subprocess.run(['docker','exec','-i','engineering-library-frontend-1','node','--experimental-vm-modules','/sources/engineering-library/agent/research/continuation-20261120/observe_javascript_queue_confined_v1.cjs'],input=json.dumps({'protocol':protocol,'sources':sources}).encode(),capture_output=True,timeout=20)
(P/'javascript-queue-confined-linux-v1.stdout').write_bytes(r.stdout);(P/'javascript-queue-confined-linux-v1.stderr').write_bytes(r.stderr)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':r.returncode,'wall_seconds':time.monotonic()-start,'protocol_sha256':hashlib.sha256(protocol_path.read_bytes()).hexdigest(),'source_execution_explicitly_scoped':True,'owner_approved':False,'training_excluded':True}
if r.returncode==0:record['observation']=json.loads(r.stdout)
with(P/'javascript-queue-confined-linux-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
assert r.returncode==0,r.stderr.decode()
print({'cases':len(record['observation']['rows']),'all_pass':record['observation']['allPass'],'failed':[row['id']for row in record['observation']['rows']if not row['allPass']],'wall_seconds':record['wall_seconds']})
