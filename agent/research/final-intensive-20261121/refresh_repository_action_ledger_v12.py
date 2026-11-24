from pathlib import Path
import json,hashlib,datetime
p=Path(__file__).resolve().parent;root=p.parents[2];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();prior=p/'repository-action-ledger-v11.json';d=json.loads(prior.read_text());f=p/'redis-targets-source-acquisition-v1.json';a=json.loads(f.read_text());by={r['absolute_path']:r for r in d['records']}
for c in a['commands']:
 argv=c['command'];r=by[argv[argv.index('-C')+1]];r.setdefault('new_actual_command_receipts',[]).append({'receipt':str(f.relative_to(root)),'receipt_sha256':sha(f),**c});key='read_only_acquisition_commands' if c['exit_code']==0 else 'failed_acquisition_commands'
 if argv not in r[key]:r[key].append(argv)
 if c['exit_code']==0 and 'show' in argv:
  path=argv[-1].split(':',1)[1]
  if path not in r['source_paths_acquired_for_selected_scope_review']:r['source_paths_acquired_for_selected_scope_review'].append(path)
for r in d['records']:r['source_paths_acquired_for_selected_scope_review']=sorted(set(r['source_paths_acquired_for_selected_scope_review']))
rails=p/'rails-request-source-acquisition-v1.json';captures=json.loads(rails.read_text());own=next(r for r in d['records'] if Path(r['absolute_path'])==root);own.setdefault('public_installed_dependency_reads',[]).append({'receipt':str(rails.relative_to(root)),'receipt_sha256':sha(rails),'records':captures['records'],'purpose':'Read/copy installed public actionpack8.1.4 source/license/gemspec for original target audit; no gemspec/target/framework execution.'})
d.setdefault('research_existing_tool_executions',[]).extend([{'receipt':str((p/name).relative_to(root)),'receipt_sha256':sha(p/name),'kind':kind} for name,kind in [('rails-request-static-observations-v1.json','SystemRuby2.6Ripper parsespublicsource asdata; notRailsruntimecompatibility'),('go-image-quality-static-observations-v1.json','ExistingGoASTproducer syntaxinspection only'),('go-image-dimensions-static-observations-v1.json','ExistingGoASTproducer syntaxinspection only'),('redis-c-raw-token-protocol-v1.json','Clang21rawtokenlexingonly; notpreprocess/type/AST/build/serverexecution')]])
d.setdefault('public_metadata_network_attempts',[]).append({'receipt':str((p/'candidate-tokenizer-json-acquisition-results-v1.json').relative_to(root)),'receipt_sha256':sha(p/'candidate-tokenizer-json-acquisition-results-v1.json'),'url':json.loads((p/'candidate-tokenizer-json-acquisition-results-v1.json').read_text())['url'],'outcome':'Oneattempt,DNSfailurebeforeHTTPresponse/body;no retries/weights/framework/modelexecution','new_checkout':False})
d.update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),extends={'path':str(prior.relative_to(root)),'sha256':sha(prior)},added_source_acquisition_receipt_v12={'path':str(f.relative_to(root)),'sha256':sha(f)},refinement='AddactualRedisreadonlyGitcommands, ownpublicactionpackdependencyreads andexistingparser/lexerresearch execution, plusfailedpublicpinnedtokenizerJSONrequest. NotadditionalGitcheckouts orprivateexternalbodyreads. Statev4/inventorycut011fieldsremainexplicitoldercuts,notfreshfinalstate.')
assert len(d['records'])==42
with (p/'repository-action-ledger-v12.json').open('x') as z:json.dump(d,z,indent=2);z.write('\n')
print(json.dumps({'repository_blocks':42,'new_Redis_commands':len(a['commands']),'new_public_dependency_files':len(captures['records']),'external_mutations':0}))
