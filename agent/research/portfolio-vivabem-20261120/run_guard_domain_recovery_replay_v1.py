from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,sys,time
p=Path(__file__).parent
mode=sys.argv[1]
assert mode in ['host','linux']
freeze=json.loads((p/'guard-domain-replay-input-freeze-v1.json').read_text())
root=Path(freeze['restored_root'])
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(Path(freeze['bundle']).read_bytes())==freeze['bundle_sha256']
assert sha((root/'manifest.json').read_bytes())==freeze['manifest_sha256']
manifest=json.loads((root/'manifest.json').read_text())
for row in manifest['files']:assert sha((root/row['path']).read_bytes())==row['sha256']
driver=(root/'replay_driver.py').read_text();assert sha(driver.encode())==freeze['driver_sha256']
payload=(root/'payload.json').read_bytes()
reference=json.loads((root/'reference-projection.json').read_text())
reference_bytes=json.dumps(reference,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
assert sha(reference_bytes)==freeze['reference_canonical_fingerprint']
folder=p/'guard-domain-recovery-replay-v1'/mode
folder.mkdir(parents=True,exist_ok=False)
if mode=='host':command=[sys.executable,'-I','-S','-B',str(root/'replay_driver.py')]
else:command=['docker','exec','-i','engineering-library-backend-1','python3','-I','-S','-B','-c',driver]
start=datetime.now(timezone.utc);wall=time.monotonic()
r=subprocess.run(command,input=payload,capture_output=True,timeout=30)
(folder/'stdout.json').write_bytes(r.stdout);(folder/'stderr.txt').write_bytes(r.stderr)
outcome={'at':datetime.now(timezone.utc).isoformat(),'started_at':start.isoformat(),'mode':mode,'returncode':r.returncode,'wall_seconds':time.monotonic()-wall,'source_bundle_sha256':freeze['bundle_sha256'],'payload_sha256':sha(payload),'driver_sha256':sha(driver.encode()),'stdout_sha256':sha(r.stdout),'stderr_sha256':sha(r.stderr),'reference_fingerprint':freeze['reference_canonical_fingerprint'],'command':command if mode=='host' else command[:-1]+['<restored-owned-driver-source>'],'status':'PROCESS_FAILED_NO_RETRY','original_go_sqlx_or_db_execution':False,'neural_calls':0,'training_gold':False}
if r.returncode==0:
 result=json.loads(r.stdout);canonical=json.dumps(result['projection'],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode();observed=sha(canonical)
 assert observed==result['canonical_fingerprint']
 matches=observed==freeze['reference_canonical_fingerprint'] and result['projection']==reference
 outcome.update(actual_runtime=result['runtime'],observed_fingerprint=observed,full_projection_matches=matches,math_cases=result['math_cases'],source_cases=result['source_cases'],module_sha256=result['module_sha256'],status='REPLAY_MATCHES_ARCHIVED_REFERENCE' if matches else 'REFERENCE_MISMATCH_NO_PATCH_OR_RETRY')
(folder/'outcome.json').write_text(json.dumps(outcome,indent=2)+'\n')
print(json.dumps({k:outcome.get(k) for k in ['mode','status','returncode','actual_runtime','observed_fingerprint','math_cases','source_cases','wall_seconds']}))
if outcome['status']!='REPLAY_MATCHES_ARCHIVED_REFERENCE':raise SystemExit(2)
