"""Offline package archive and static export-data method-set verification."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

P=Path('/sources/engineering-library/agent/research/continuation-20261120')
provenance=json.loads((P/'go-geom-root-package-provenance-v1.json').read_text())
base=P/'new-public-sources-v1/twpayne--go-geom'/provenance['revision']
toolchain=Path('/sources/engineering-library/.local-backups/continuation-20261119/cached-go-toolchain')
if hashlib.sha256((toolchain/'bin/go').read_bytes()).hexdigest()!='59c65090beeda377c09007eb8fae1c6aadf0a7b551e65ee13d461092d29e8005':raise ValueError('compiler identity changed')
work=Path('/tmp/el-cont-20261120-go-geom-static-v1');work.mkdir(exist_ok=False)
source=work/'source';source.mkdir();artifacts=work/'artifacts';artifacts.mkdir()
before={}
for entry in provenance['rows']:
    if entry['status']!='verified':raise ValueError('incomplete source closure')
    raw=(base/entry['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=entry['sha256']:raise ValueError('frozen source drift')
    before[entry['path']]=entry['sha256'];(source/entry['path']).write_bytes(raw)
env=dict(os.environ,GOROOT=str(toolchain),GOENV='off',GOTOOLCHAIN='local',GO111MODULE='on',GOWORK='off',GOPROXY='off',GOSUMDB='off',GOFLAGS='',CGO_ENABLED='0',GOOS='linux',GOARCH='arm64',GOPATH=str(work/'gopath'),GOMODCACHE=str(work/'modcache'),GOCACHE='/tmp/el-cont-20261120-build-context-v2/cache',GOMAXPROCS='2',GOMEMLIMIT='512MiB',GOTELEMETRY='off')
go=str(toolchain/'bin/go');commands=[]

def run(label,command,cwd,command_env=env):
    started=time.monotonic();r=subprocess.run(command,env=command_env,cwd=cwd,capture_output=True,timeout=180)
    (artifacts/(label+'.stdout')).write_bytes(r.stdout);(artifacts/(label+'.stderr')).write_bytes(r.stderr)
    row={'label':label,'command':command,'exit_code':r.returncode,'seconds':time.monotonic()-started};commands.append(row)
    (artifacts/'commands-progress.json').write_text(json.dumps(commands,indent=2)+'\n')
    if r.returncode:raise RuntimeError(label+' failed;all raw evidence retained,no network fallback')
    return r

archive=artifacts/'geom-package.a'
run('package-build',[go,'build','-p','1','-mod=readonly','-trimpath','-buildvcs=false','-o',str(archive),'.'],source)
listed=run('package-export-list',[go,'list','-mod=readonly','-trimpath','-buildvcs=false','-deps','-export','-json','.'],source)
text=listed.stdout.decode();decoder=json.JSONDecoder();packages=[]
while text.strip():
    text=text.lstrip();item,end=decoder.raw_decode(text);packages.append(item);text=text[end:]
exports={item['ImportPath']:item['Export']for item in packages if item.get('Export')}
subject='github.com/twpayne/go-geom'
if subject not in exports:raise ValueError('subject export missing')
exports[subject]=str(archive)
for name,path in exports.items():
    if not Path(path).is_file()or not path.startswith(('/tmp/el-cont-20261120-build-context-v2/cache/',str(artifacts)+'/')):raise ValueError('export path outside explicit owned compile storage')
export_map=artifacts/'exports-map.json';export_map.write_text(json.dumps({'package':subject,'exports':exports},indent=2)+'\n')
inspector_source=P/'go-package-method-set-v1/main.go';formatted=run('inspector-format',[str(toolchain/'bin/gofmt'),str(inspector_source)],work).stdout
(artifacts/'method-set.formatted.go').write_bytes(formatted)
inspector=artifacts/'method-set-linux-arm64';inspector_env=dict(env,GO111MODULE='off')
run('inspector-build',[go,'build','-p','1','-trimpath','-buildvcs=false','-o',str(inspector),str(artifacts/'method-set.formatted.go')],work,inspector_env)
observed=run('static-method-set',[str(inspector),str(export_map)],work)
result=json.loads(observed.stdout)
expected={'setCoords':'*geom.geom0','SetCoords':'*geom.Point','Coords':'*geom.geom0','FlatCoords':'*geom.geom0','Clone':'*geom.Point','SetSRID':'*geom.Point','MustSetCoords':'*geom.Point'}
checks={item['name']:item['declaring_receiver']==expected[item['name']]for item in result['point_methods']}
unchanged=all(hashlib.sha256((base/name).read_bytes()).hexdigest()==digest and hashlib.sha256((source/name).read_bytes()).hexdigest()==digest for name,digest in before.items())
receipt={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'revision':provenance['revision'],'commands':commands,'source_hashes':before,
         'source_original_and_copy_unchanged':unchanged,'package_archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
         'method_set_observation':result,'declaring_receiver_checks':checks,'all_checks_pass':all(checks.values())and unchanged,
         'compile_context':{'toolchain':'go1.27.4','goos':'linux','goarch':'arm64','cgo':False,'module_mode':True,'downloads_disabled':True},
         'public_library_compiled':True,'public_library_executed':False,'public_tests_or_generator_executed':False,
         'owned_metadata_reader_executed':True,'runtime_mutation_or_concurrency_tested':False,'new_model_calls':0,
         'limit':'Static selected frozen tracked root package only;not an arbitrary deployment/untracked-file closure or runtime behavior measurement.'}
(artifacts/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
import tarfile
bundle_path=work/'artifacts.tar.gz'
with tarfile.open(bundle_path,'w:gz')as bundle:
    for item in sorted(artifacts.iterdir()):bundle.add(item,arcname=item.name,recursive=False)
print(json.dumps({'all_checks_pass':receipt['all_checks_pass'],'archive':str(bundle_path),'archive_sha256':hashlib.sha256(bundle_path.read_bytes()).hexdigest(),'methods':checks,'public_library_executed':False}),flush=True)
