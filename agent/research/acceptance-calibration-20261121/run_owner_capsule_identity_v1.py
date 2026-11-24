"""Observe frozen owned source identity controls; no upstream source execution."""
from pathlib import Path
import datetime, hashlib, json, subprocess

P=Path(__file__).resolve().parent; ROOT=P.parents[2]
protocol_path=P/'owner-capsule-identity-protocol-v1.json'
protocol=json.loads(protocol_path.read_text())
for row in protocol['observers']:
    assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256']
binary=P/'go-owner-capsule-observer-v1'
freeze={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),
        'binary_mode':binary.stat().st_mode&0o777,
        'protocol_sha256':hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
        'compiled_owned_source_only':True,'upstream_executed':False}
with (P/'owner-capsule-identity-producer-freeze-v1.json').open('x') as stream:
    json.dump(freeze,stream,indent=2);stream.write('\n')
originals={}; rows=[]
for case in protocol['cases']:
    source=ROOT/case['path']; raw=source.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==case['sha256']
    if case['task']=='cobra':
        command=[str(binary.resolve()),str(source.resolve())]; data=None
    else:
        command=['/usr/local/bin/docker','exec','-i','-w','/app/frontend',
                 'engineering-library-frontend-1','node','-e',(P/'observe_ts_owner_capsule_v1.cjs').read_text()]
        data=raw
    out=subprocess.run(command,input=data,capture_output=True,timeout=30)
    with (source.parent/'observer.stdout.json').open('xb')as stream:stream.write(out.stdout)
    with (source.parent/'observer.stderr.txt').open('xb')as stream:stream.write(out.stderr)
    assert out.returncode==0,out.stderr.decode()
    observed=json.loads(out.stdout);assert observed['source_sha256']==case['sha256']
    identities={name:value['normalized_owner_sha256']for name,value in observed['selected_owners'].items()}
    if case['id'].endswith('-original'):originals[case['task']]=identities
    equal=identities==originals[case['task']]
    row={**case,'selected_owner_identity_matches':equal,
         'normalized_owner_hashes':identities,'matches_frozen_reference':equal==case['expected_selected_owner_identity_matches'],
         'observer_stdout_sha256':hashlib.sha256(out.stdout).hexdigest(),
         'exit_code':out.returncode,'whole_document_admitted':False,'source_executed':False}
    with (source.parent/'observation-v1.json').open('x')as stream:json.dump(row,stream,indent=2);stream.write('\n')
    rows.append(row)
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':protocol_path.name,
        'protocol_sha256':freeze['protocol_sha256'],'records':rows,'cases':len(rows),
        'all_identity_expectations_match':all(r['matches_frozen_reference']for r in rows),
        'selected_owner_identity_matches':sum(r['selected_owner_identity_matches']for r in rows),
        'selected_owner_identity_mismatches':sum(not r['selected_owner_identity_matches']for r in rows),
        'interpretation':'Fullselected-owneridentitydetectsbodychangesmissedbynormalizedrelationvectorsandretainscomments/unselectedbodychangesinthisfiniteprofile. Identityisnotsemanticcertification: imports/globalbindings/helperdependencies/typechecking/runtime remainunverified. No originalTpin/referenceoracceptancechanged; no new-revisionwhole-noteadmission.',
        'prior_exposed_controls':6,'fresh_owned_source_variants':6,'generic_semantic_accuracy':None,
        'model_calls':0,'production_changes':0,'gold':0,'optimizer_updates':0}
with (P/'owner-capsule-identity-results-v1.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps({k:v for k,v in result.items()if k!='records'},indent=2))
