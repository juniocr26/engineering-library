"""Closed owned architecture syntax pack with complete bounded inline sources."""
import ast,hashlib,importlib.util
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('architecture_previous_observer',P.parent/'documentation-intelligence-20261120/assemble_architecture_facts_v2.py')
previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
PREVIOUS_SHA=hashlib.sha256(Path(previous.__file__).read_bytes()).hexdigest()
OWN_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
FILES=previous.FILES;SOURCE=previous.SOURCE

def extract(sources):
 if hashlib.sha256(Path(previous.__file__).read_bytes()).hexdigest()!=PREVIOUS_SHA or hashlib.sha256(Path(__file__).read_bytes()).hexdigest()!=OWN_SHA:raise ValueError('loaded architecture observer changed; reload required')
 for name,raw in sources.items():
  if type(raw)is not bytes or len(raw)>16384:raise ValueError('closed source size/type bound')
  tree=ast.parse(raw.decode('utf-8'))
  if sum(1 for _ in ast.walk(tree))>4096:raise ValueError('closed architecture node bound')
  compile(tree,name,'exec')
 pack=previous.extract(sources)
 pack['architecture_observer_v3']={'version':'0.0.3-research','producer_sha256':OWN_SHA,'previous_observer_sha256':PREVIOUS_SHA,'source_executed':False,'sources':{n:b.decode('utf-8')for n,b in sources.items()}}
 return pack
