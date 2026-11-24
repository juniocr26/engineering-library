"""Preserve exact existing compiler inputs, without installation or runtime changes."""
import datetime,gzip,hashlib,io,json,subprocess,tarfile
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];prior=json.loads((P/'javascript-queue-type-consumers-v1.json').read_text());assert prior['typescript_version']=='5.9.3'
compiler_root='/app/frontend/node_modules/typescript';selected=['package.json','LICENSE.txt','ThirdPartyNoticeText.txt','lib/typescript.js']+[path.removeprefix(compiler_root+'/')for path in prior['standard_library_files']]
assert len(selected)==len(set(selected))and all(not name.startswith('/')and'..'not in Path(name).parts for name in selected)
program="""const fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');const names=JSON.parse(fs.readFileSync(0,'utf8'));const root=path.dirname(require.resolve('typescript/package.json'));const rows=names.map(name=>{const p=path.join(root,name);const stat=fs.lstatSync(p);if(!stat.isFile()||stat.isSymbolicLink()||stat.size>16*1024*1024)throw Error('unsafe installed compiler input');const raw=fs.readFileSync(p);return {path:name,bytes:raw.length,sha256:crypto.createHash('sha256').update(raw).digest('hex')}});process.stdout.write(JSON.stringify({root,compiler:require.resolve('typescript'),version:require('typescript').version,node:process.version,arch:process.arch,platform:process.platform,files:rows}));"""
r=subprocess.run(['docker','exec','-i','-e','NODE_PATH=/app/frontend/node_modules','engineering-library-frontend-1','node','-e',program],input=json.dumps(selected).encode(),capture_output=True,timeout=20);assert r.returncode==0,r.stderr.decode();metadata=json.loads(r.stdout);assert metadata['root']==compiler_root and metadata['version']=='5.9.3'
for row in metadata['files']:
 absolute=compiler_root+'/'+row['path']
 if absolute in prior['standard_library_files']:assert row['sha256']==prior['standard_library_files'][absolute]['sha256']
parser_hash=json.loads((P/'javascript-evaluation-scope-v3.json').read_text())['rows'][0]['result'].get('producer',{}).get('parser_sha256')
# First adverse row is refused before producer output; use an accepted owned row if needed.
if not parser_hash:
 for row in json.loads((P/'javascript-evaluation-scope-v3.json').read_text())['rows']:
  if row['result'].get('producer'):parser_hash=row['result']['producer']['parser_sha256'];break
assert next(row['sha256']for row in metadata['files']if row['path']=='lib/typescript.js')==parser_hash
result=subprocess.run(['docker','exec','engineering-library-frontend-1','tar','-C',compiler_root,'-cf','-',*selected],capture_output=True,timeout=30);assert result.returncode==0,result.stderr.decode();tar_bytes=result.stdout
store=ROOT/'.local-backups/continuation-20261120/typescript-5.9.3-selected-closure-v1';store.mkdir(exist_ok=False);archive=store/'compiler-and-selected-standard-libraries.tar.gz'
with archive.open('xb')as output:
 with gzip.GzipFile(fileobj=output,mode='wb',mtime=0)as zipped:zipped.write(tar_bytes)
expected={row['path']:row for row in metadata['files']}
with tarfile.open(archive,'r:gz')as tar:
 members=tar.getmembers();assert len(members)==len(expected)and{m.name for m in members}==set(expected)
 for member in members:
  assert member.isfile()and not member.name.startswith('/')and'..'not in Path(member.name).parts
  raw=tar.extractfile(member).read();row=expected[member.name];assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['sha256']
image=subprocess.run(['docker','inspect','--format','{{.Id}} {{.Image}}','engineering-library-frontend-1'],capture_output=True,text=True,timeout=10);assert image.returncode==0
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archive':str(archive.relative_to(ROOT)),'archive_bytes':archive.stat().st_size,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'installed_source':metadata,'container_and_image_id':image.stdout.strip(),'all_member_hashes_verified':True,'typescript_standard_library_files':57,'total_files':len(expected),'dependency_installation':False,'container_changed':False,'model_weights_copied':False,'runtime_binary_preserved':False,'full_runtime_or_cold_boot_reproducibility_claimed':False,'scope':'Exact existing pure-JS compiler,57selectedstandardlibrarydeclarations,packageandlegalnotices. This is an artifact copy, not a new tool installation or complete TypeScript distribution.'}
with(P/'typescript-selected-closure-preservation-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'files':len(expected),'archive_bytes':archive.stat().st_size,'sha256':record['archive_sha256'],'compiler_matches_original_observer':True})
