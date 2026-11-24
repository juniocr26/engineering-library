"""V2 separate research verifier: source AST plus typed fact-value binding."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess

P=Path(__file__).resolve().parent
class Refused(ValueError): pass

def strict(raw):
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:raise Refused('duplicate JSON key')
            result[key]=value
        return result
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda token: (_ for _ in ()).throw(Refused('nonfinite JSON')))

def one(items,label):
    if len(items)!=1: raise Refused('ambiguous or absent '+label)
    return items[0]
def named(node,name): return isinstance(node,ast.Name) and node.id==name

def reconstruct(models,utilities):
    mt=ast.parse(models);ut=ast.parse(utilities)
    cls=one([n for n in mt.body if isinstance(n,ast.ClassDef) and n.name=='Dependant'],'Dependant')
    fn=one([n for n in ut.body if isinstance(n,ast.AsyncFunctionDef) and n.name=='solve_dependencies'],'solver')
    fields={}
    for field in cls.body:
        if isinstance(field,ast.AnnAssign) and isinstance(field.target,ast.Name) and field.target.id in ['use_cache','scope']:
            if field.target.id in fields: raise Refused('duplicate selected field')
            fields[field.target.id]=field
    if set(fields)!= {'use_cache','scope'}:raise Refused('selected fields missing')
    if not isinstance(fields['use_cache'].value,ast.Constant) or fields['use_cache'].value.value is not True:raise Refused('use_cache not declared True')
    if not isinstance(fields['scope'].value,ast.Constant) or fields['scope'].value.value is not None:raise Refused('scope not declared None')
    loop=one([n for n in fn.body if isinstance(n,ast.For) and named(n.target,'sub_dependant') and isinstance(n.iter,ast.Attribute) and named(n.iter.value,'dependant') and n.iter.attr=='dependencies'],'dependency loop')
    def comparison(node,left,op,right):
        return isinstance(node,ast.Compare) and named(node.left,left) and len(node.ops)==len(node.comparators)==1 and isinstance(node.ops[0],op) and (named(node.comparators[0],right) if isinstance(right,str) else isinstance(node.comparators[0],ast.Constant) and node.comparators[0].value is right)
    init=one([n for n in fn.body if isinstance(n,ast.If) and comparison(n.test,'dependency_cache',ast.Is,None)],'cache initializer')
    if len(init.body)!=1 or init.orelse:raise Refused('initializer has extra branches')
    assignment=init.body[0]
    if not isinstance(assignment,ast.Assign) or len(assignment.targets)!=1 or not named(assignment.targets[0],'dependency_cache') or not isinstance(assignment.value,ast.Dict) or assignment.value.keys or assignment.value.values:raise Refused('initializer not empty dictionary assignment')
    cache_binds=[]
    for node in ast.walk(fn):
        stores_name=(isinstance(node,ast.Name) and node.id=='dependency_cache' and isinstance(node.ctx,(ast.Store,ast.Del)))
        named_definition=(isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and node is not fn and node.name=='dependency_cache')
        exception_target=isinstance(node,ast.ExceptHandler) and node.name=='dependency_cache'
        imported_target=isinstance(node,ast.alias) and (node.asname or node.name.split('.')[0])=='dependency_cache'
        declared_scope=isinstance(node,(ast.Global,ast.Nonlocal)) and 'dependency_cache' in node.names
        pattern_target=(isinstance(node,(ast.MatchAs,ast.MatchStar)) and node.name=='dependency_cache') or (isinstance(node,ast.MatchMapping) and node.rest=='dependency_cache')
        if stores_name or named_definition or exception_target or imported_target or declared_scope or pattern_target:cache_binds.append(node)
    if len(cache_binds)!=1 or cache_binds[0] is not assignment.targets[0]:raise Refused('other cache binding/deletion or unsupported scope declaration')
    recursive=[]
    for statement in loop.body:
        if not isinstance(statement,ast.Assign) or not isinstance(statement.value,ast.Await):continue
        call=statement.value.value
        if isinstance(call,ast.Call) and named(call.func,'solve_dependencies'):
            keyword=one([k for k in call.keywords if k.arg=='dependency_cache'],'recursive cache keyword')
            if not named(keyword.value,'dependency_cache'):raise Refused('different cache expression passed')
            recursive.append(statement)
    recurse=one(recursive,'direct recursive call')
    reads=[];writes=[]
    for node in loop.body:
        if not isinstance(node,ast.If):continue
        test=node.test
        if isinstance(test,ast.BoolOp) and isinstance(test.op,ast.And) and len(test.values)==2:
            flag,membership=test.values
            if isinstance(flag,ast.Attribute) and named(flag.value,'sub_dependant') and flag.attr=='use_cache' and comparison(membership,'sub_dependant_cache_key',ast.In,'dependency_cache'):
                if len(node.body)!=1:raise Refused('extra cache read statements')
                stmt=node.body[0]
                if not isinstance(stmt,ast.Assign) or len(stmt.targets)!=1 or not named(stmt.targets[0],'solved') or not isinstance(stmt.value,ast.Subscript) or not named(stmt.value.value,'dependency_cache') or not named(stmt.value.slice,'sub_dependant_cache_key'):raise Refused('cache read direction differs')
                reads.append(node)
        if comparison(test,'sub_dependant_cache_key',ast.NotIn,'dependency_cache'):
            if len(node.body)!=1 or node.orelse:raise Refused('extra cache write branches')
            stmt=node.body[0]
            if not isinstance(stmt,ast.Assign) or len(stmt.targets)!=1 or not isinstance(stmt.targets[0],ast.Subscript) or not named(stmt.targets[0].value,'dependency_cache') or not named(stmt.targets[0].slice,'sub_dependant_cache_key') or not named(stmt.value,'solved'):raise Refused('cache write direction differs')
            writes.append(node)
    read=one(reads,'cache read');write=one(writes,'cache write')
    if loop.body.index(write)<=loop.body.index(read):raise Refused('source statement order differs')
    assertions=[]
    for variable in ['request_astack','function_astack']:
        candidates=[]
        for n in fn.body:
            if isinstance(n,ast.Assert) and isinstance(n.test,ast.Call) and named(n.test.func,'isinstance') and len(n.test.args)==2 and named(n.test.args[0],variable) and named(n.test.args[1],'AsyncExitStack') and not n.test.keywords:candidates.append(n)
        assertions.append(one(candidates,variable+' assertion'))
    return {'PF01':('fastapi/dependencies/models.py',[fields['use_cache'],fields['scope']]),'PF02':('fastapi/dependencies/utils.py',[init]),'PF03':('fastapi/dependencies/utils.py',[recurse]),'PF04':('fastapi/dependencies/utils.py',[read.test,read.body[0]]),'PF05':('fastapi/dependencies/utils.py',[write]),'PF06':('fastapi/dependencies/utils.py',assertions)}

def reacquire():
    registry=json.loads((P/'source-freeze-v1.json').read_text())['files'];repos=json.loads((P/'collection-inventory-v2.json').read_text())['repositories'];repo=one([r for r in repos if r['repository']=='fastapi'],'source repository');texts={};identity=[]
    for name in ['fastapi/dependencies/models.py','fastapi/dependencies/utils.py']:
        registered=one([r for r in registry if r['repository']=='fastapi' and r['path']==name],'registered source')
        raw=subprocess.check_output(['git','-c','core.fsmonitor=false','-C',repo['absolute_path'],'show',registered['revision']+':'+name],env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'),timeout=15)
        if hashlib.sha256(raw).hexdigest()!=registered['sha256']:raise Refused('Git source digest differs')
        texts[name]=raw.decode();identity.append({'path':name,'revision':registered['revision'],'sha256':registered['sha256']})
    return texts,identity

def verify_observation(observation,texts,identity):
    reconstructed=reconstruct(texts['fastapi/dependencies/models.py'],texts['fastapi/dependencies/utils.py']);facts=observation['facts']
    if {r['id'] for r in facts}!=set(reconstructed) or len(facts)!=6:raise Refused('fact identity set differs')
    required_top={'profile','status','facts','source_program_executed','runtime_guarantee','arbitrary_prose_verified','owner_approved','training_gold'}
    if set(observation)!=required_top or observation['profile']!='fastapi-written-dependency-cache-flow/1' or observation['status']!='WRITTEN_FLOW_OBSERVED':raise Refused('observation profile differs')
    for key in ['source_program_executed','runtime_guarantee','arbitrary_prose_verified','owner_approved','training_gold']:
        if observation[key] is not False:raise Refused('unsupported approval/runtime claim')
    # Values are admitted only after the independently queried AST conditions hold.
    expected_values={
      'PF01':{'use_cache_declared':True,'scope_declared':None},
      'PF02':{'condition':'dependency_cache is None','assignment':'dependency_cache = {}','other_local_cache_name_rebindings':False},
      'PF03':{'call':'solve_dependencies','keyword':'dependency_cache','value':'dependency_cache','placement':'direct assignment in selected dependency loop'},
      'PF04':{'read_condition':'sub_dependant.use_cache and sub_dependant_cache_key in dependency_cache','assignment':'solved = dependency_cache[sub_dependant_cache_key]','dynamic_call_completion_verified':False},
      'PF05':{'write_condition':'sub_dependant_cache_key not in dependency_cache','assignment':'dependency_cache[sub_dependant_cache_key] = solved','use_cache_in_this_guard':False,'applies_only_when_control_reaches_guard':True},
      'PF06':{'written_isinstance_assertions':['request_astack','function_astack'],'type_name':'AsyncExitStack','assertions_enabled_at_runtime_unverified':True}}
    checks=[]
    for fact in facts:
        if set(fact)!={'id','lexical_owner','written_fact','evidence','runtime_verified'}:raise Refused('fact shape differs')
        owner='Dependant' if fact['id']=='PF01' else 'solve_dependencies'
        if fact['lexical_owner']!=owner or fact['runtime_verified'] is not False:raise Refused('lexical owner/runtime claim differs')
        # JSON canonicalization retains bool/int distinction (True is not 1).
        canonical=lambda value:json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)
        if canonical(fact['written_fact'])!=canonical(expected_values[fact['id']]):raise Refused('typed written fact differs from independently reconstructed source rule')
        path,nodes=reconstructed[fact['id']];evidence=fact['evidence']
        if len(evidence)!=len(nodes):raise Refused('quote count differs')
        raw=texts[path].encode();lines=raw.splitlines(keepends=True)
        for record,node in zip(evidence,nodes):
            quote=b''.join(lines[node.lineno-1:node.end_lineno])
            if record['path']!=path or record['source_sha256']!=hashlib.sha256(raw).hexdigest() or record['first_line']!=node.lineno or record['last_line']!=node.end_lineno or record['quote'].encode()!=quote or record['quote_sha256']!=hashlib.sha256(quote).hexdigest():raise Refused('source quote identity differs')
        checks.append({'fact':fact['id'],'independently_reconstructed_ast':True,'git_source_and_exact_quotes_match':True,'typed_fact_values_match':True,'lexical_owner_and_runtime_limits_match':True})
    result={'status':'SIX_WRITTEN_AST_RULES_AND_TYPED_FACTS_VERIFIED','sources':identity,'checks':checks,'generator_observer_not_imported':True,'source_program_executed':False,'runtime_verified':False,'arbitrary_prose_semantically_verified':False,'owner_approved':False,'training_gold':False,'limits':'Independent acquisition and separately implemented AST queries only; not a general verifier or independent human review. Candidate prose still requires fixed-template and semantic review.'}
    return result

if __name__=='__main__':
    texts,identity=reacquire();raw=(P/'python-cache-flow-observation-v2.json').read_bytes()
    result=verify_observation(strict(raw),texts,identity)
    result['observation_sha256']=hashlib.sha256(raw).hexdigest()
    result['verifier_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    with (P/'python-cache-flow-independent-source-review-v4.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'checks':len(result['checks']),'packet_hash_bound':True}))
