"""Compile owned observer with preserved offline toolchain in existing backend."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

P=Path('/sources/engineering-library/agent/research/continuation-20261120')
STUDY=P/'go-build-context-v1'
TOOLCHAIN=Path('/sources/engineering-library/.local-backups/continuation-20261119/cached-go-toolchain')
expected=json.loads(Path('/sources/engineering-library/.local-backups/continuation-20261119/cached-go-toolchain-receipt.json').read_text())['pins']
for name in ['bin/go','bin/gofmt','pkg/tool/linux_arm64/compile','LICENSE']:
    if hashlib.sha256((TOOLCHAIN/name).read_bytes()).hexdigest()!=expected[name]:raise ValueError('preserved compiler input changed: '+name)
work=Path('/tmp/el-cont-20261120-build-context-v2');work.mkdir(exist_ok=False)
artifacts=work/'build-artifacts';artifacts.mkdir(exist_ok=False)
source=STUDY/'main.go';source_before=source.read_bytes()
env=dict(os.environ,GOROOT=str(TOOLCHAIN),GOENV='off',GOTOOLCHAIN='local',GO111MODULE='off',GOWORK='off',GOPROXY='off',GOSUMDB='off',GOFLAGS='',CGO_ENABLED='0',GOOS='linux',GOARCH='arm64',GOCACHE=str(work/'cache'),GOMAXPROCS='2',GOMEMLIMIT='512MiB',GOTELEMETRY='off')
fmt=subprocess.run([str(TOOLCHAIN/'bin/gofmt'),str(source)],env=env,capture_output=True,timeout=20)
(artifacts/'gofmt.stderr').write_bytes(fmt.stderr)
if fmt.returncode:raise RuntimeError('gofmt failed;rawstderr retained')
formatted=artifacts/'main.formatted.go';formatted.write_bytes(fmt.stdout)
binary=artifacts/'build-context-linux-arm64'
command=[str(TOOLCHAIN/'bin/go'),'build','-p','1','-trimpath','-buildvcs=false','-o',str(binary),str(formatted)]
started=time.monotonic();result=subprocess.run(command,env=env,cwd=work,capture_output=True,timeout=240)
(artifacts/'build.stdout').write_bytes(result.stdout);(artifacts/'build.stderr').write_bytes(result.stderr)
receipt={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':command,'exit':result.returncode,'seconds':time.monotonic()-started,'compiler_sha256':expected['bin/go'],'original_source_sha256':hashlib.sha256(source_before).hexdigest(),'formatted_source_sha256':hashlib.sha256(fmt.stdout).hexdigest(),'source_unchanged':source.read_bytes()==source_before,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest()if binary.is_file()else None,'source_application_compiled':False,'owned_observer_compiled':True,'new_container':False,'dependencies_downloaded':False,'model_calls':0,'cache_path':str(work/'cache')}
(artifacts/'build-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
(artifacts/'GO-LICENSE').write_bytes((TOOLCHAIN/'LICENSE').read_bytes())
import tarfile
archive=work/'build-artifacts.tar.gz'
with tarfile.open(archive,'w:gz') as bundle:
    for item in sorted(artifacts.iterdir()):bundle.add(item,arcname=item.name,recursive=False)
print(json.dumps(dict(receipt,archive=str(archive),archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest())),flush=True)
if result.returncode:raise RuntimeError('owned observer build failed;all build evidence retained')
