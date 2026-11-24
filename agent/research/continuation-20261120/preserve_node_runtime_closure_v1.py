"""Copy exact existing public runtime bytes into local preservation, never install."""
import datetime,gzip,hashlib,io,json,subprocess,tarfile
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];freeze_path=P/'node-runtime-closure-freeze-v1.json';freeze=json.loads(freeze_path.read_text());files=freeze['files'];names=sorted({e['realpath'].lstrip('/')for e in files});assert all(name and'..'not in Path(name).parts for name in names)
r=subprocess.run(['docker','exec','engineering-library-frontend-1','tar','--hard-dereference','-C','/','-cf','-',*names],capture_output=True,timeout=45);assert r.returncode==0,r.stderr.decode();assert len(r.stdout)<=freeze['total_uncompressed_bytes']+131072
bodies={}
with tarfile.open(fileobj=io.BytesIO(r.stdout),mode='r:')as tar:
 members=tar.getmembers();assert {m.name for m in members}==set(names)
 for member in members:
  assert member.isfile()and not member.name.startswith('/')and'..'not in Path(member.name).parts;body=tar.extractfile(member).read();expected=[e for e in files if e['realpath'].lstrip('/')==member.name];assert expected and all(hashlib.sha256(body).hexdigest()==e['sha256']and len(body)==e['bytes']for e in expected);bodies[member.name]=body
store=ROOT/'.local-backups/continuation-20261120/node-24.22.0-linux-arm64-selected-closure-v1';store.mkdir(exist_ok=False);archive=store/'node-loader-libraries-and-notices.tar.gz'
with archive.open('xb')as raw:
 with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0)as zipped:
  with tarfile.open(fileobj=zipped,mode='w')as tar:
   for e in files:
    body=bodies[e['realpath'].lstrip('/')];info=tarfile.TarInfo(e['archive_path']);info.size=len(body);info.mode=e['mode']&0o777;info.mtime=0;tar.addfile(info,io.BytesIO(body))
with tarfile.open(archive,'r:gz')as tar:
 members=tar.getmembers();expected={e['archive_path']:e for e in files};assert len(members)==len(expected)
 for member in members:
  assert member.isfile()and member.name in expected;entry=expected[member.name];body=tar.extractfile(member).read();assert hashlib.sha256(body).hexdigest()==entry['sha256']and len(body)==entry['bytes']
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'freeze_sha256':hashlib.sha256(freeze_path.read_bytes()).hexdigest(),'archive':str(archive.relative_to(ROOT)),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'archive_bytes':archive.stat().st_size,'entries':files,'all_input_and_archive_member_hashes_verified':True,'symlinks_or_hardlinks_in_archive':False,'member_mtime_normalized_zero_not_campaign_time':True,'node_version':'v24.22.0','platform':'LinuxARM64','original_runtime_or_system_files_changed':False,'application_or_model_or_private_data_copied':False,'package_manager_installation':False,'remote_upload':False,'cold_boot_or_complete_os_recovery_claimed':False,'scope':'SelectedtrustedNodeexecutable,sevenobservedlddsharedlibrary/loaderfilesandfivelegalnoticeentries. Kernel/vDSOanddynamicfeaturedataremainoutsideclosure.'}
with(P/'node-runtime-selected-closure-preservation-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'files':len(files),'archive_bytes':archive.stat().st_size,'sha256':record['archive_sha256'],'installed_runtime_changed':False})
