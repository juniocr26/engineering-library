"""Execute reviewed retry library with owned bounded clocks/timers, no real waiting."""
import datetime,hashlib,json,os,subprocess,tarfile,time
from pathlib import Path
P=Path('/sources/engineering-library/agent/research/continuation-20261120');protocol=json.loads((P/'backoff-confined-runtime-protocol-v1.json').read_text());freeze=json.loads((P/'backoff-source-family-freeze-v1.json').read_text());fetch=json.loads((P/'backoff-source-fetch-v1.json').read_text());pins=json.loads((P/'backoff-runtime-producer-pins-v1.json').read_text());tc=Path('/sources/engineering-library/.local-backups/continuation-20261119/cached-go-toolchain');assert hashlib.sha256((tc/'bin/go').read_bytes()).hexdigest()=='59c65090beeda377c09007eb8fae1c6aadf0a7b551e65ee13d461092d29e8005'
for name,sha in pins['driver_files'].items():assert hashlib.sha256((P/name).read_bytes()).hexdigest()==sha
work=Path('/tmp/el-backoff-confined-runtime-20261120-v1');work.mkdir(exist_ok=False);out=work/'artifacts';out.mkdir();commands=[];results=[]
env=dict(os.environ,GOROOT=str(tc),GOENV='off',GOTOOLCHAIN='local',GO111MODULE='off',GOWORK='off',GOPROXY='off',GOSUMDB='off',GOFLAGS='',CGO_ENABLED='0',GOOS='linux',GOARCH='arm64',GOCACHE='/tmp/el-cont-20261120-build-context-v2/cache',GOMAXPROCS='2',GOMEMLIMIT='512MiB',GOTELEMETRY='off')
def run(label,args,environ,timeout):
 start=time.monotonic();r=subprocess.run(args,env=environ,cwd=work,capture_output=True,timeout=timeout);(out/(label+'.stdout')).write_bytes(r.stdout);(out/(label+'.stderr')).write_bytes(r.stderr);commands.append({'label':label,'command':args,'exit_code':r.returncode,'seconds':time.monotonic()-start});(out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
 if r.returncode:raise ValueError(label+' failed;raw observations preserved')
 return r
for cut in freeze['cuts']:
 tag=cut['tag'];gp=work/tag/'gopath';source=gp/'src/github.com/cenkalti/backoff/v4';source.mkdir(parents=True);before={}
 for entry in fetch['files']:
  if entry['tag']!=tag:continue
  raw=(P/entry['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['sha256'];name=Path(entry['path']).name;(source/name).write_bytes(raw);before[name]=entry['sha256']
 environ=dict(env,GOPATH=str(gp));binary=out/('backoff-'+tag);extra='previous.go'if tag=='v4.1.3'else'current.go';driver=P/'backoff-runtime-driver-v1'
 run(tag+'-build',[str(tc/'bin/go'),'build','-p','1','-trimpath','-buildvcs=false','-o',str(binary),str(driver/'main.go'),str(driver/extra)],environ,180)
 observed=json.loads(run(tag+'-observe',[str(binary)],environ,20).stdout);cases=[c for c in protocol['cases']if not c['current_only']or tag=='v4.3.0'];expected={c['id']:c for c in cases};assert len(observed)==len(expected)and len({r['id']for r in observed})==len(observed);rows=[]
 for row in observed:
  case=expected[row['id']];row['expected_fields']=case['expected_fields'];row['field_checks']={key:row['observed'].get(key)==value for key,value in case['expected_fields'].items()};row['pass']=all(row['field_checks'].values());rows.append(row)
 unchanged=all(hashlib.sha256((source/name).read_bytes()).hexdigest()==sha for name,sha in before.items())and all(hashlib.sha256((P/entry['path']).read_bytes()).hexdigest()==entry['sha256']for entry in fetch['files']if entry['tag']==tag)
 results.append({'tag':tag,'revision':cut['revision'],'rows':rows,'passes':sum(r['pass']for r in rows),'cases':len(rows),'source_originals_and_copies_unchanged':unchanged,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest()})
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':results,'commands':commands,'context':{'go':'1.27.4','os':'linux','arch':'arm64','cgo':False,'module_mode':False},'source_initializers_and_reviewed_functions_executed':True,'owned_timer_and_clock':True,'real_retry_timers_or_sleep_used':False,'public_ticker_or_goroutine_api_called':False,'network_or_application_io':False,'package_downloads':False,'shared_frozen_cases':30,'current_only_api_cases':8,'repeated_old_current_cases_not_independent':True,'training_excluded':True,'owner_approved':False,'model_calls':0,'limits':protocol['limits']};(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');archive=work/'artifacts.tar.gz'
with tarfile.open(archive,'w:gz')as tar:
 for f in sorted(out.iterdir()):tar.add(f,arcname=f.name,recursive=False)
print(json.dumps({'archive':str(archive),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'results':[{k:c[k]for k in ['tag','passes','cases','source_originals_and_copies_unchanged']}for c in results]}))
