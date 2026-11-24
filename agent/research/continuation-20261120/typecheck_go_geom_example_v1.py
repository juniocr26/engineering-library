"""Typecheck exact chapter example with explicit precompiled import archives."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
import time

P=Path('/sources/engineering-library/agent/research/continuation-20261120')
protocol=json.loads((P/'go-geom-example-typecheck-protocol-v1.json').read_text())
source=P/'go-geom-illustrative-example-v1.go'
if hashlib.sha256(source.read_bytes()).hexdigest()!=protocol['example_source_sha256']:raise ValueError('chapter example changed')
prior=Path('/tmp/el-cont-20261120-go-geom-static-v1/artifacts');archive=prior/'geom-package.a'
if hashlib.sha256(archive.read_bytes()).hexdigest()!=protocol['subject_archive_sha256']:raise ValueError('subject archive changed,no rebuild')
work=Path('/tmp/el-cont-20261120-go-geom-example-v1');work.mkdir(exist_ok=False)
exports=json.loads((prior/'exports-map.json').read_text())['exports']
importcfg=work/'importcfg';importcfg.write_text(''.join('packagefile '+name+'='+path+'\n'for name,path in sorted(exports.items())))
toolchain=Path('/sources/engineering-library/.local-backups/continuation-20261119/cached-go-toolchain')
compiler=toolchain/'pkg/tool/linux_arm64/compile'
if hashlib.sha256(compiler.read_bytes()).hexdigest()!='4070e0e743ba23672219a3687a1f9bfb489fa5c95bfb6584b4f33932339f92ef':raise ValueError('compiler identity changed')
obj=work/'example.o';command=[str(compiler),'-p','main','-lang=go1.26','-importcfg',str(importcfg),'-o',str(obj),str(source)]
env=dict(os.environ,GOROOT=str(toolchain),GOENV='off',GOTOOLCHAIN='local',GOPROXY='off',GOSUMDB='off',GOMAXPROCS='2',GOMEMLIMIT='512MiB')
start=time.monotonic();r=subprocess.run(command,env=env,capture_output=True,timeout=30)
(work/'compile.stdout').write_bytes(r.stdout);(work/'compile.stderr').write_bytes(r.stderr)
receipt={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':command,'exit_code':r.returncode,'seconds':time.monotonic()-start,
         'source_sha256':protocol['example_source_sha256'],'subject_archive_sha256':protocol['subject_archive_sha256'],
         'object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest()if obj.is_file()else None,'subject_library_rebuilt':False,
         'example_linked':False,'example_executed':False,'subject_library_executed':False,'dependencies_downloaded':False,
         'scope':'Exact displayed Go example statically compiled to object against verified subject archive;not a runtime output check.'}
(work/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(work/'example.go').write_bytes(source.read_bytes())
bundle_path=work/'evidence.tar.gz'
with tarfile.open(bundle_path,'w:gz')as bundle:
    for name in ['importcfg','example.go','compile.stdout','compile.stderr','receipt.json']+(['example.o']if obj.exists()else[]):bundle.add(work/name,arcname=name,recursive=False)
print(json.dumps({'exit_code':r.returncode,'archive':str(bundle_path),'archive_sha256':hashlib.sha256(bundle_path.read_bytes()).hexdigest(),'example_executed':False}),flush=True)
if r.returncode:raise RuntimeError('static example failed;do not claim validity;rawevidencepreserved')
