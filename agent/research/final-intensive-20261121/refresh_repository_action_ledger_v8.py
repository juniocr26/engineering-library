import json,datetime,hashlib
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[2];prior=p/'repository-action-ledger-v7.json';d=json.loads(prior.read_text());state=p/'repository-state-observation-v4.json';current={r['repository']:r for r in json.loads(state.read_text())['records']};by={r['absolute_path']:r for r in d['records']};names=['chi-revision-context-acquisition-v1.json','chi-revision-context-acquisition-v2.json','chi-revision-context-acquisition-v3.json','go-image-animation-context-acquisition-v1.json','go-image-animation-extra-context-acquisition-v1.json','go-image-compression-source-acquisition-v1.json','go-image-application-source-graph-v1/protocol.json'];receipts=[];added=0
for name in names:
 f=p/name;v=json.loads(f.read_text());digest=hashlib.sha256(f.read_bytes()).hexdigest();receipts.append({'path':str(f.relative_to(root)),'sha256':digest})
 def walk(x):
  global added
  if isinstance(x,dict):
   argv=x.get('command')
   if isinstance(argv,list) and argv and argv[0]=='git' and 'exit_code' in x and '-C' in argv:
    repo=argv[argv.index('-C')+1];r=by[repo];edge={'receipt':str(f.relative_to(root)),'receipt_sha256':digest,'command':argv,'exit_code':x['exit_code'],'stderr':x.get('stderr','')};r.setdefault('new_actual_command_receipts',[]).append(edge);added+=1
    target=r['read_only_acquisition_commands'] if x['exit_code']==0 else r['failed_acquisition_commands']
    if argv not in target:target.append(argv)
    if x['exit_code']==0 and 'show' in argv:
     operand=argv[-1]
     if ':' in operand:
      path=operand.split(':',1)[1]
      if path and path not in r['source_paths_acquired_for_selected_scope_review']:r['source_paths_acquired_for_selected_scope_review'].append(path)
   for value in x.values():walk(value)
  elif isinstance(x,list):
   for value in x:walk(value)
 walk(v)
for r in d['records']:
 r['latest_observed_state']={'receipt':str(state.relative_to(root)),'head':current[r['repository']]['head'],'head_matches_baseline':current[r['repository']]['head_matches_baseline'],'status_matches_baseline':current[r['repository']]['status_matches_baseline'],'actual_read_only_commands':current[r['repository']]['commands']};r['source_paths_acquired_for_selected_scope_review']=sorted(set(r['source_paths_acquired_for_selected_scope_review']))
d.update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),extends={'path':str(prior.relative_to(root)),'sha256':hashlib.sha256(prior.read_bytes()).hexdigest()},current_repository_state_receipt=str(state.relative_to(root)),current_campaign_scope_receipt='agent/research/final-intensive-20261121/campaign-scope-observation-v6.json',added_source_acquisition_receipts=receipts,refinement='Include all actual commands in selected Chi revision and new Go Image receipts; exact target source paths deduplicated, failures retained. No source-program/runtime or local-model execution inferred from acquiring sources or research compiler execution.',self_cut='Created-file inventory remains explicitly cut011, not an exhaustive current final list; subsequent artifacts require next inventory. Final campaign ledger still pending.')
d['new_owned_go_compiler_build_receipts']=[{'path':str((p/name).relative_to(root)),'sha256':hashlib.sha256((p/name).read_bytes()).hexdigest(),'command':json.loads((p/name).read_text())['command']} for name in ['go-source-graph-type-observer-build-v1.json','go-source-graph-type-observer-build-v2.json','go-source-graph-type-observer-build-v3.json']]
assert len(d['records'])==42
with (p/'repository-action-ledger-v8.json').open('x') as f:json.dump(d,f,indent=2);f.write('\n')
print(json.dumps({'repository_blocks':42,'new_actual_command_witnesses':added,'go_image_source_paths':len(by['/Users/juniorosa/Documents/Projetos/Portifólio/go-image-optimizer']['source_paths_acquired_for_selected_scope_review']),'external_mutations':0}))
