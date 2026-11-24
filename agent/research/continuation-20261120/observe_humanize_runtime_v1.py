"""Run reviewed Go source in existing container; no source rewriting or downloads."""
import datetime,hashlib,json,os,subprocess,time,tarfile
from pathlib import Path
P=Path('/sources/engineering-library/agent/research/continuation-20261120')
protocol=json.loads((P/'humanize-confined-runtime-protocol-v1.json').read_text());fetch=json.loads((P/'humanize-source-fetch-v1.json').read_text());toolchain=Path('/sources/engineering-library/.local-backups/continuation-20261119/cached-go-toolchain')
assert hashlib.sha256((toolchain/'bin/go').read_bytes()).hexdigest()=='59c65090beeda377c09007eb8fae1c6aadf0a7b551e65ee13d461092d29e8005'
work=Path('/tmp/el-humanize-confined-runtime-20261120-v1');work.mkdir(exist_ok=False);artifacts=work/'artifacts';artifacts.mkdir();commands=[];results=[]
baseenv=dict(os.environ,GOROOT=str(toolchain),GOENV='off',GOTOOLCHAIN='local',GO111MODULE='off',GOWORK='off',GOPROXY='off',GOSUMDB='off',GOFLAGS='',CGO_ENABLED='0',GOOS='linux',GOARCH='arm64',GOCACHE='/tmp/el-cont-20261120-build-context-v2/cache',GOMAXPROCS='2',GOMEMLIMIT='512MiB',GOTELEMETRY='off',GOMODCACHE=str(work/'unused-modcache'))
def run(label,args,env,timeout):
 start=time.monotonic();r=subprocess.run(args,cwd=work,env=env,capture_output=True,timeout=timeout)
 (artifacts/(label+'.stdout')).write_bytes(r.stdout);(artifacts/(label+'.stderr')).write_bytes(r.stderr);commands.append({'label':label,'command':args,'exit_code':r.returncode,'seconds':time.monotonic()-start});(artifacts/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
 if r.returncode:raise ValueError(label+' failed; raw evidence retained')
 return r
for cut in protocol['cuts']:
 tag=cut['tag'];gp=work/tag/'gopath';source=gp/'src/github.com/dustin/go-humanize';source.mkdir(parents=True);identities={}
 for entry in fetch['files']:
  if entry['tag']!=tag:continue
  raw=(P/entry['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['sha256'];name=Path(entry['path']).name;(source/name).write_bytes(raw);identities[name]=entry['sha256']
 env=dict(baseenv,GOPATH=str(gp));binary=artifacts/('humanize-'+tag)
 run(tag+'-build',[str(toolchain/'bin/go'),'build','-p','1','-trimpath','-buildvcs=false','-o',str(binary),str(P/'humanize-runtime-driver-v1/main.go')],env,180)
 output=run(tag+'-observe',[str(binary),str(P/'humanize-confined-runtime-protocol-v1.json')],env,20);rows=json.loads(output.stdout);expected={c['id']:c['expected'][tag]for c in protocol['cases']};assert len(rows)==len(expected)and len({r['id']for r in rows})==len(rows)
 for row in rows:row['expected']=expected[row['id']];row['pass']=row['observed']==row['expected']
 unchanged=all(hashlib.sha256((source/name).read_bytes()).hexdigest()==sha for name,sha in identities.items())
 results.append({'tag':tag,'revision':cut['revision'],'rows':rows,'passes':sum(r['pass']for r in rows),'cases':len(rows),'copied_sources_unchanged':unchanged,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest()})
receipt={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':results,'commands':commands,'source_package_initializers_executed':True,'source_functions_executed':True,'upstream_tests_executed':False,'source_edited':False,'downloads':False,'context':{'go':'1.27.4','os':'linux','arch':'arm64','cgo':False},'distinct_frozen_cases':len(protocol['cases']),'revisions':len(results),'not_independent_lifecycle_accuracy':True,'training_excluded':True,'owner_approved':False,'model_calls':0}
(artifacts/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
archive=work/'artifacts.tar.gz'
with tarfile.open(archive,'w:gz')as tar:
 for f in sorted(artifacts.iterdir()):tar.add(f,arcname=f.name,recursive=False)
print(json.dumps({'archive':str(archive),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'results':[{k:r[k]for k in ['tag','passes','cases','copied_sources_unchanged']}for r in results]}))
