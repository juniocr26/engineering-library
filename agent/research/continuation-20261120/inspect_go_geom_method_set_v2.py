"""Correct only owned export-scope reader; reuse successful subject archive."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import tarfile

P=Path('/sources/engineering-library/agent/research/continuation-20261120')
prior=Path('/tmp/el-cont-20261120-go-geom-static-v1/artifacts')
protocol=json.loads((P/'go-geom-method-set-scope-supplement-v1.json').read_text())
subject=prior/'geom-package.a'
if hashlib.sha256(subject.read_bytes()).hexdigest()!=protocol['reused_public_archive_sha256']:raise ValueError('subject archive drift;no rebuild')
work=Path('/tmp/el-cont-20261120-go-geom-reader-v2');work.mkdir(exist_ok=False)
artifacts=work/'artifacts';artifacts.mkdir()
toolchain=Path('/sources/engineering-library/.local-backups/continuation-20261119/cached-go-toolchain')
if hashlib.sha256((toolchain/'bin/go').read_bytes()).hexdigest()!='59c65090beeda377c09007eb8fae1c6aadf0a7b551e65ee13d461092d29e8005':raise ValueError('compiler drift')
env=dict(os.environ,GOROOT=str(toolchain),GOENV='off',GOTOOLCHAIN='local',GO111MODULE='off',GOWORK='off',GOPROXY='off',GOSUMDB='off',GOFLAGS='',CGO_ENABLED='0',GOOS='linux',GOARCH='arm64',GOCACHE='/tmp/el-cont-20261120-build-context-v2/cache',GOMAXPROCS='2',GOMEMLIMIT='512MiB',GOTELEMETRY='off')
source=P/'go-package-method-set-v2/main.go'
if hashlib.sha256(source.read_bytes()).hexdigest()!=protocol['owned_reader_source_sha256']:raise ValueError('owned source drift')
commands=[]

def run(label,command):
    start=time.monotonic();r=subprocess.run(command,env=env,cwd=work,capture_output=True,timeout=120)
    (artifacts/(label+'.stdout')).write_bytes(r.stdout);(artifacts/(label+'.stderr')).write_bytes(r.stderr)
    commands.append({'label':label,'command':command,'exit':r.returncode,'seconds':time.monotonic()-start})
    (artifacts/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    if r.returncode:raise ValueError('owned reader failure;preserve,no subject rebuild')
    return r

formatted=run('format',[str(toolchain/'bin/gofmt'),str(source)]).stdout
formatted_path=artifacts/'main.formatted.go';formatted_path.write_bytes(formatted);binary=artifacts/'method-set-linux-arm64'
run('build-owned-reader',[str(toolchain/'bin/go'),'build','-p','1','-trimpath','-buildvcs=false','-o',str(binary),str(formatted_path)])
exports=json.loads((prior/'exports-map.json').read_text());hashes={name:hashlib.sha256(Path(path).read_bytes()).hexdigest()for name,path in exports['exports'].items()}
result=run('method-set',[str(binary),str(prior/'exports-map.json')]);body=json.loads(result.stdout)
expected=json.loads((P/'go-geom-static-method-set-oracle-v1.json').read_text())['expected_receivers']
checks={item['name']:item['declaring_receiver']==expected[item['name']]for item in body['point_methods']}
unchanged=all(hashlib.sha256(Path(exports['exports'][name]).read_bytes()).hexdigest()==digest for name,digest in hashes.items())
provenance=json.loads((P/'go-geom-root-package-provenance-v1.json').read_text());base=P/'new-public-sources-v1/twpayne--go-geom'/provenance['revision']
source_checks={item['path']:hashlib.sha256((base/item['path']).read_bytes()).hexdigest()==item['sha256']for item in provenance['rows']}
receipt={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'STATIC_METHOD_SET_AND_DECLARING_RECEIVERS_VERIFIED','revision':provenance['revision'],
         'subject_archive_sha256':protocol['reused_public_archive_sha256'],'subject_library_build_attempts':1,'subject_library_rebuilt':False,
         'method_set':body,'receiver_checks':checks,'source_checks':source_checks,'export_archive_hashes':hashes,'export_archives_unchanged':unchanged,
         'all_checks_pass':all(checks.values())and len(checks)==7 and all(source_checks.values())and unchanged,
         'owned_reader_binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'commands':commands,
         'source_library_executed':False,'tests_or_generator_executed':False,'dependencies_downloaded':False,
         'runtime_state_or_concurrency_verified':False,'static_context':{'toolchain':'go1.27.4','goos':'linux','goarch':'arm64','cgo':False,'source_go_directive':'1.26.3'},
         'private_helpers_policy':'Unavailable private names in export scope are not source absence. Their declarations remain pinned AST/source evidence;successful full-root library compilation checks that source namespace.'}
(artifacts/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
archive=work/'artifacts.tar.gz'
with tarfile.open(archive,'w:gz')as bundle:
    for item in sorted(artifacts.iterdir()):bundle.add(item,arcname=item.name,recursive=False)
print(json.dumps({'all_checks_pass':receipt['all_checks_pass'],'archive':str(archive),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'receiver_checks':checks,'private_scope_status':body['package_functions']}),flush=True)
