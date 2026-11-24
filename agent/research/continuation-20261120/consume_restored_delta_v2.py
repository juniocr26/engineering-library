"""Load sealed research producers from the restored tree, never the live tree."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
receipt = json.loads((P / 'recovery-delta-receipt-v2.json').read_text())
restored = Path(receipt['restored_root'])
worker = r'''
import copy,hashlib,importlib.util,json,pathlib,sys,tarfile
sys.dont_write_bytecode=True
root=pathlib.Path(sys.argv[1]);p=root/'agent/research/continuation-20261120'
spec=importlib.util.spec_from_file_location('sealed_batch',p/'registered_claim_batch_v1.py');batch_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(batch_module)
for module in [batch_module,batch_module.single,batch_module.single.binding,batch_module.workspace,batch_module.candidates]:
 assert pathlib.Path(module.__file__).resolve().is_relative_to(root),module.__file__
cut=root/'.local-backups/continuation-20261120/paired-claim-batch-controls-v1';meta=json.loads((cut/'receipt.json').read_text());archive=root/meta['archive'];assert hashlib.sha256(archive.read_bytes()).hexdigest()==meta['sha256'];expected={e['path']:e for e in meta['entries']}
selected={'two-shared-document-modifications','modify-plus-addressed-noop','two-modifications-with-registered-synthetic-relocation'}
owned=root/'recovered-consumption-controls-v2';owned.mkdir(exist_ok=False)
with tarfile.open(archive)as tar:
 for member in tar.getmembers():
  path=pathlib.PurePosixPath(member.name);assert member.isfile()and not path.is_absolute()and'..'not in path.parts
  if path.parts[0]not in selected:continue
  raw=tar.extractfile(member).read();assert hashlib.sha256(raw).hexdigest()==expected[member.name]['sha256'];target=owned/member.name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
rows=[]
for name in sorted(selected):
 initial=json.loads((owned/name/'exact-inputs.json').read_text());registration=initial['registration'];old='/private/tmp/el-claim-batch-controls-20261120-v1'
 registration['documentation_root']=str(owned)+registration['documentation_root'][len(old):]
 for source in registration['source_registration']['sources'].values():
  assert source['root'].startswith(old+'/');source['root']=str(owned)+source['root'][len(old):]
 instance=batch_module.RegisteredClaimBatch(registration);result=instance.prepare(initial['requests']);assert result['status']=='PREPARED',result
 rows.append({'id':name,'status':result['status'],'operation_count':len(result['operations']),'candidate_hashes':{lang:c['candidate_sha256']for lang,c in result['candidates'].items()},'source_executed':result['source_executed'],'publication_authorized':result['publication_authorized']})
 if name=='two-shared-document-modifications':
  invalid=copy.deepcopy(initial['requests']);invalid[1]['replacements']['pt-br']='smart_truncate possui parametro inventado.\n'
  refused=instance.prepare(invalid);assert refused['status']=='REFUSED'and'candidates'not in refused
  rows.append({'id':'recovered-negative-incomplete-factual-language','status':'REFUSED','no_partial_candidate':True,'new_independent_case':False})
spec=importlib.util.spec_from_file_location('sealed_keyword_router',p/'closed_keyword_lifecycle_v1.py');router=importlib.util.module_from_spec(spec);spec.loader.exec_module(router)
assert pathlib.Path(router.prefix.__file__).resolve().is_relative_to(root)
packet=json.loads((root/'agent/research/documentation-intelligence-20261120/public-lifecycle-results-v1/public-remap-trace.json').read_text())['input'];result=router.decision(packet);assert result['action']=='MODIFY',result
rows.append({'id':'recovered-original-remap-keyword-packet','action':result['action'],'original_packet_sha256':result['original_packet_sha256'],'source_executed':False,'full_public_callable_executed':False})
print(json.dumps({'status':'VERIFIED','producer_modules_loaded_from_restored_root':True,'restored_batch_sha256':hashlib.sha256((p/'registered_claim_batch_v1.py').read_bytes()).hexdigest(),'restored_router_sha256':hashlib.sha256((p/'closed_keyword_lifecycle_v1.py').read_bytes()).hexdigest(),'rows':rows,'model_calls':0,'source_native_experiments_rerun':False,'neural_training':False,'production_or_catalog_written':False,'new_distinct_evaluation_cases':0}))
'''
start = time.monotonic()
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', GIT_OPTIONAL_LOCKS='0')
process = subprocess.run([sys.executable, '-c', worker, str(restored)], cwd=restored, env=env, text=True, capture_output=True, timeout=120)
(P/'restored-delta-consumption-v2.stdout').write_text(process.stdout)
(P/'restored-delta-consumption-v2.stderr').write_text(process.stderr)
record = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'exit_code': process.returncode, 'wall_seconds': time.monotonic() - start, 'restore_root': str(restored), 'source_cut_receipt_sha256': hashlib.sha256((P/'recovery-delta-receipt-v2.json').read_bytes()).hexdigest()}
if process.returncode == 0:
    record.update(json.loads(process.stdout))
    manifest = json.loads((ROOT / receipt['input_manifest']['path']).read_text())
    for name, expected in manifest['effective_expected_files'].items():
        path = restored / name
        assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == expected['sha256'], name
    record['all_20134_expected_source_and_evidence_files_unchanged_after_consumption'] = True
with (P/'restored-delta-consumption-v2.json').open('x') as stream:
    stream.write(json.dumps(record, indent=2) + '\n')
print(json.dumps({k:v for k,v in record.items() if k != 'rows'}))
raise SystemExit(process.returncode)
