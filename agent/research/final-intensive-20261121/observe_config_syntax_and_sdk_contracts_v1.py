import subprocess,json,hashlib,datetime
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[2];folder=p/'go-image-config-static-observations-v1';folder.mkdir();sdk=folder/'existing-sdk-contract-source';sdk.mkdir();edges=[]
for source in [Path('/usr/local/go/src/os/env.go'),Path('/usr/local/go/src/fmt/errors.go'),Path('/usr/local/go/LICENSE')]:
 raw=source.read_bytes();target=sdk/(source.parent.name+'-'+source.name if source.name!='LICENSE' else 'LICENSE');target.open('xb').write(raw);edges.append({'source_path':str(source),'saved_path':str(target.relative_to(root)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'role':'ExistingGo1.27.1 SDK source contract, not proof of actual target runtime SDK'})
commands=[]
for name in ['backend/internal/config/config.go','backend/cmd/api/main.go','backend/internal/infrastructure/http/server.go','backend/internal/infrastructure/http/server_test.go']:
 f=p/'go-image-configuration-source-context-v1'/name;cmd=['/usr/local/go/bin/gofmt','-e','-d',str(f)];r=subprocess.run(cmd,capture_output=True,timeout=20);out=folder/(f.name+'.syntax.stdout.txt');err=folder/(f.name+'.syntax.stderr.txt');out.open('xb').write(r.stdout);err.open('xb').write(r.stderr);commands.append({'command':cmd,'exit_code':r.returncode,'source_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'stdout_path':str(out.relative_to(root)),'stderr_path':str(err.relative_to(root)),'meaning':'Parser/format observation only; diff output is not a syntax failure or target execution'});assert r.returncode==0
with (p/'go-image-config-static-observations-v1.json').open('x') as f:json.dump({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':commands,'sdk_contract_sources':edges,'source_tests_executed':False,'application_runtime_executed':False,'model_calls':0},f,indent=2);f.write('\n')
print('4 actual Go sources parsed; existing SDK env/fmt contract source retained with license')
