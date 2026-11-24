"""Pin the validated caller correction while retaining exact operational history."""
import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
manifest=ROOT/'agent/recovery/manifest.json'
raw=manifest.read_bytes();before_sha=hashlib.sha256(raw).hexdigest();before=json.loads(raw);after=copy.deepcopy(before)
# These receipts must already exist and pass; never pin an unvalidated candidate.
guard=json.loads((P/'returned-map-renderer-candidate-v1.json').read_text());assert guard['matches']==guard['n']==19 and guard['caller_version']=='1.9.43'
catch=json.loads((P/'caught-guard-after-returned-map-v1.json').read_text());assert catch['all_previous_catch_outcomes_preserved']is True
ruby=json.loads((P/'ruby-regression-after-returned-map-v1.json').read_text());assert ruby['exit_code']==0 and ruby['summary']=={'runs':262,'assertions':1787,'failures':0,'errors':0,'skips':0}
python=json.loads((P/'python-regression-after-returned-map-v1.json').read_text());assert python['exit_code']==0 and python['existing_tests']==3
history=ROOT/'.local-backups/continuation-20261120/recovery-manifests';history.mkdir(exist_ok=True)
preimage=history/(before_sha+'.json')
with preimage.open('xb')as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
changes=[]
for row in after['operational_files']:
 if row['path']in {'backend/lib/documentation/command.rb','backend/lib/documentation/python_structure.py'}:
  old=copy.deepcopy(row);data=(ROOT/row['path']).read_bytes();row.update(sha256=hashlib.sha256(data).hexdigest(),size=len(data));changes.append({'before':old,'after':copy.deepcopy(row),'reason':'Validated1.9.43bounded direct-return mapping reference preservation;19guard-action checks with six explicit semantic/profile limits,12previouscatchcases,262Ruby/1787assertions and3Python checks.'})
assert len(changes)==2 and before['model']==after['model']
at=datetime.datetime.now(datetime.timezone.utc).isoformat()
after['continuation_20261120_manifest_reconciliations'].append({'at':at,'prior_manifest':str(preimage.relative_to(ROOT)),'prior_manifest_sha256':before_sha,'changes':changes,'caller_version':'1.9.43','reason':'Pin only the two validated source files; preserve operational preimages, sealed cuts and model identity.','model_object_changed':False,'permanent_tests_changed':False,'training_gold':False})
encoded=(json.dumps(after,ensure_ascii=False,indent=2)+'\n').encode();temporary=manifest.with_name('.manifest-returned-map-update.tmp')
with temporary.open('xb')as stream:stream.write(encoded);stream.flush();os.fsync(stream.fileno())
os.replace(temporary,manifest)
process=subprocess.run([sys.executable,str(ROOT/'agent/recovery/bootstrap.py'),'knowledge'],cwd=ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',GIT_OPTIONAL_LOCKS='0'),text=True,capture_output=True,timeout=90)
(P/'normal-bootstrap-after-returned-map-v1.stdout').write_text(process.stdout);(P/'normal-bootstrap-after-returned-map-v1.stderr').write_text(process.stderr)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':process.returncode,'manifest_before_sha256':before_sha,'manifest_after_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'prior_exact_manifest':str(preimage.relative_to(ROOT)),'changes':changes,'model_object_unchanged':before['model']==after['model'],'operational_file_count_unchanged':len(before['operational_files'])==len(after['operational_files']),'atomic_temporary_path_consumed_by_rename':str(temporary.relative_to(ROOT)),'cold_boot_or_remote_durability_claim':False}
if process.returncode==0:record['normal_bootstrap']=json.loads(process.stdout)
with(P/'operational-manifest-returned-map-refresh-v1.json').open('x')as stream:stream.write(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items()if k!='changes'}));raise SystemExit(process.returncode)
