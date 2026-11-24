import argparse,json,hashlib
from pathlib import Path
from pinned_tree_membership_v1 import verify_membership
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True,type=Path);ROOT=ap.parse_args().root.resolve();P=ROOT/'agent/research/final-intensive-20261121';sha=lambda b:hashlib.sha256(b).hexdigest();protocol=json.loads((P/'pinned-tree-positive-witness-protocol-v1.json').read_bytes());proof=json.loads((P/'pinned-tree-positive-witness-results-v1.json').read_bytes());controls=json.loads((P/'pinned-tree-membership-controls-results-v1.json').read_bytes());cp=json.loads((P/'pinned-tree-membership-controls-protocol-v1.json').read_bytes());assert sha((P/'pinned-tree-positive-witness-protocol-v1.json').read_bytes())==proof['protocol_sha256'] and sha((P/'pinned-tree-positive-witness-results-v1.json').read_bytes())==cp['proof_sha256'] and sha((P/'pinned_tree_membership_v1.py').read_bytes())==cp['verifier_sha256']==controls['verifier_sha256']
objects={}
for e in proof['saved_objects']:
 f=ROOT/e['path'];assert f.resolve().is_relative_to(ROOT);raw=f.read_bytes();assert sha(raw)==e['sha256'] and len(raw)==e['bytes'];objects[(e['kind'],e['git_oid'])]=raw
result=verify_membership(protocol['pin'],protocol['selected_path'],objects,protocol['known_source_sha256']);assert result['blob_oid']==proof['leaf_blob_oid'] and result['blob_sha256']==proof['leaf_sha256'] and len(result['path_steps'])==5
assert result['global_scope_complete'] is False and result['REMOVE_allowed'] is False and proof['global_scope_complete_proved'] is False and proof['automatic_REMOVE_allowed'] is False
assert proof['before']==proof['after'] and all(c['exit_code']==0 for c in proof['commands'])
assert controls['matched_controls']==7 and controls['intact_positive_membership_proofs']==1 and controls['negative_perturbations_refused']==6 and all(x['matched'] for x in controls['cases'])
print(json.dumps({'status':'PASS_OFFLINE_PINNED_TREE_POSITIVE_MEMBERSHIP_RECOVERY','raw_objects':len(objects),'path_steps':5,'recorded_controls':7,'current_git_commands':0,'current_target_source_or_model_execution':False,'global_scope_complete':False,'automatic_REMOVE_allowed':False,'independent_human_or_semantic_approval_inferred':False}))
