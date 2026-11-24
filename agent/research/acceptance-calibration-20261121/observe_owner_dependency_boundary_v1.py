"""Parse two frozen owned binding controls; never execute their source."""
from pathlib import Path
import datetime,hashlib,json,subprocess
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
protocol_path=P/'owner-capsule-dependency-boundary-protocol-v1.json'
protocol=json.loads(protocol_path.read_text());baseline=json.loads((P/protocol['baseline_result']).read_text())
assert hashlib.sha256((P/protocol['baseline_result']).read_bytes()).hexdigest()==protocol['baseline_result_sha256']
for row in protocol['observers']:assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256']
originals={r['task']:r['normalized_owner_hashes']for r in baseline['records']if r['id'].endswith('-original')}
rows=[]
for case in protocol['cases']:
 source=ROOT/case['path'];raw=source.read_bytes();assert hashlib.sha256(raw).hexdigest()==case['sha256']
 if case['task']=='cobra':command=[str((P/'go-owner-capsule-observer-v1').resolve()),str(source.resolve())];data=None
 else:command=['/usr/local/bin/docker','exec','-i','-w','/app/frontend','engineering-library-frontend-1','node','-e',(P/'observe_ts_owner_capsule_v1.cjs').read_text()];data=raw
 out=subprocess.run(command,input=data,capture_output=True,timeout=30)
 with(source.parent/'observer.stdout.json').open('xb')as f:f.write(out.stdout)
 with(source.parent/'observer.stderr.txt').open('xb')as f:f.write(out.stderr)
 assert out.returncode==0,out.stderr.decode()
 result=json.loads(out.stdout);identities={name:value['normalized_owner_sha256']for name,value in result['selected_owners'].items()}
 same=identities==originals[case['task']];pin=case['sha256']==case['original_source_sha256']
 rows.append({**case,'selected_owner_identity_matches':same,'original_full_source_identity_matches':pin,
              'matches_frozen_identity_expectations':same==case['expected_selected_owner_identity_matches']and pin==case['expected_original_full_source_identity_matches'],
              'normalized_owner_hashes':identities,'stdout_sha256':hashlib.sha256(out.stdout).hexdigest(),
              'source_executed':False,'whole_document_admitted':False,'runtime_refutation_executed':False})
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':protocol_path.name,
 'protocol_sha256':hashlib.sha256(protocol_path.read_bytes()).hexdigest(),'records':rows,
 'cases':len(rows),'all_expected_identity_boundaries_observed':all(r['matches_frozen_identity_expectations']for r in rows),
 'selected_owner_identity_collisions':sum(r['selected_owner_identity_matches']for r in rows),
 'original_source_pin_mismatches':sum(not r['original_full_source_identity_matches']for r in rows),
 'interpretation':'Bothownedbindingchangespreserveselectedowneridentitybutinvalidateattributedbehaviorunderwrittenbindingreferences. Fullowneridentityisusefulinvalidationevidence,notsemanticadmission. Alloriginalsourcepinsrejectthem; no currentTfalseacceptance or genericproof. No externalcodeexecuted/typechecked.',
 'model_calls':0,'production_changes':0,'gold':0,'optimizer_updates':0}
with(P/'owner-capsule-dependency-boundary-results-v1.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in result.items()if k!='records'},indent=2))
