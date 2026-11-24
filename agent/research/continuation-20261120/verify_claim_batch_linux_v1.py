"""Consume three existing positive batches on Linux, without new distinct cases."""
import datetime
import json
from pathlib import Path
import subprocess
import time

P = Path(__file__).resolve().parent
REMOTE = r'''
import hashlib,importlib.util,json,pathlib,sys,tarfile
sys.dont_write_bytecode=True
root=pathlib.Path('/sources/engineering-library');p=root/'agent/research/continuation-20261120'
cut=root/'.local-backups/continuation-20261120/paired-claim-batch-controls-v1'
receipt=json.loads((cut/'receipt.json').read_text());archive=root/receipt['archive']
assert hashlib.sha256(archive.read_bytes()).hexdigest()==receipt['sha256']
entries={e['path']:e for e in receipt['entries']}
selected={'two-shared-document-modifications','modify-plus-addressed-noop','two-modifications-with-registered-synthetic-relocation'}
base=pathlib.Path('/tmp/el-claim-batch-linux-20261120-v1');base.mkdir(exist_ok=False)
with tarfile.open(archive)as tar:
 for member in tar.getmembers():
  path=pathlib.PurePosixPath(member.name)
  assert member.isfile()and not path.is_absolute()and'..'not in path.parts
  if path.parts[0]not in selected:continue
  raw=tar.extractfile(member).read();assert hashlib.sha256(raw).hexdigest()==entries[member.name]['sha256']
  dest=base/member.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
spec=importlib.util.spec_from_file_location('linux_claim_batch',p/'registered_claim_batch_v1.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
rows=[]
for name in sorted(selected):
 initial=json.loads((base/name/'exact-inputs.json').read_text());registration=initial['registration'];old='/private/tmp/el-claim-batch-controls-20261120-v1'
 assert registration['documentation_root'].startswith(old+'/')
 registration['documentation_root']=str(base)+registration['documentation_root'][len(old):]
 for source in registration['source_registration']['sources'].values():
  assert source['root'].startswith(old+'/');source['root']=str(base)+source['root'][len(old):]
 batch=module.RegisteredClaimBatch(registration);result=batch.prepare(initial['requests']);assert result['status']=='PREPARED',result
 assert set(result['candidates'])=={'en','pt-br'}and len(result['operations'])==2
 rows.append({'id':name,'result':result,'source_relocation_is_synthetic':initial['source_relocation_is_synthetic']})
print(json.dumps({'status':'VERIFIED','python':sys.version,'platform':sys.platform,'rows':rows,'existing_cases_repeated_on_second_os':3,'new_distinct_cases':0,'source_executed':False,'model_calls':0,'windows_verified':False,'production_or_catalog_written':False,'producer_sha256':hashlib.sha256((p/'registered_claim_batch_v1.py').read_bytes()).hexdigest()}))
'''
start = time.monotonic()
process = subprocess.run(['docker','exec','engineering-library-backend-1','python3','-c',REMOTE], text=True, capture_output=True, timeout=120)
(P/'registered-claim-batch-linux-v1.stdout').write_text(process.stdout)
(P/'registered-claim-batch-linux-v1.stderr').write_text(process.stderr)
record = {'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':process.returncode,'wall_seconds':time.monotonic()-start}
if process.returncode == 0:
    record.update(json.loads(process.stdout))
with (P/'registered-claim-batch-linux-v1.json').open('x') as stream:
    stream.write(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k not in ['rows','python']}))
raise SystemExit(process.returncode)
