"""Closed written-helper claim admission; no general prose/runtime entailment."""
import ast,collections,copy,hashlib,importlib.util,json,re
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('closed_helper_keyword_fallback',P/'closed_keyword_lifecycle_v1.py');fallback=importlib.util.module_from_spec(spec);spec.loader.exec_module(fallback)
declaration=fallback.declaration;engine=declaration.engine;observer=engine.observer
NAME=declaration.NAME
DEPENDENCIES={str(Path(module.__file__)):hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()for module in [fallback,declaration,engine,observer,observer.retrieval]}
OWN_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()

def parse(text,language,selector):
 if type(text)is not str or len(text.encode())>4096:raise ValueError('bounded paired prose required')
 subject=re.escape(selector)
 patterns=[(subject+(r' composes ('+NAME+r') and ('+NAME+r') with ('+NAME+r')\.'if language=='en'else r' compõe ('+NAME+r') e ('+NAME+r') com ('+NAME+r')\.'),'written-return-composition',['outer','inner','shared_argument']),
 (subject+(r' materializes ('+NAME+r') into a list\.'if language=='en'else r' materializa ('+NAME+r') em uma lista\.'),'written-list-materialization',['callee']),
 (subject+(r' always delegates traversal to ('+NAME+r')\.'if language=='en'else r' sempre delega a travessia a ('+NAME+r')\.'),'fixed-written-callback',['callee'])]
 for pattern,kind,fields in patterns:
  match=re.fullmatch(pattern,text)
  if match:
   claim={'kind':kind,**dict(zip(fields,match.groups()))}
   if kind=='fixed-written-callback':claim['keyword']='enter'
   engine.validate_claim(claim);return {'predicate':claim,'subject_class':None}
 pattern=(r'The returned sentinel class does not define ('+NAME+r') or ('+NAME+r')\.'if language=='en'else r'A classe sentinela retornada não define ('+NAME+r') nem ('+NAME+r')\.')
 match=re.fullmatch(pattern,text)
 if match:
  claim={'kind':'no-direct-returned-class-methods','methods':list(match.groups())};engine.validate_claim(claim);return {'predicate':claim,'subject_class':'Sentinel'}
 return None

def selected(source,selector):
 tree=ast.parse(source,type_comments=True);functions=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==selector]
 if len(functions)!=1:raise ValueError('unique source declaration required for helper admission')
 counts=collections.Counter()
 for statement in tree.body:
  names,dynamic=observer.module_bindings(ast.Module(body=[statement],type_ignores=[]))
  if dynamic:raise ValueError('dynamic module binding outside helper admission')
  counts.update(names)
 return tree,functions[0],counts

def local_regular_helper(tree,counts,name):
 definitions=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name]
 if len(definitions)!=1 or definitions[0].decorator_list or counts[name]!=1:raise ValueError('helper name lacks a unique undecorated module declaration')

def admit_call_helpers(source,selector,kind):
 tree,fn,counts=selected(source,selector);body=observer.without_docstring(fn.body)
 if len(body)!=1 or not isinstance(body[0],ast.Return)or not isinstance(body[0].value,ast.Call):raise ValueError('complete direct return-call body required')
 call=body[0].value
 if not isinstance(call.func,ast.Name):raise ValueError('direct local call name required')
 if kind=='written-list-materialization':
  if call.func.id!='list'or len(call.args)!=1 or not isinstance(call.args[0],ast.Call)or not isinstance(call.args[0].func,ast.Name):raise ValueError('list materialization source shape outside profile')
  names=[call.args[0].func.id]
 else:
  if len(call.args)!=2 or not isinstance(call.args[0],ast.Call)or not isinstance(call.args[0].func,ast.Name):raise ValueError('composition source shape outside profile')
  names=[call.func.id,call.args[0].func.id]
 for name in names:local_regular_helper(tree,counts,name)

def admitted_callable_guards(fn,counts,local_counts):
 params={n.arg for n in fn.args.posonlyargs+fn.args.args+fn.args.kwonlyargs}
 admitted=set()
 for node in fn.body:
  if not isinstance(node,ast.If)or node.orelse or len(node.body)!=1:continue
  test=node.test
  if not isinstance(test,ast.UnaryOp)or not isinstance(test.op,ast.Not)or not isinstance(test.operand,ast.Call):continue
  check=test.operand
  if not isinstance(check.func,ast.Name)or check.func.id!='callable'or len(check.args)!=1 or check.keywords or not isinstance(check.args[0],ast.Name):continue
  parameter=check.args[0].id;raised=node.body[0]
  if parameter not in params or local_counts[parameter]or counts['callable']or'callable'in params or local_counts['callable']:continue
  if not isinstance(raised,ast.Raise)or raised.cause is not None or not isinstance(raised.exc,ast.Call)or not isinstance(raised.exc.func,ast.Name):continue
  error=raised.exc.func.id
  if error not in {'TypeError','ValueError'}or counts[error]or error in params or local_counts[error]or len(raised.exc.args)!=1 or raised.exc.keywords:continue
  admitted.add(id(node))
 return admitted

