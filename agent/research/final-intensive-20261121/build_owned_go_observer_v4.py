import json,datetime,hashlib,subprocess,os
from pathlib import Path
p=Path(__file__).resolve().parent;prior=json.loads((p/'go-source-graph-type-observer-build-v1.json').read_text());folder=p/'offline-go-type-observer-v4';cmd=['/usr/local/go/bin/go','build','-o',str(folder/'observer'),str(folder/'main.go')];overrides=prior['environment_overrides'];env={**os.environ,**overrides};start=datetime.datetime.now(datetime.timezone.utc);before=hashlib.sha256((folder/'main.go').read_bytes()).hexdigest();r=subprocess.run(cmd,capture_output=True,timeout=60,env=env);assert hashlib.sha256((folder/'main.go').read_bytes()).hexdigest()==before
(folder/'build.stdout.txt').open('xb').write(r.stdout);(folder/'build.stderr.txt').open('xb').write(r.stderr);out={'at':start.isoformat(),'command':cmd,'environment_overrides':overrides,'exit_code':r.returncode,'seconds':(datetime.datetime.now(datetime.timezone.utc)-start).total_seconds(),'source_sha256':before,'previous_observers_preserved':True,'network_or_installs':False,'source_target_executed':False}
if r.returncode==0:out.update(binary_sha256=hashlib.sha256((folder/'observer').read_bytes()).hexdigest(),binary_bytes=(folder/'observer').stat().st_size)
with (p/'go-source-graph-type-observer-build-v2.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps(out));print(r.stderr.decode());assert r.returncode==0
