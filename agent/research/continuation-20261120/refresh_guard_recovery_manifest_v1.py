"""Pin two validated caller files after preserving the exact prior recovery lock."""
import copy
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
target=ROOT/'agent/recovery/manifest.json'
original=target.read_bytes()
if hashlib.sha256(original).hexdigest()!='525b40dd8e1a7bea80ee01f2c39d309733f03e31c592e5742f7c229dc03e0043':raise ValueError('manifest drift; do not absorb owner changes')
before=json.loads(original);after=copy.deepcopy(before)
base=json.loads((P/'ruby-exception-guard-protocol-v1.json').read_text())['core_before']
regression=json.loads((P/'ruby-regression-after-exception-guard-v1.json').read_text())
if regression['exit_code']!=0:raise ValueError('existing regression did not pass')
for filename in ['ruby-exception-guard-final-v1.json','ruby-exception-ambiguity-final-v1.json']:
    if not all(row['matches']for row in json.loads((P/filename).read_text())['rows']):raise ValueError('frozen guard observations not accepted')
changes=[]
for name in base:
    matches=[(i,e)for i,e in enumerate(after['operational_files'])if e['path']==name]
    if len(matches)!=1 or matches[0][1]['sha256']!=base[name]:raise ValueError('source manifest preimage changed')
    i,old=matches[0];raw=(ROOT/name).read_bytes();new=dict(old,sha256=hashlib.sha256(raw).hexdigest(),size=len(raw))
    after['operational_files'][i]=new;changes.append({'before':old,'after':new,'reason':'Source-derived bilingual caught-exception identifier refusal; caller1.9.42;validated12researchobservations and unchanged262Ruby/1787assertions.'})
spec=importlib.util.spec_from_file_location('bootstrap_guard',ROOT/'agent/recovery/bootstrap.py');bootstrap=importlib.util.module_from_spec(spec);spec.loader.exec_module(bootstrap)
bootstrap.check_knowledge(after);bootstrap.model_metadata(after)
archive=ROOT/'.local-backups/continuation-20261120/recovery-manifests'/('525b40dd8e1a7bea80ee01f2c39d309733f03e31c592e5742f7c229dc03e0043.json')
with archive.open('xb')as stream:stream.write(original);stream.flush();os.fsync(stream.fileno())
if archive.read_bytes()!=original:raise ValueError('recovery preimage preservation failed')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
after['continuation_20261120_manifest_reconciliations'].append({'at':now,'prior_manifest':str(archive.relative_to(ROOT)),'prior_manifest_sha256':hashlib.sha256(original).hexdigest(),'changes':changes,'caller_version':'1.9.42','reason':'Pin the bounded validated caller correction, keeping old source/preimage archives and model identity.','model_object_changed':False,'permanent_tests_changed':False,'training_gold':False})
encoded=(json.dumps(after,indent=2,ensure_ascii=False)+'\n').encode()
with(P/'operational-manifest-guard-refresh-v1.json').open('xb')as stream:stream.write(encoded)
if target.read_bytes()!=original:raise ValueError('owner manifest changed;candidate preserved only')
temporary=target.with_name('manifest.exception-guard.tmp')
with temporary.open('xb')as stream:stream.write(encoded);stream.flush();os.fsync(stream.fileno())
if target.read_bytes()!=original or temporary.read_bytes()!=encoded:raise ValueError('atomic install precondition changed')
os.replace(temporary,target);fd=os.open(target.parent,os.O_RDONLY)
try:os.fsync(fd)
finally:os.close(fd)
installed=json.loads(target.read_bytes());bootstrap.check_knowledge(installed);bootstrap.model_metadata(installed)
if installed['model']!=before['model']or target.read_bytes()!=encoded:raise ValueError('post-install lock/model mismatch')
receipt={'at':now,'status':'VALIDATED_CALLER_HASHES_PINNED','changes':changes,'manifest_before_sha256':hashlib.sha256(original).hexdigest(),'manifest_after_sha256':hashlib.sha256(encoded).hexdigest(),'model_object_unchanged':True,'knowledge_files':len(installed['operational_files']),'source_preimages':'exception-guard-source-preimages-v1.json and exception-guard-first-candidate-preimages-v1.json','cold_boot_claimed':False}
(P/'operational-manifest-guard-refresh-receipt-v1.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k!='changes'}))
