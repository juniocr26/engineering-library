"""Freeze new exception ownership/admission counterexamples before observations."""
import ast,datetime,hashlib,importlib.util,json
from pathlib import Path
P=Path(__file__).resolve().parent;OLD=P.parent/'documentation-intelligence-20261120'
spec=importlib.util.spec_from_file_location('old_architecture_observer',OLD/'assemble_architecture_facts_v2.py');observer=importlib.util.module_from_spec(spec);spec.loader.exec_module(observer)
base={n:(observer.SOURCE/n).read_bytes()for n in observer.FILES}
rows=[]
def add(id,file,transform,expected,reason):
 sources=dict(base)
 if file:
  tree=ast.parse(sources[file]);transform(tree);ast.fix_missing_locations(tree);sources[file]=(ast.unparse(tree)+'\n').encode();compile(tree,file,'exec')
 rows.append({'id':id,'expected':expected,'reason':reason,'sources':{n:b.decode()for n,b in sources.items()},'source_sha256':{n:hashlib.sha256(b).hexdigest()for n,b in sources.items()}})
def read(t):return next(n for n in ast.walk(t)if isinstance(n,ast.FunctionDef)and n.name=='read')
def handler(t):return read(t).body[1].handlers[0]
def lazy_call(t):
 assignment=read(t).body[1].body[0];assignment.value=ast.Lambda(args=ast.arguments(posonlyargs=[],args=[],kwonlyargs=[],kw_defaults=[],defaults=[]),body=assignment.value)
def dead_call(t):
 assignment=read(t).body[1].body[0];assignment.value=ast.IfExp(test=ast.Constant(True),body=ast.Constant(None),orelse=assignment.value)
def handler_nested(t):
 h=handler(t);h.body=[ast.FunctionDef(name='never_called',args=ast.arguments(posonlyargs=[],args=[],kwonlyargs=[],kw_defaults=[],defaults=[]),body=h.body,decorator_list=[])]
def handler_dead(t):
 h=handler(t);h.body=[ast.If(test=ast.Constant(False),body=h.body,orelse=[])]
def handler_return(t):handler(t).body.insert(0,ast.Return(ast.Constant(None)))
def handler_loop(t):
 h=handler(t);h.body=[ast.For(target=ast.Name(id='unused',ctx=ast.Store()),iter=ast.Tuple(elts=[],ctx=ast.Load()),body=h.body,orelse=[])]
def rebind(name):
 def change(t):t.body.insert(3,ast.Assign(targets=[ast.Name(id=name,ctx=ast.Store())],value=ast.Name(id='ValueError'if name!='balance_from_payload'else'print',ctx=ast.Load())))
 return change
def protocol_rebound(t):t.body.insert(1,ast.Assign(targets=[ast.Name(id='Protocol',ctx=ast.Store())],value=ast.Name(id='object',ctx=ast.Load())))
add('original-owned-architecture',None,None,'DERIVED','Existing reviewed fixed source shape.')
add('try-client-call-lazy-lambda','adapter.py',lazy_call,'REFUSED','Lexically nested client call is not the direct expression evaluated by the protected assignment.')
add('try-client-call-dead-expression','adapter.py',dead_call,'REFUSED','Unreachable client call must not certify the documented client-call exception boundary.')
add('translation-raise-nested-definition','adapter.py',handler_nested,'REFUSED','Nested function is not an executed handler raise.')
add('translation-raise-dead-conditional','adapter.py',handler_dead,'REFUSED','Dead conditional does not execute the documented raise.')
add('translation-raise-after-return','adapter.py',handler_return,'REFUSED','Unconditional return precedes the claimed translation raise.')
add('translation-raise-empty-loop','adapter.py',handler_loop,'REFUSED','Empty loop never reaches its lexically nested raise.')
add('catch-import-rebound','adapter.py',rebind('GatewayUnavailable'),'REFUSED','Imported exception identity is overwritten before the class declaration.')
add('raised-import-rebound','adapter.py',rebind('BalanceUnavailable'),'REFUSED','Imported translated exception identity is overwritten before the class declaration.')
add('mapper-import-rebound','adapter.py',rebind('balance_from_payload'),'REFUSED','Imported mapper identity is overwritten before the class declaration.')
add('protocol-import-rebound','client.py',protocol_rebound,'REFUSED','Written Protocol base resolves to overwritten local binding in the source sequence.')
def harmless(t):t.body.insert(0,ast.Expr(ast.Constant('Owned module documentation.')))
add('harmless-module-docstring','adapter.py',harmless,'DERIVED','A source docstring does not change bindings or the reviewed statement shape.')
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_before_predictions':True,'scope':'Owned synthetic mutations only; no permanent tests or source fixtures modified.','source_executed':False,'model_calls':0,'rows':rows,'baseline_observer_sha256':hashlib.sha256((OLD/'assemble_architecture_facts_v2.py').read_bytes()).hexdigest(),'baseline_compiler_sha256':hashlib.sha256((OLD/'prepare_architecture_claims_v2.py').read_bytes()).hexdigest()}
with(P/'architecture-boundary-oracle-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'cases':len(rows),'expected_refusals':sum(r['expected']=='REFUSED'for r in rows)})
