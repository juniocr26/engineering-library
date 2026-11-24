"""Owned worker: terminate itself at exactly one real persistence boundary."""
import os,signal,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'agent/tools'));import documentation_maintenance as m
spec=m.read_specification(sys.argv[1]);original=m.write_new

def interrupted(fd,name,data,metadata=None):
 original(fd,name,data,metadata)
 if name=='active/en/guide.md':os.kill(os.getpid(),signal.SIGKILL)
m.write_new=interrupted
m.build(spec,prepare=True)
raise RuntimeError('fault boundary was not reached')
