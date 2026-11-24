from pathlib import Path
import json,hashlib,datetime,subprocess,shutil
p=Path(__file__).resolve().parent;root=p.parents[2];r=next(r for r in json.loads((p/'repository-action-ledger-v14.json').read_text())['records'] if r['repository']=='ruff');repo=r['absolute_path'];rev='0222c19dd8e0c9a927f2e47bf3774a108431da25';assert rev==r['preexisting_head']
protocol={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository':repo,'revision':rev,'required_scope':['Full source snapshots ofworkspace/settings.rs andlinter/settings/types.rs; selectedsource field/FormatterSettings impl, storeddefault/read-onlyresolver, compiledlistconstructor/iterator/Optionhelper andnegationbranches.','RelevantPythonVersion declaration source metadata, ifavailable withoutinventedpath/sourceidentity; no numericdefault orwholeconfigurationprecedence promised bychapter.','Actualbaseline sourcepacket/request/rawresponse andtype-domainclaim, fulloriginalENPT/3FAQs.','Rootlicense/Cargo/toolchainmetadata read asdata. No build/Cargo/rustup invocation ordownloads, toolchaininstallation orRuff/formatter execution.'],'examples_and_tests_profile':'Originalchapter hasno executable examples orruntimeclaims. Authorizedchecks are exactpinnedsource/statement-range/bilingual/FAQ/stdlibAPIreference review; no compiler/parser claim. Missingcriticalsourceidentity remainsINCONCLUSIVE. G5matchesfrozenDoDv3static/executionclaimrequirements,notRustbuildcertification.','existing_toolchain_metadata':{'PATH_rustc':shutil.which('rustc'),'PATH_rustfmt':shutil.which('rustfmt'),'rustup_toolchain_rustc_paths':[str(f) for f in (Path.home()/'.rustup/toolchains').glob('*/bin/rustc')]},'owner_questions':0,'model_calls':0,'criterion_change':False}
with (p/'ruff-target-source-protocol-v1.json').open('x') as f:json.dump(protocol,f,indent=2);f.write('\n')
folder=p/'ruff-target-source-context-v1';folder.mkdir();commands=[];records=[]
def run(args):
 argv=['git','--no-optional-locks','-C',repo]+args;x=subprocess.run(argv,capture_output=True,timeout=30);commands.append({'command':argv,'exit_code':x.returncode,'stdout':x.stdout.decode() if args[0]=='ls-tree' else None,'stderr':x.stderr.decode()});return x
names=run(['ls-tree','--name-only',rev]);assert names.returncode==0;licenses=[n for n in names.stdout.decode().splitlines() if any(s in n.upper() for s in ['LICENSE','COPYING'])]
for name in ['crates/ruff_workspace/src/settings.rs','crates/ruff_linter/src/settings/types.rs','Cargo.toml','rust-toolchain.toml']+licenses:
 x=run(['show',rev+':'+name])
 if x.returncode:continue
 dest=folder/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.open('xb').write(x.stdout);records.append({'source_path':name,'saved_path':str(dest.relative_to(root)),'sha256':hashlib.sha256(x.stdout).hexdigest(),'bytes':len(x.stdout)})
# Directory metadata only; choose the actual PythonVersion source by filename, not a guessed fabricated declaration.
x=run(['ls-tree','-r','--name-only',rev,'--','crates/ruff_python_ast/src/']);candidates=[n for n in x.stdout.decode().splitlines() if 'python_version' in n and n.endswith('.rs')]
for name in candidates:
 x=run(['show',rev+':'+name])
 if x.returncode:continue
 dest=folder/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.open('xb').write(x.stdout);records.append({'source_path':name,'saved_path':str(dest.relative_to(root)),'sha256':hashlib.sha256(x.stdout).hexdigest(),'bytes':len(x.stdout)})
with (p/'ruff-target-source-acquisition-v1.json').open('x') as f:json.dump({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':commands,'records':records,'license_filenames':licenses,'PythonVersion_source_candidates':candidates,'external_writes':False,'source_or_tests_or_Cargo_executed':False},f,indent=2);f.write('\n')
print(json.dumps({'files':len(records),'failed_commands':sum(c['exit_code']!=0 for c in commands),'license_names':licenses,'PythonVersion_source_files':candidates}))
