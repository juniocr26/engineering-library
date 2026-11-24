from pathlib import Path
import json,subprocess,hashlib,datetime
p=Path(__file__).resolve().parent;root=p.parents[2];source=p/'sdk-retry-target-source-context-v1';records=[];parser=Path('/usr/local/go/bin/gofmt');assert parser.is_file()
for f in sorted(source.rglob('*.go')):
 raw=f.read_bytes();cmd=[str(parser),'-e'];r=subprocess.run(cmd,input=raw,capture_output=True,timeout=20);records.append({'path':str(f.relative_to(root)),'source_sha256':hashlib.sha256(raw).hexdigest(),'command':cmd,'exit_code':r.returncode,'stderr':r.stderr.decode(),'formatted_stdout_sha256':hashlib.sha256(r.stdout).hexdigest(),'source_not_modified':f.read_bytes()==raw});assert r.returncode==0 and not r.stderr
bad=b'package labels\nfunc broken( {\n';f=p/'sdk-retry-owned-syntax-negative-v1.go.txt'
with f.open('xb') as s:s.write(bad)
r=subprocess.run([str(parser),'-e'],input=bad,capture_output=True,timeout=20);assert r.returncode!=0 and r.stderr
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'parser_path':str(parser),'parser_sha256':hashlib.sha256(parser.read_bytes()).hexdigest(),'target_files':records,'owned_negative':{'path':str(f.relative_to(root)),'sha256':hashlib.sha256(bad).hexdigest(),'exit_code':r.returncode,'stderr':r.stderr.decode()},'syntax_only':True,'no_import_typecheck_build_or_SDK_execution':True,'new_model_calls':0}
with (p/'sdk-retry-target-syntax-observations-v1.json').open('x') as s:json.dump(out,s,indent=2);s.write('\n')
print(json.dumps({'Go_files_syntax_pass':len(records),'owned_syntax_error_refused':1,'type_or_runtime':False}))
