"""Owned single-file publication experiment; no production changes or job replay."""
from pathlib import Path
import hashlib,json,os,stat,sys
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
protocol=json.loads((P/'atomic-publication-process-protocol-v1.json').read_text())
source=ROOT/protocol['production_source']['path']
assert hashlib.sha256(source.read_bytes()).hexdigest()==protocol['production_source']['sha256']
variant,phase,folder_text,tag=sys.argv[1:]
folder=Path(folder_text).resolve()
assert folder.is_relative_to(P/'atomic-publication-process-v1')
payload=json.dumps({'owned_marker':tag,'body':protocol['body_text']},sort_keys=True,separators=(',',':')).encode()+b'\n'
original_write,original_fsync=os.write,os.fsync

def observed_write(fd,data):
 if phase=='before_write':os._exit(91)
 if phase=='mid_write':
  original_write(fd,bytes(data)[:len(data)//2]);os._exit(91)
 return original_write(fd,data)

def observed_fsync(fd):
 original_fsync(fd)
 mode=os.fstat(fd).st_mode
 if phase=='after_file_fsync'and stat.S_ISREG(mode):os._exit(91)
 if phase=='after_parent_fsync'and stat.S_ISDIR(mode):os._exit(91)

os.write,os.fsync=observed_write,observed_fsync
try:
 if variant=='current_workspace':
  sys.path.insert(0,str(ROOT/'agent/tools'))
  import documentation_workspace as workspace
  with workspace.directory(folder)as root_fd:workspace.write_new(root_fd,'artifact.json',payload)
 elif variant=='owned_stage_link':
  # Fixed owned canonical directory, same filesystem; no hostile name replacement model.
  root_fd=os.open(folder,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
  stage='stage-'+tag+'.json'
  try:
   fd=os.open(stage,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=root_fd)
   try:
    view=memoryview(payload)
    while view:
     count=os.write(fd,view)
     if not count:raise RuntimeError('short write')
     view=view[count:]
    os.fsync(fd)
   finally:os.close(fd)
   # Existing final file/symlink causes EEXIST; never os.replace or unlink.
   os.link(stage,'artifact.json',src_dir_fd=root_fd,dst_dir_fd=root_fd,follow_symlinks=False)
   if phase=='after_link':os._exit(91)
   os.fsync(root_fd)
   # Preserve staging evidence, including loser/orphan bytes; no cleanup deletion.
  finally:os.close(root_fd)
 else:raise RuntimeError('unknown frozen variant')
except FileExistsError:
 print(json.dumps({'status':'REFUSED_EXISTING_NAME','variant':variant,'tag':tag}))
 raise SystemExit(17)
print(json.dumps({'status':'PUBLISHED','variant':variant,'tag':tag,'payload_sha256':hashlib.sha256(payload).hexdigest()}))
