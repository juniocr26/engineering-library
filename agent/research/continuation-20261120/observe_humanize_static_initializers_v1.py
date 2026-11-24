"""Offline complete-source type check; reuse frozen source copies and compiled stdlib exports."""
import datetime,hashlib,json,os,subprocess,tarfile,time
from pathlib import Path
P=Path('/sources/engineering-library/agent/research/continuation-20261120');protocol=json.loads((P/'humanize-static-initializer-protocol-v1.json').read_text());fetch=json.loads((P/'humanize-source-fetch-v1.json').read_text());tc=Path('/sources/engineering-library/.local-backups/continuation-20261119/cached-go-toolchain');assert hashlib.sha256((tc/'bin/go').read_bytes()).hexdigest()=='59c65090beeda377c09007eb8fae1c6aadf0a7b551e65ee13d461092d29e8005'
work=Path('/tmp/el-humanize-static-initializers-20261120-v1');work.mkdir(exist_ok=False);out=work/'artifacts';out.mkdir();prior=Path('/tmp/el-humanize-confined-runtime-20261120-v1');commands=[];results=[];reader=P/'go-initializer-reader-v1/main.go';assert hashlib.sha256(reader.read_bytes()).hexdigest()==protocol['reader_sha256']
env=dict(os.environ,GOROOT=str(tc),GOENV='off',GOTOOLCHAIN='local',GO111MODULE='off',GOWORK='off',GOPROXY='off',GOSUMDB='off',GOFLAGS='',CGO_ENABLED='0',GOOS='linux',GOARCH='arm64',GOCACHE='/tmp/el-cont-20261120-build-context-v2/cache',GOMAXPROCS='2',GOMEMLIMIT='512MiB',GOTELEMETRY='off',GOPATH=str(work/'unused-gopath'))
def run(label,args,cwd=work,environ=env):
 start=time.monotonic();r=subprocess.run(args,env=environ,cwd=cwd,capture_output=True,timeout=180);(out/(label+'.stdout')).write_bytes(r.stdout);(out/(label+'.stderr')).write_bytes(r.stderr);commands.append({'label':label,'command':args,'exit':r.returncode,'seconds':time.monotonic()-start});(out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
 if r.returncode:raise ValueError(label+' failed; raw evidence retained')
 return r
binary=out/'go-initializer-reader-linux-arm64';run('build-owned-reader',[str(tc/'bin/go'),'build','-p','1','-trimpath','-buildvcs=false','-o',str(binary),str(reader)])
for tag in ['v1.0.0','v1.0.1']:
 gp=prior/tag/'gopath';source=gp/'src/github.com/dustin/go-humanize';entries=[e for e in fetch['files']if e['tag']==tag];before={Path(e['path']).name:e['sha256']for e in entries}
 assert all(hashlib.sha256((source/name).read_bytes()).hexdigest()==sha for name,sha in before.items())
 listed=run(tag+'-exports',[str(tc/'bin/go'),'list','-p','1','-deps','-export','-json','.'],source,dict(env,GOPATH=str(gp)));decoder=json.JSONDecoder();text=listed.stdout.decode();packages=[]
 while text.strip():
  text=text.lstrip();row,end=decoder.raw_decode(text);packages.append(row);text=text[end:]
 subject=[x for x in packages if x['ImportPath']=='github.com/dustin/go-humanize'];assert len(subject)==1;subject=subject[0];files=[str(source/name)for name in subject['GoFiles']];assert set(Path(f).name for f in files)=={name for name in before if name.endswith('.go')}
 exports={x['ImportPath']:x['Export']for x in packages if x.get('Export')and x['ImportPath']!='github.com/dustin/go-humanize'}
 assert all(Path(path).is_file()and path.startswith('/tmp/el-cont-20261120-build-context-v2/cache/')for path in exports.values())
 request={'package':'github.com/dustin/go-humanize','files':files,'exports':exports};req=out/(tag+'-request.json');req.write_text(json.dumps(request,indent=2)+'\n');observation=json.loads(run(tag+'-static-reader',[str(binary),str(req)]).stdout);assert observation['subject_source_executed']is False
 constants={r['name']:r for r in observation['constants']};variables={r['name']:r for r in observation['variables']};functions={r['name']:r for r in observation['functions']};maps={r['name']:r for r in observation['map_initializers']};checks=[]
 for case in protocol['cases']:
  kind=case['kind'];value=None
  if kind=='constant':value=constants.get(case['name'],{}).get('exact_constant_value')
  elif kind=='variable-type':value=variables.get(case['name'],{}).get('type')
  elif kind=='function-type':value=functions.get(case['name'],{}).get('type')
  elif kind=='map-initializer':
   matches=[x for x in maps[case['table']]['entries']if x['key_constant']==case['key']];assert len(matches)<=1;value=matches[0]['value_source']if matches else None
  elif kind=='init-count':value=len(observation['explicit_initializers'])
  else:raise ValueError('unexpected frozen check')
  expected=case['expected'][tag];checks.append({'id':case['id'],'expected':expected,'observed':value,'pass':value==expected})
 unchanged=all(hashlib.sha256((source/name).read_bytes()).hexdigest()==sha for name,sha in before.items())
 results.append({'tag':tag,'observation':observation,'checks':checks,'passes':sum(x['pass']for x in checks),'cases':len(checks),'source_copies_unchanged':unchanged,'compiled_export_hashes':{name:hashlib.sha256(Path(path).read_bytes()).hexdigest()for name,path in exports.items()}})
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':results,'commands':commands,'reader_binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'distinct_frozen_checks':len(protocol['cases']),'subject_source_executed':False,'subject_initializers_executed_in_this_followup':False,'owned_type_reader_executed':True,'downloads':False,'training_excluded':True,'owner_approved':False,'not_general_runtime_map_or_mutability_proof':True}
(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');archive=work/'artifacts.tar.gz'
with tarfile.open(archive,'w:gz')as tar:
 for f in sorted(out.iterdir()):tar.add(f,arcname=f.name,recursive=False)
print(json.dumps({'archive':str(archive),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'results':[{k:x[k]for k in ['tag','passes','cases','source_copies_unchanged']}for x in results]}))
