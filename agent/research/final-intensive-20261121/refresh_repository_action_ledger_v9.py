import json,datetime,hashlib
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[2];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();prior=p/'repository-action-ledger-v8.json';d=json.loads(prior.read_text());by={r['absolute_path']:r for r in d['records']};names=['go-image-configuration-context-acquisition-v1.json','starlette-server-error-source-acquisition-v1.json','frontend-dimensions-source-acquisition-v1.json'];receipts=[];added=0;failed=0
for name in names:
 f=p/name;v=json.loads(f.read_text());digest=sha(f);receipts.append({'path':str(f.relative_to(root)),'sha256':digest})
 for c in v['commands']:
  argv=c['command'];r=by[argv[argv.index('-C')+1]];edge={'receipt':str(f.relative_to(root)),'receipt_sha256':digest,**c};r.setdefault('new_actual_command_receipts',[]).append(edge);added+=1;failed+=c['exit_code']!=0;target=r['read_only_acquisition_commands'] if c['exit_code']==0 else r['failed_acquisition_commands']
  if argv not in target:target.append(argv)
  if c['exit_code']==0 and 'show' in argv:
   src=argv[-1].split(':',1)[1]
   if src not in r['source_paths_acquired_for_selected_scope_review']:r['source_paths_acquired_for_selected_scope_review'].append(src)
 for rec in v['records']:assert sha(root/rec['saved_path'])==rec['sha256']
for r in d['records']:r['source_paths_acquired_for_selected_scope_review']=sorted(set(r['source_paths_acquired_for_selected_scope_review']))
inspections=d.setdefault('external_existing_SDK_read_only_inspections',[])
m=json.loads((p/'go-vendored-httpguts-snapshot-manifest-v1.json').read_text())
inspections.append({'kind':'Exact local installed Go SDK vendor snapshot, not a new checkout','receipt':str((p/'go-vendored-httpguts-snapshot-manifest-v1.json').relative_to(root)),'receipt_sha256':sha(p/'go-vendored-httpguts-snapshot-manifest-v1.json'),'records':m['records'],'source_revision':m['source_revision'],'upstream_commit_and_byte_equivalence_verified':False,'source_program_executed':False,'writes_to_SDK':False})
for folder in ['go-image-config-static-observations-v1/existing-sdk-contract-source']:
 f=p/folder
 inspections.append({'kind':'Existing SDK source contracts copied read-only for configuration review','directory':str(f.relative_to(root)),'records':[{'saved_path':str(a.relative_to(root)),'bytes':a.stat().st_size,'sha256':sha(a)} for a in sorted(f.rglob('*')) if a.is_file() and not a.is_symlink()],'target_execution':False})
proto=json.loads((p/'frontend-dimensions-typecheck-protocol-v1.json').read_text());d.setdefault('engineering_library_inspected_and_used_by_research_execution',[]).append({'kind':'Existing TypeScript 5.9.3 standard declarations read by JSC closed virtual module host','receipt':str((p/'frontend-dimensions-typecheck-protocol-v1.json').relative_to(root)),'receipt_sha256':sha(p/'frontend-dimensions-typecheck-protocol-v1.json'),'records':proto['standard_declarations'],'production_files_modified':False,'target_source_executed':False,'full_application_build':False})
d.update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),extends={'path':str(prior.relative_to(root)),'sha256':sha(prior)},new_source_acquisition_receipts_v9=receipts,refinement='Add exact config, Starlette and frontend source acquisition commands, including failed named config_test query. Existing SDK/vendor source reads and TypeScript standard declarations are additional evidence contexts, not additional repository checkouts or target execution.',self_cut='Created-file inventory field inherited from cut011 and state from observationv4; not exhaustive final inventory/state. New receipts appended without deleting prior witnesses.')
assert len(d['records'])==42
with (p/'repository-action-ledger-v9.json').open('x') as f:json.dump(d,f,indent=2);f.write('\n')
print(json.dumps({'repository_blocks':42,'new_actual_command_witnesses':added,'new_failed_commands':failed,'external_mutations':0}))