def admit_reaching_prefix(statements,admitted_guards=()):
 class PrefixFlow(ast.NodeVisitor):
  def __init__(self):self.exception_handler=False
  def visit_If(self,node):
   if id(node)not in admitted_guards:self.generic_visit(node)
  def visit_FunctionDef(self,node):pass
  visit_AsyncFunctionDef=visit_FunctionDef
  def visit_ClassDef(self,node):raise ValueError('class evaluation before callback wire is outside profile')
  def visit_Return(self,node):raise ValueError('possible earlier return before callback handoff')
  def visit_Raise(self,node):
   if not self.exception_handler:raise ValueError('possible stopping raise before callback handoff')
  def visit_While(self,node):raise ValueError('loop before callback handoff is outside reaching profile')
  visit_For=visit_While
  visit_AsyncFor=visit_While
  visit_With=visit_While
  visit_AsyncWith=visit_While
  visit_Yield=visit_While
  visit_YieldFrom=visit_While
  visit_Await=visit_While
  def visit_ExceptHandler(self,node):
   prior=self.exception_handler;self.exception_handler=True
   for statement in node.body:self.visit(statement)
   self.exception_handler=prior
 flow=PrefixFlow()
 for statement in statements:flow.visit(statement)

def admit_callback_wire(source,selector):
 tree,fn,counts=selected(source,selector);local_regular_helper(tree,counts,'remap')
 if any(isinstance(n,(ast.Global,ast.Nonlocal))for n in ast.walk(fn)):raise ValueError('callback scope declaration outside profile')
 calls=[n.value for n in fn.body if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)]
 if len(calls)!=1:raise ValueError('one unconditional callback handoff statement required')
 call=calls[0]
 if not isinstance(call.func,ast.Name)or call.func.id!='remap'or len(call.args)!=1 or not isinstance(call.args[0],ast.Name)or len(call.keywords)!=1 or call.keywords[0].arg!='enter'or not isinstance(call.keywords[0].value,ast.Name):raise ValueError('only the written remap enter handoff is admitted')
 wrapper_name=call.keywords[0].value.id;wrappers=[n for n in fn.body if isinstance(n,ast.FunctionDef)and n.name==wrapper_name]
 local_counts=collections.Counter()
 for statement in fn.body:
  names,dynamic=observer.module_bindings(ast.Module(body=[statement],type_ignores=[]))
  if dynamic:raise ValueError('dynamic callback scope outside profile')
  local_counts.update(names)
 if len(wrappers)!=1 or local_counts[wrapper_name]!=1 or wrappers[0].decorator_list:raise ValueError('unique undecorated direct callback wrapper required')
 wrapper=wrappers[0]
 handoff_index=next(index for index,node in enumerate(fn.body)if isinstance(node,ast.Expr)and node.value is call)
 if fn.body.index(wrapper)>=handoff_index:raise ValueError('callback wrapper is not bound before its handoff')
 admit_reaching_prefix(fn.body[:handoff_index],admitted_callable_guards(fn,counts,local_counts))
 returns=[n.value for n in wrapper.body if isinstance(n,ast.Return)]
 if len(returns)!=1 or not isinstance(returns[0],ast.Call)or not isinstance(returns[0].func,ast.Name):raise ValueError('direct callback return call required')
 return_index=next(index for index,node in enumerate(wrapper.body)if isinstance(node,ast.Return)and node.value is returns[0])
 admit_reaching_prefix(wrapper.body[:return_index])
 target=returns[0].func.id;params={n.arg for n in fn.args.posonlyargs+fn.args.args+fn.args.kwonlyargs};inner_params={n.arg for n in wrapper.args.posonlyargs+wrapper.args.args+wrapper.args.kwonlyargs}
 if target in inner_params:raise ValueError('callback callee is a wrapper parameter')
 if target in params and local_counts[target]:raise ValueError('outer callback parameter has written rebinding')
 for statement in wrapper.body:
  names,dynamic=observer.module_bindings(ast.Module(body=[statement],type_ignores=[]))
  if dynamic or target in names:raise ValueError('callback target has a local/dynamic wrapper binding')
 if target not in params:local_regular_helper(tree,counts,target)

