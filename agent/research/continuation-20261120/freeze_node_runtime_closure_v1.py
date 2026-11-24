"""Inventory existing public runtime bytes only; never copy application/image data."""
import datetime,json,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent
program=r'''
const fs=require('node:fs'),crypto=require('node:crypto');const names=[process.execPath,'/usr/local/LICENSE','/usr/local/share/doc/node/LICENSE','/usr/share/doc/nodejs/copyright','/usr/share/doc/libc6/copyright','/usr/share/doc/libstdc++6/copyright','/usr/share/doc/libgcc-s1/copyright','/usr/share/doc/zlib1g/copyright'];const rows=[];
for(const name of names){try{const real=fs.realpathSync(name),stat=fs.lstatSync(real);if(!stat.isFile()||stat.size>192*1024*1024)throw Error('nonregular/oversize');const raw=fs.readFileSync(real);rows.push({path:name,realpath:real,bytes:raw.length,mode:stat.mode&511,sha256:crypto.createHash('sha256').update(raw).digest('hex')})}catch(error){rows.push({path:name,unavailable:true,reason:error.code||error.message})}}
console.log(JSON.stringify({node:process.version,executable:process.execPath,platform:process.platform,arch:process.arch,versions:process.versions,files:rows}));
'''
r=subprocess.run(['docker','exec','engineering-library-frontend-1','node','-e',program],capture_output=True,text=True,timeout=30);assert r.returncode==0,r.stderr;metadata=json.loads(r.stdout);assert metadata['node']=='v24.22.0'and metadata['platform']=='linux'and metadata['arch']=='arm64'
ldd=subprocess.run(['docker','exec','engineering-library-frontend-1','ldd',metadata['executable']],capture_output=True,text=True,timeout=15);(P/'node-runtime-ldd-v1.stdout').write_text(ldd.stdout);(P/'node-runtime-ldd-v1.stderr').write_text(ldd.stderr);assert ldd.returncode==0,ldd.stderr
libraries=[]
for line in ldd.stdout.splitlines():
 parts=line.strip().split()
 if len(parts)>=3 and parts[1]=='=>'and parts[2].startswith('/'):libraries.append({'soname':parts[0],'path':parts[2]})
 elif parts and parts[0].startswith('/'):libraries.append({'soname':Path(parts[0]).name,'path':parts[0],'dynamic_loader':True})
assert libraries and any(e.get('dynamic_loader')for e in libraries)
program=r'''
const fs=require('node:fs'),crypto=require('node:crypto');const entries=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify(entries.map(e=>{const real=fs.realpathSync(e.path),stat=fs.lstatSync(real);if(!stat.isFile()||stat.size>32*1024*1024)throw Error('library bound');const raw=fs.readFileSync(real);return {...e,realpath:real,bytes:raw.length,mode:stat.mode&511,sha256:crypto.createHash('sha256').update(raw).digest('hex')}})));
'''
r=subprocess.run(['docker','exec','-i','engineering-library-frontend-1','node','-e',program],input=json.dumps(libraries),capture_output=True,text=True,timeout=20);assert r.returncode==0,r.stderr;libraries=json.loads(r.stdout)
files=[]
node_entry=next(e for e in metadata['files']if e['path']==metadata['executable']);files.append({**node_entry,'archive_path':'bin/node','kind':'node-executable'})
for e in libraries:files.append({**e,'archive_path':'lib/'+e['soname'],'kind':'dynamic-loader'if e.get('dynamic_loader')else'shared-library'})
for index,e in enumerate(metadata['files']):
 if e['path']==metadata['executable']or e.get('unavailable'):continue
 files.append({**e,'archive_path':'legal/'+str(index)+'-'+Path(e['path']).parent.name+'-'+Path(e['path']).name,'kind':'legal-notice'})
assert len({e['archive_path']for e in files})==len(files)and any(e['kind']=='legal-notice'and e['path']=='/usr/local/LICENSE'for e in files)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'purpose':'Preserve alreadyinstalledNode24.22.0LinuxARM64executable,observedlddsharedlibrary/loaderclosureandavailablelegalnotices for isolated replay;noapplication/image/model/private-dataexport.','runtime_metadata':metadata,'files':files,'total_uncompressed_bytes':sum(e['bytes']for e in files),'source_execution_allowed_in_followup':'OnlycopiedtrustedNode/loaderbinaries plusownedhash/version/typecheckprograms;noinspectedapplicationorprivateprojectcode.','archive_not_created_yet':True,'dependencies_or_weights_downloaded':False,'package_manager_installation':False,'global_runtime_replaced':False,'model_calls':0,'training_steps':0,'limits':['Observeduser-spaceloadersupportsfutureboundedreplay,notallNodefeaturesorplugins.','Kernelfiles,vDSO,locale,DNS,certificatestores,addonsandcontainerbasearenotclaimedfullyarchived.','LinuxARM64only;notamacOS/Windowsruntimeorfullcoldboot/remoteproof.']}
with(P/'node-runtime-closure-freeze-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'files':len(files),'libraries_and_loader':len(libraries),'bytes':record['total_uncompressed_bytes'],'node':metadata['node'],'archive_created':False})
