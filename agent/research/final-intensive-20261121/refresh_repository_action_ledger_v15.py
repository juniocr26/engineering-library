from pathlib import Path
import json,datetime,hashlib
p=Path(__file__).resolve().parent;root=p.parents[2];old=p/'repository-action-ledger-v14.json';d=json.loads(old.read_text());by={r['repository']:r for r in d['records']};added=0
for repo,names in [('ruff',['ruff-target-source-acquisition-v1.json']),('opencv',['opencv-targets-source-acquisition-v1.json','opencv-targets-source-acquisition-v2.json','opencv-targets-source-acquisition-v3.json'])]:
 rec=by[repo]
 for name in names:
  f=p/name
  for e in json.loads(f.read_text())['records']:
   attempt={'command':e['command'],'exit_code':e['exit_code'],'receipt':str(f.relative_to(root))}
   if 'saved_path' in e:attempt['saved_path']=e['saved_path']
   rec.setdefault('read_only_acquisition_attempts',[]).append(attempt);added+=1
   if e['exit_code']==0:
    source=e['command'][-1].split(':',1)[1]
    if source not in rec.setdefault('source_paths_acquired_for_selected_scope_review',[]):rec['source_paths_acquired_for_selected_scope_review'].append(source)
    rec.setdefault('read_only_acquisition_commands',[]).append(e['command'])
f=p/'opencv-scalar-declaration-location-v1.json';e=json.loads(f.read_text());by['opencv'].setdefault('read_only_search_commands',[]).append({'receipt':str(f.relative_to(root)),'command':e['command'],'exit_code':e['exit_code']})
d.update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),extends={'path':str(old.relative_to(root)),'sha256':hashlib.sha256(old.read_bytes()).hexdigest()},additional_public_network_query={'protocol':str((p/'go-vendored-httpguts-upstream-identity-protocol-v1.json').relative_to(root)),'result':str((p/'go-vendored-httpguts-upstream-identity-results-v1.json').relative_to(root)),'status':'INCONCLUSIVE_PRIMARY_METADATA_TOOL_ACCESS','local_checkout_created_or_modified':False},self_cut='Adds actual Ruff/OpenCV reads and bounded pinned declaration search, including failed missing path; previous statev5/scopev7/inventorycut014 remain dated observations, not fresh final-state proof.')
with (p/'repository-action-ledger-v15.json').open('x') as f:json.dump(d,f,indent=2);f.write('\n')
print(json.dumps({'repository_blocks':len(d['records']),'acquisition_attempts_added':added,'search_commands_added':1,'production_mutation':False}))
