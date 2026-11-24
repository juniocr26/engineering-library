from pathlib import Path
import json,hashlib,datetime
from pinned_tree_membership_v1 import verify_membership
P=Path(__file__).resolve().parent;ROOT=P.parents[2];proof=json.loads((P/'pinned-tree-positive-witness-results-v1.json').read_bytes());objects={(e['kind'],e['git_oid']):(ROOT/e['path']).read_bytes() for e in proof['saved_objects']};commit=proof['pin'];path=proof['selected_path'];sha=proof['leaf_sha256'];cases=[('intact-positive',None),('corrupted-blob','OBJECT_HASH_MISMATCH'),('missing-root-tree','MISSING_OBJECT'),('missing-blob','MISSING_OBJECT'),('wrong-path','PATH_NOT_MEMBER'),('wrong-source-SHA256','EXPECTED_SOURCE_HASH_MISMATCH'),('parent-path','UNSAFE_SELECTED_PATH')]
protocol={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'before_outcomes':True,'verifier_sha256':hashlib.sha256((P/'pinned_tree_membership_v1.py').read_bytes()).hexdigest(),'proof_sha256':hashlib.sha256((P/'pinned-tree-positive-witness-results-v1.json').read_bytes()).hexdigest(),'cases':[{'id':i,'expected_refusal':e} for i,e in cases],'scope':'One real previously exposed public source membership proof plus six owned perturbations; not general semanticFAR, globalcompleteness or REMOVE correctness.'}
with (P/'pinned-tree-membership-controls-protocol-v1.json').open('x') as f:json.dump(protocol,f,indent=2);f.write('\n')
rows=[]
for name,expected in cases:
 data=dict(objects);selected=path;expected_sha=sha
 if name=='corrupted-blob':key=('blob',proof['leaf_blob_oid']);data[key]=data[key]+b'X'
 elif name=='missing-root-tree':data.pop(('tree',proof['root_tree_oid']))
 elif name=='missing-blob':data.pop(('blob',proof['leaf_blob_oid']))
 elif name=='wrong-path':selected=path+'.absent'
 elif name=='wrong-source-SHA256':expected_sha='0'*64
 elif name=='parent-path':selected='../'+path
 refusal=None;result=None
 try:result=verify_membership(commit,selected,data,expected_sha)
 except ValueError as e:refusal=str(e)
 matched=refusal==expected;rows.append({'id':name,'expected_refusal':expected,'actual_refusal':refusal,'result':result,'matched':matched})
assert all(r['matched'] for r in rows)
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':hashlib.sha256((P/'pinned-tree-membership-controls-protocol-v1.json').read_bytes()).hexdigest(),'verifier_sha256':protocol['verifier_sha256'],'cases':rows,'matched_controls':7,'intact_positive_membership_proofs':1,'negative_perturbations_refused':6,'git_commands_run_by_verifier':0,'target_source_execution':False,'model_calls':0,'production_changes':0,'global_scope_or_REMOVE_approval_inferred':False}
with (P/'pinned-tree-membership-controls-results-v1.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in out.items() if k!='cases'}))
