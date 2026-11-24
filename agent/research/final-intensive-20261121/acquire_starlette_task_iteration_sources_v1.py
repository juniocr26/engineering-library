from pathlib import Path
import json,hashlib,datetime,subprocess,ast
p=Path(__file__).resolve().parent;root=p.parents[2];protocol=json.loads((p/'starlette-task-iteration-target-protocol-v1.json').read_text());repo=protocol['repository'];revision=protocol['revision'];out=p/'starlette-task-iteration-source-context-v1';out.mkdir();commands=[];records=[]
for path in ['starlette/background.py','starlette/concurrency.py','starlette/_utils.py','starlette/responses.py','tests/test_background.py','tests/test_concurrency.py','LICENSE.md','pyproject.toml']:
 argv=['git','--no-optional-locks','-C',repo,'show',revision+':'+path];r=subprocess.run(argv,capture_output=True,timeout=30);commands.append({'command':argv,'exit_code':r.returncode,'stderr':r.stderr.decode()})
 if r.returncode:continue
 f=out/path;f.parent.mkdir(parents=True,exist_ok=True);f.open('xb').write(r.stdout);rec={'source_path':path,'saved_path':str(f.relative_to(root)),'bytes':len(r.stdout),'sha256':hashlib.sha256(r.stdout).hexdigest()}
 if f.suffix=='.py':rec['syntax_ast_parse']='PASS';ast.parse(r.stdout,filename=path)
 records.append(rec)
argv=['git','--no-optional-locks','-C',repo,'grep','-n','-e','BackgroundTask','-e','iterate_in_threadpool',revision,'--','starlette/background.py','starlette/concurrency.py','starlette/responses.py'];r=subprocess.run(argv,capture_output=True,timeout=30);commands.append({'command':argv,'exit_code':r.returncode,'stdout':r.stdout.decode(),'stderr':r.stderr.decode()})
x={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':commands,'records':records,'external_writes':False,'source_or_tests_executed':False}
with (p/'starlette-task-iteration-source-acquisition-v1.json').open('x') as f:json.dump(x,f,indent=2);f.write('\n')
print(json.dumps({'files':len(records),'syntax_only':sum('syntax_ast_parse' in r for r in records),'failed_commands':sum(c['exit_code']!=0 for c in commands)}))
