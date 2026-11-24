"""Research-only exact written AST rules; supplied application code is never executed."""
import ast
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent
MAX_SOURCE = 65536

class Inconclusive(ValueError):
    pass

def shape(source):
    return ast.dump(ast.parse(source).body[0], include_attributes=False)

def expression(source):
    return ast.dump(ast.parse(source, mode='eval').body, include_attributes=False)

def node_shape(node):
    return ast.dump(node, include_attributes=False)

def unique(values, label):
    if len(values) != 1:
        raise Inconclusive(label+' is absent or ambiguous')
    return values[0]

def observe(models_source, utils_source):
    sources={'fastapi/dependencies/models.py':models_source,'fastapi/dependencies/utils.py':utils_source}
    trees={}
    for name,text in sources.items():
        if not isinstance(text,str) or not 0<len(text.encode())<=MAX_SOURCE or '\0' in text:
            raise Inconclusive('source bound')
        tree=ast.parse(text)
        if sum(1 for _ in ast.walk(tree))>20000:
            raise Inconclusive('AST bound')
        trees[name]=tree
    model=trees['fastapi/dependencies/models.py']; utility=trees['fastapi/dependencies/utils.py']
    owner=unique([n for n in model.body if isinstance(n,ast.ClassDef) and n.name=='Dependant'],'Dependant')
    solver=unique([n for n in utility.body if isinstance(n,ast.AsyncFunctionDef) and n.name=='solve_dependencies'],'solve_dependencies')
    parents={child:node for node in ast.walk(solver) for child in ast.iter_child_nodes(node)}
    def quote(path,node):
        raw=sources[path].encode();lines=raw.splitlines(keepends=True);part=b''.join(lines[node.lineno-1:node.end_lineno])
        return {'path':path,'source_sha256':hashlib.sha256(raw).hexdigest(),'first_line':node.lineno,'last_line':node.end_lineno,'quote':part.decode(),'quote_sha256':hashlib.sha256(part).hexdigest()}
    facts=[]
    def record(identifier, nodes, path, owner_name, data):
        facts.append({'id':identifier,'lexical_owner':owner_name,'written_fact':data,'evidence':[quote(path,n) for n in nodes],'runtime_verified':False})
    use=unique([n for n in owner.body if isinstance(n,ast.AnnAssign) and isinstance(n.target,ast.Name) and n.target.id=='use_cache'],'use_cache declaration')
    scope=unique([n for n in owner.body if isinstance(n,ast.AnnAssign) and isinstance(n.target,ast.Name) and n.target.id=='scope'],'scope declaration')
    if not (isinstance(use.value,ast.Constant) and use.value.value is True and isinstance(scope.value,ast.Constant) and scope.value.value is None):
        raise Inconclusive('original declared defaults not established')
    record('PF01',[use,scope],'fastapi/dependencies/models.py','Dependant',{'use_cache_declared':True,'scope_declared':None})
    initial=unique([n for n in solver.body if isinstance(n,ast.If) and node_shape(n.test)==expression('dependency_cache is None')],'cache initialization guard')
    if len(initial.body)!=1 or initial.orelse or node_shape(initial.body[0])!=shape('dependency_cache = {}'):
        raise Inconclusive('empty cache initialization body differs')
    assignments=[n for n in ast.walk(solver) if isinstance(n,(ast.Assign,ast.AnnAssign,ast.AugAssign)) and any(isinstance(t,ast.Name) and t.id=='dependency_cache' for t in (n.targets if isinstance(n,ast.Assign) else [n.target]))]
    if assignments!=[initial.body[0]]:
        raise Inconclusive('other cache-name rebinding present')
    record('PF02',[initial],'fastapi/dependencies/utils.py','solve_dependencies',{'condition':'dependency_cache is None','assignment':'dependency_cache = {}','other_local_cache_name_rebindings':False})
    loop=unique([n for n in solver.body if isinstance(n,ast.For) and node_shape(n.target)==expression('sub_dependant').replace('Load()','Store()') and node_shape(n.iter)==expression('dependant.dependencies')],'selected dependency loop')
    calls=[n for n in ast.walk(solver) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='solve_dependencies']
    recursive=unique(calls,'written recursive call')
    kw=unique([k for k in recursive.keywords if k.arg=='dependency_cache'],'recursive dependency_cache keyword')
    if node_shape(kw.value)!=expression('dependency_cache'):
        raise Inconclusive('recursive cache passage differs')
    assign=parents.get(parents.get(recursive))
    if not isinstance(parents.get(recursive),ast.Await) or not isinstance(assign,ast.Assign) or parents.get(assign) is not loop:
        raise Inconclusive('recursive call placement differs')
    record('PF03',[assign],'fastapi/dependencies/utils.py','solve_dependencies',{'call':'solve_dependencies','keyword':'dependency_cache','value':'dependency_cache','placement':'direct assignment in selected dependency loop'})
    read=unique([n for n in loop.body if isinstance(n,ast.If) and node_shape(n.test)==expression('sub_dependant.use_cache and sub_dependant_cache_key in dependency_cache')],'cache read guard')
    if len(read.body)!=1 or node_shape(read.body[0])!=shape('solved = dependency_cache[sub_dependant_cache_key]'):
        raise Inconclusive('cache read assignment differs')
    record('PF04',[read.test,read.body[0]],'fastapi/dependencies/utils.py','solve_dependencies',{'read_condition':'sub_dependant.use_cache and sub_dependant_cache_key in dependency_cache','assignment':'solved = dependency_cache[sub_dependant_cache_key]','dynamic_call_completion_verified':False})
    write=unique([n for n in loop.body if isinstance(n,ast.If) and node_shape(n.test)==expression('sub_dependant_cache_key not in dependency_cache')],'cache write guard')
    if len(write.body)!=1 or write.orelse or node_shape(write.body[0])!=shape('dependency_cache[sub_dependant_cache_key] = solved'):
        raise Inconclusive('cache write assignment differs')
    if loop.body.index(write)<=loop.body.index(read):
        raise Inconclusive('write no longer follows read/computation branches')
    record('PF05',[write],'fastapi/dependencies/utils.py','solve_dependencies',{'write_condition':'sub_dependant_cache_key not in dependency_cache','assignment':'dependency_cache[sub_dependant_cache_key] = solved','use_cache_in_this_guard':False,'applies_only_when_control_reaches_guard':True})
    assertions=[]
    for name in ['request_astack','function_astack']:
        node=unique([n for n in solver.body if isinstance(n,ast.Assert) and node_shape(n.test)==expression('isinstance('+name+', AsyncExitStack)')],name+' assertion')
        assertions.append(node)
    record('PF06',assertions,'fastapi/dependencies/utils.py','solve_dependencies',{'written_isinstance_assertions':['request_astack','function_astack'],'type_name':'AsyncExitStack','assertions_enabled_at_runtime_unverified':True})
    return {'profile':'fastapi-written-dependency-cache-flow/1','status':'WRITTEN_FLOW_OBSERVED','facts':facts,'source_program_executed':False,'runtime_guarantee':False,'arbitrary_prose_verified':False,'owner_approved':False,'training_gold':False}

if __name__=='__main__':
    registry=json.loads((P/'source-freeze-v1.json').read_text())['files'];texts={}
    for name in ['fastapi/dependencies/models.py','fastapi/dependencies/utils.py']:
        item=unique([r for r in registry if r['repository']=='fastapi' and r['path']==name],'frozen source')
        path=Path(item['evidence_path']);raw=path.read_bytes()
        if path.is_symlink() or hashlib.sha256(raw).hexdigest()!=item['sha256']:
            raise Inconclusive('frozen source identity mismatch')
        texts[name]=raw.decode()
    observation=observe(texts['fastapi/dependencies/models.py'],texts['fastapi/dependencies/utils.py'])
    target=P/'python-cache-flow-observation-v1.json'
    with target.open('x') as output:output.write(json.dumps(observation,indent=2)+'\n')
    print(json.dumps({'status':observation['status'],'facts':len(observation['facts']),'source_executed':False}))
