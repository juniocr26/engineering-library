"""Version/flag-specific Git-source package fixture observations; no npm install."""
import datetime,hashlib,io,json,subprocess,tarfile,time
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];protocol_path=P/'javascript-package-format-protocol-v1.json';protocol=json.loads(protocol_path.read_text());archive=P/'javascript-package-format-source-fixtures-v1.tar.gz';entries=[]
old_revisions={'e316fac4e7aeede98beeb87e3a7de4ffc3d8eebf','af91c37f51aecf607ca2261b907b9d86b6a69e77'};current_revisions={'38a6773e552d24f4c9eb2d79d57b6cff017c587d','2e57f8c95e5e1f40379c6f85d18aee962662eb22'}
with tarfile.open(archive,'w:gz')as tar:
 for entry in protocol['source_files']:
  raw=(P/entry['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['sha256'];assert entry['revision']in old_revisions|current_revisions
  group='old'if entry['revision']in old_revisions else'current';name=group+'/node_modules/'+entry['repository'].split('/')[-1]+'/'+Path(entry['path']).name;info=tarfile.TarInfo(name);info.size=len(raw);info.mode=0o600;info.mtime=0;tar.addfile(info,io.BytesIO(raw));entries.append({'path':name,'source_path':entry['path'],'sha256':entry['sha256'],'bytes':len(raw)})
with tarfile.open(archive,'r:gz')as tar:
 members=tar.getmembers();assert len(members)==16
 for member in members:assert member.isfile()and hashlib.sha256(tar.extractfile(member).read()).hexdigest()==next(e['sha256']for e in entries if e['path']==member.name)
remote='/tmp/el-git-source-package-format-20261120-v1'
def docker(args,**kwargs):
 r=subprocess.run(['docker','exec',*args],capture_output=True,timeout=30,**kwargs);assert r.returncode==0,r.stderr.decode();return r
start=time.monotonic();docker(['engineering-library-frontend-1','mkdir',remote]);docker(['engineering-library-frontend-1','tar','--no-same-owner','-xzf','/sources/engineering-library/'+str(archive.relative_to(ROOT)),'-C',remote])
hasher="const fs=require('node:fs'),crypto=require('node:crypto');const data=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify(data.entries.map(e=>({path:e.path,sha256:crypto.createHash('sha256').update(fs.readFileSync(data.root+'/'+e.path)).digest('hex')}))));"
def hashes():return json.loads(docker(['-i','engineering-library-frontend-1','node','-e',hasher],input=json.dumps({'root':remote,'entries':entries}).encode()).stdout)
before=hashes();assert all(row['sha256']==next(e['sha256']for e in entries if e['path']==row['path'])for row in before)
program=r'''
const path=require('node:path'),{createRequire}=require('node:module');const mode=process.argv[1];
(async()=>{
 const base=process.cwd();const limiterPath=require.resolve('p-limit');const queuePath=createRequire(limiterPath).resolve('yocto-queue');if(!limiterPath.startsWith(base+'/node_modules/p-limit/')||!queuePath.startsWith(base+'/node_modules/yocto-queue/'))throw Error('module graph escaped owned fixture');
 const common={node:process.version,requireModuleFeature:process.features.require_module,limiterPath,queuePath,mode};
 try{
  if(mode==='require-shape'){
   const raw=require('p-limit');console.log(JSON.stringify({...common,kind:'shape',raw_type:typeof raw,default_type:typeof raw.default}));return;
  }
  let factory;
  if(mode.startsWith('dynamic-import'))factory=(await import('p-limit')).default;
  else {const raw=require('p-limit');factory=mode==='require-call-default'?raw.default:raw;}
  const limit=factory(1);const value=await limit(n=>n+1,6);console.log(JSON.stringify({...common,kind:'value',value}));
 }catch(error){console.log(JSON.stringify({...common,kind:'error',name:error.name,code:error.code||null,message:error.message}));}
})().catch(error=>{console.error(error.stack);process.exitCode=1});
'''
rows=[]
for case in protocol['cases']:
 args=['-w',remote+'/'+case['version_group'],'engineering-library-frontend-1','node']
 if case['disable_require_interop']:args.append(protocol['disable_flag'])
 args+=['-e',program,case['mode']]
 r=subprocess.run(['docker','exec',*args],capture_output=True,text=True,timeout=10);observed=json.loads(r.stdout)if r.returncode==0 else{'process_error':r.stderr};matched=r.returncode==0 and all(observed.get(key)==value for key,value in case['expected'].items())and observed.get('node')==protocol['exact_node_runtime'].split()[0]
 rows.append({'id':case['id'],'expected':case['expected'],'observed':observed,'matches':matched,'exit_code':r.returncode,'stderr':r.stderr})
after=hashes();assert after==before
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':hashlib.sha256(protocol_path.read_bytes()).hexdigest(),'source_fixture_archive':{'path':str(archive.relative_to(ROOT)),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'entries':entries},'rows':rows,'correct':sum(r['matches']for r in rows),'n':len(rows),'wall_seconds':time.monotonic()-start,'all_materialized_source_hashes_unchanged':True,'owned_temporary_root':remote,'unique_reviewed_source_modules_evaluated_across_cases':4,'source_files_rewritten':False,'installed_dependency_distribution_imported':False,'package_manager_or_environment_install':False,'application_io_or_http':False,'timers_used':False,'new_model_calls':0,'training_steps':0,'owner_approved':False,'limitations':['ExactNode24.22.0LinuxARM64andtwoflagstates;noall-version/platformcompatibilityclaim.','Git-sourcepackagefixturesnotauthenticatednpmtarballsoractualapplicationdependencies.','No sourcechangeclassifieraccuracy,neuralholdoutorpublicationclaim.']}
with(P/'javascript-package-format-results-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'correct':record['correct'],'n':len(rows),'failed':[r['id']for r in rows if not r['matches']],'source_hashes_unchanged':True})
