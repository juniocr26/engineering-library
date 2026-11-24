"""Reject lexical exception/binding lookalikes outside the reviewed owned shape."""
import ast,hashlib,importlib.util
from pathlib import Path
P=Path(__file__).resolve().parent

def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
observer=load(P/'architecture_fact_observer_v3.py','architecture_closed_observer')
previous=load(P.parent/'documentation-intelligence-20261120/prepare_architecture_claims_v2.py','architecture_previous_compiler')
PREVIOUS_SHA=hashlib.sha256(Path(previous.__file__).read_bytes()).hexdigest()
OWN_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

def namespace(tree):
 names=set();imports=set()
 for node in tree.body:
  if isinstance(node,ast.Expr)and isinstance(node.value,ast.Constant)and type(node.value.value)is str:continue
  if isinstance(node,ast.ImportFrom)and not node.level and all(n.name!='*'for n in node.names):
   bound=[n.asname or n.name for n in node.names];imports.update(bound)
  elif isinstance(node,(ast.FunctionDef,ast.ClassDef)):bound=[node.name]
  else:raise ValueError('module statement outside closed import/declaration namespace')
  for name in bound:
   if name in names:raise ValueError('module binding shadows an earlier import/declaration')
   names.add(name)
 return imports

def derive(pack):
 if hashlib.sha256(Path(previous.__file__).read_bytes()).hexdigest()!=PREVIOUS_SHA or hashlib.sha256(Path(__file__).read_bytes()).hexdigest()!=OWN_SHA:raise ValueError('loaded architecture compiler changed; reload required')
 stamp=pack.get('architecture_observer_v3')
 if type(stamp)is not dict or stamp.get('producer_sha256')!=observer.OWN_SHA or stamp.get('source_executed')is not False:raise ValueError('closed complete-source observer stamp required')
 sources={n:t.encode('utf-8')for n,t in stamp['sources'].items()}
 if observer.extract(sources)!=pack:raise ValueError('architecture fields differ from bounded source re-extraction')
 trees={n:ast.parse(b.decode())for n,b in sources.items()}
 imports={n:namespace(t)for n,t in trees.items()}
 for name,tree in trees.items():
  for node in ast.walk(tree):
   if isinstance(node,(ast.Global,ast.Nonlocal)):raise ValueError('dynamic scope declaration outside fixed architecture profile')
   if isinstance(node,ast.Name)and isinstance(node.ctx,(ast.Store,ast.Del))and node.id in imports[name]:raise ValueError('local assignment shadows an imported architecture reference')
   if isinstance(node,ast.arg)and node.arg in imports[name]:raise ValueError('formal parameter shadows an imported architecture reference')
 cls=next(n for n in trees['adapter.py'].body if isinstance(n,ast.ClassDef)and n.name=='BalanceAdapter')
 if cls.decorator_list or cls.bases or cls.keywords:raise ValueError('adapter class transformations outside reviewed profile')
 read=next(n for n in cls.body if isinstance(n,ast.FunctionDef)and n.name=='read')
 if read.decorator_list:raise ValueError('decorated read method outside reviewed profile')
 if [type(n).__name__ for n in read.body]!=['If','Try','Return']:raise ValueError('direct exception boundary shape changed')
 protected=read.body[1]
 if len(protected.body)!=1 or not isinstance(protected.body[0],ast.Assign):raise ValueError('one direct protected assignment required')
 assignment=protected.body[0]
 if len(assignment.targets)!=1 or not isinstance(assignment.targets[0],ast.Name)or assignment.targets[0].id!='payload':raise ValueError('protected result is not the selected payload binding')
 if not isinstance(assignment.value,ast.Call)or ast.unparse(assignment.value.func)!='self._client.get':raise ValueError('protected assignment must directly evaluate the selected client call')
 if len(protected.handlers)!=1 or protected.orelse or protected.finalbody:raise ValueError('one direct translation handler required')
 handler=protected.handlers[0]
 if len(handler.body)!=1 or not isinstance(handler.body[0],ast.Raise):raise ValueError('translation must be a direct sole handler raise')
 client=next(n for n in trees['client.py'].body if isinstance(n,ast.ClassDef)and n.name=='JsonClient')
 if client.decorator_list or client.keywords:raise ValueError('protocol class transformations outside reviewed profile')
 result=previous.derive(pack)
 result.update(version='0.0.3-research',producer_sha256=OWN_SHA,observer_sha256=observer.OWN_SHA,source_executed=False,owner_approved=False,training_gold=False,publication_authorized=False)
 result['limitations']=['Closed owned source syntax profile only; imports, protocol conformance, dynamic receivers, helper behavior and actual exception flow are not executed or resolved.','Complete inline source hashes bind this extraction, not physical paths or independently authenticated Git revisions.']
 return result
