"""Consume restored public archival and historical execution evidence only."""
from pathlib import Path
import argparse
import collections
import hashlib
import json

parser=argparse.ArgumentParser()
parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
args=parser.parse_args()
ROOT=args.root
P=ROOT/'agent/research/final-intensive-20261121'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
archived=json.loads((P/'archived-family-exposure-integrity-results-v2.json').read_text())
verified=0
for row in archived['records']:
    target=ROOT/row['snapshot']
    assert not target.is_symlink() and target.is_file()
    assert sha(target)==row['expected_sha256']
    assert target.stat().st_size==row['expected_bytes']
    verified+=1
assert verified==archived['matching_entries']==145
witnesses=json.loads((P/'model-exposure-execution-witness-audit-v1.json').read_text())
for row in witnesses['records']:
    for name in ['request','outcome','response','content']:
        assert sha(ROOT/row[name])==row[name+'_sha256']
    request=json.loads((ROOT/row['request']).read_text())
    outcome=json.loads((ROOT/row['outcome']).read_text())
    response=json.loads((ROOT/row['response']).read_text())
    assert row['verified_historical_execution_artifact'] is True
    assert outcome['raw_response_sha256']==sha(ROOT/row['response'])
    assert response['done'] is True and response['eval_count']>0
    assert response['eval_count']==outcome['eval_count']
    assert response['model']==request['model']
    assert response['message']['content']==(ROOT/row['content']).read_text()
    assert row['counted_as_new_model_call'] is False
matrix=json.loads((P/'repository-exposure-matrix-v3.json').read_text())
assert len(matrix['records'])==42
assert len({r['repository'] for r in matrix['records']})==42
for row in matrix['records']:
    assert row['training_eligible'] is False
    assert row['independent_evaluation_certified'] is False
    assert row['owner_training_gold'] is False
    if row['current_role']=='PRIVATE_METADATA_ONLY_NO_INFERENCE_NO_TRAINING':
        assert row['current_private_external_source_body_read'] is False
assert dict(collections.Counter(r['current_role'] for r in matrix['records']))==matrix['role_counts']
print(json.dumps({'public_archived_snapshots_hash_verified':verified,
                  'historical_execution_witnesses_verified':len(witnesses['records']),
                  'repository_matrix_rows_consistent':len(matrix['records']),
                  'new_model_calls':0,'training_eligible':0,
                  'scope':'Frozen metadata and actual restored public bytes. Catalog directory presence remains the original recorded observation, not a restored live catalog or clean-clone proof.'}))