def decision(packet):
 result={'version':'0.0.3-research','action':'INCONCLUSIVE','source_executed':False,'runtime_bindings_verified':False,'physical_source_paths_authenticated':False,'physical_documentation_certified':False,'owner_approved':False,'training_gold':False,'publication_authorized':False,'automatic_candidate_applier_supported':False,'model_calls':0,'writes':0,'producer_sha256':OWN_SHA,'dependencies_sha256':DEPENDENCIES,'scope':'CLOSED_BILINGUAL_WRITTEN_HELPER_OR_PRIOR_KEYWORD_DECLARATION_PROFILE'}
 try:
  if hashlib.sha256(Path(__file__).read_bytes()).hexdigest()!=OWN_SHA or any(hashlib.sha256(Path(name).read_bytes()).hexdigest()!=expected for name,expected in DEPENDENCIES.items()):raise ValueError('loaded helper admission dependency changed; reload required')
  packet=copy.deepcopy(packet)
  if type(packet)is not dict or set(packet)!=declaration.TOP:raise ValueError('original closed eleven-field packet required')
  if packet['language']!='python'or packet['complete_scope']is not True or packet['source_available']is not True:raise ValueError('complete available Python source required')
  if packet['metadata']!={}or packet['positive_retirement_evidence']is not None:raise ValueError('metadata/retirement extension not admitted')
  for name in ['id','family','logical_contract_id']:
   if type(packet[name])is not str or not packet[name]or len(packet[name].encode())>256:raise ValueError('bounded packet identities required')
  logical=packet['logical_contract_id']
  if not re.fullmatch(NAME+r'(?:\.'+NAME+r')*',logical):raise ValueError('bounded logical selector required')
  selector=logical.rsplit('.',1)[-1]
  if not engine.valid_name(selector):raise ValueError('selector is not a Python identifier')
  docs=packet['documentation']
  if type(docs)is not dict or set(docs)!={'en','pt-br'}:raise ValueError('paired prose required')
  mapped={language:parse(text,language,selector)for language,text in docs.items()}
  if all(value is None for value in mapped.values()):
   prior=fallback.decision(copy.deepcopy(packet))
   if prior.get('source_executed')is not False:result['source_executed']=None;raise ValueError('fallback execution authority uncertain')
   return {**prior,'helper_admission_fallback':True,'helper_admission_producer_sha256':OWN_SHA}
  if mapped['en']is None or mapped['en']!=mapped['pt-br']:raise ValueError('bilingual helper claims disagree or one is unrecognized')
  claim=mapped['en']['predicate'];cards={}
  for when,key in [('previous','previous_source'),('current','current_source')]:
   source=packet[key]
   if type(source)is not str or len(source.encode())>65536:raise ValueError('bounded inline complete source required')
   cards[when]={'path':'inline-packet-module.py','revision':'source-sha256:'+hashlib.sha256(source.encode()).hexdigest(),'source':source,'sha256':hashlib.sha256(source.encode()).hexdigest()}
  observed=engine.recommend(cards['previous'],cards['current'],selector,{'en':claim,'pt-br':claim})
  if any(observed.get(flag)is not False for flag in ['source_executed','runtime_bindings_verified','owner_approved','training_gold','publication_authorized']):result['source_executed']=None;raise ValueError('typed delegate authority uncertain')
  if observed['action']not in ['NO-OP','MODIFY','INCONCLUSIVE']:raise ValueError('helper grammar never authorizes addition or retirement')
  if observed['action']!='INCONCLUSIVE':
   for when in ['previous','current']:
    if claim['kind']in ['written-return-composition','written-list-materialization']:admit_call_helpers(cards[when]['source'],selector,claim['kind'])
    elif claim['kind']=='fixed-written-callback':admit_callback_wire(cards[when]['source'],selector)
    elif mapped['en']['subject_class']:
     local=observed['evidence'][when].get('returned_local_class')
     if not local or local['class_name']!=mapped['en']['subject_class']:raise ValueError('returned class subject is not established')
  result.update(action=observed['action'],reason=observed['reason'],selector=selector,parsed_claim=mapped['en'],typed_observation=observed,original_packet_sha256=digest(packet),interpretation='Only admitted written-source relationships; not all runtime behaviors, arbitrary natural-language entailment or physical-catalog approval.')
 except (ValueError,TypeError,KeyError,AttributeError,SyntaxError,UnicodeError,RecursionError)as error:result.update(action='INCONCLUSIVE',reason=str(error)[:1024])
 return result
