"""Archive finite owned physical inputs without following synthetic symlinks."""
import datetime,hashlib,json,os,stat,tarfile
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
roots=[Path('/private/tmp')/name for name in ['el-registered-helper-binding-20261120-v1','el-registered-helper-binding-20261120-v2','el-registered-helper-binding-20261120-v3','el-helper-final-gate-leaf-20261120-v1','el-helper-final-gate-leaf-20261120-v2']]
rows=[];links=[];dest=ROOT/'.local-backups/continuation-20261120/helper-grammar-physical-inputs-v1';dest.mkdir(exist_ok=False);archive=dest/'owned-physical-inputs.tar.gz'
with tarfile.open(archive,'w:gz')as tar:
 for root in roots:
  assert root.is_dir()and not root.is_symlink()
  for directory,dirs,files in os.walk(root,followlinks=False):
   base=Path(directory)
   for name in dirs+files:
    f=base/name;mode=f.lstat().st_mode;relative=str(Path(root.name)/f.relative_to(root))
    if stat.S_ISLNK(mode):links.append({'path':relative,'target':os.readlink(f),'followed':False})
    elif stat.S_ISREG(mode):
     raw=f.read_bytes();tar.add(f,arcname=relative,recursive=False);rows.append({'path':relative,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    elif not stat.S_ISDIR(mode):raise ValueError('unexpected special owned input')
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archive':str(archive.relative_to(ROOT)),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'archive_bytes':archive.stat().st_size,'regular_files':rows,'synthetic_symlinks_metadata_only':links,'source_is_owned_fixture_not_external_application':True,'source_executed':False,'training_excluded':True}
with(P/'helper-grammar-physical-inputs-preservation-v1.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'regular_files':len(rows),'synthetic_symlinks':len(links),'archive_bytes':r['archive_bytes']})
