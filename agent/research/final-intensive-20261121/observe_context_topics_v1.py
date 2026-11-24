"""Separate exact-owner AST and native syntax evidence for frozen chapter scopes."""
from pathlib import Path
import ast
import datetime
import hashlib
import json
import os
import re
import sys

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
sys.dont_write_bytecode=True
os.environ['PYTHONDONTWRITEBYTECODE']='1'
sys.path.insert(0,str(ROOT/'agent/tools'))
import go_source_ast

sha=lambda raw:hashlib.sha256(raw).hexdigest()
acquired=json.loads((P/'context-topic-source-acquisition-v1.json').read_text())['observations']
for entry in acquired:
    assert entry['exit_code']==0
    assert sha((ROOT/entry['saved_path']).read_bytes())==entry['sha256']
base=P/'context-topic-sources-v1'
fastapi=base/'fastapi-request-context/05e6df7e906c3decba377c37548019973f40bf15'
chi=base/'chi-wrapper-context/9f8adb1aabaa8a91180a821111d3f8e668d1c0bf'
routing=ast.parse((fastapi/'fastapi/routing.py').read_text())
utils=ast.parse((fastapi/'fastapi/dependencies/utils.py').read_text())
parents={child:node for node in ast.walk(routing) for child in ast.iter_child_nodes(node)}
handler=next(n for n in routing.body if isinstance(n,ast.FunctionDef) and n.name=='get_request_handler')
app=next(n for n in handler.body if isinstance(n,ast.AsyncFunctionDef) and n.name=='app')


def direct_calls(owner,name):
    parent={child:node for node in ast.walk(owner) for child in ast.iter_child_nodes(node)}
    result=[]
    for call in ast.walk(owner):
        if not isinstance(call,ast.Call) or ast.unparse(call.func)!=name:
            continue
        node=call
        while node in parent:
            node=parent[node]
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.Lambda)):
                break
        if node is owner:result.append(call)
    return result


def single_call(owner,name):
    found=direct_calls(owner,name)
    if len(found)!=1:raise ValueError('Expected exactly one call in exact lexical owner: '+name)
    return found[0]


def guards(call,owner):
    result=[]
    node=call
    while node is not owner:
        parent=parents[node]
        if isinstance(parent,ast.If):
            if node in parent.body:branch='then'
            elif node in parent.orelse:branch='else'
            else:branch='test'
            result.append({'condition':ast.unparse(parent.test),'branch':branch,'line':parent.lineno})
        node=parent
    return list(reversed(result))


solver_call=single_call(app,'solve_dependencies')
endpoint=single_call(app,'run_endpoint_function')
serialization=single_call(app,'serialize_response')
solver=next(n for n in utils.body if isinstance(n,ast.AsyncFunctionDef) and n.name=='solve_dependencies')
recursive=single_call(solver,'solve_dependencies')
keywords=lambda call:{item.arg:ast.unparse(item.value) for item in call.keywords}
required=[arg.arg for arg,default in zip(solver.args.kwonlyargs,solver.args.kw_defaults) if default is None]
solver_kwargs=keywords(solver_call)
endpoint_guards=guards(endpoint,app)
serialization_guards=guards(serialization,app)
chapter=ROOT/'agent/research/portfolio-vivabem-20261120/fastapi-request-context-candidate-v2'
snippets={lang:re.findall(r'```python\n(.*?)```',(chapter/(lang+'.md')).read_text(),re.S)[0] for lang in ['en','pt-BR']}
assert snippets['en']==snippets['pt-BR']
example_tree=ast.parse(snippets['en'])
example_call=next(n for n in ast.walk(example_tree) if isinstance(n,ast.Call) and ast.unparse(n.func)=='solve_dependencies')
example_keywords=keywords(example_call)
properties={
    'F-CACHE-ABSENT':'dependency_cache' not in solver_kwargs and None not in solver_kwargs,
    'F-NONERROR-GUARD':any(g['condition']=='not errors' and g['branch']=='then' for g in endpoint_guards),
    'F-SERIALIZATION-ELSE':any(g['condition']=='isinstance(raw_response, Response)' and g['branch']=='else' for g in serialization_guards),
    'F-RECURSIVE-CACHE':keywords(recursive).get('dependency_cache')=='dependency_cache',
    'F-REQUIRED-ARGS':set(required)<=set(example_keywords),
}
out=P/'context-topic-verification-v1'
out.mkdir()
source=(chi/'middleware/wrap_writer.go').read_text()
request={'source':source,'path':'selected.go','selectors':['NewWrapResponseWriter','basicWriter.WriteHeader','basicWriter.Write','httpFancyWriter.ReadFrom']}
native=go_source_ast.run(json.dumps(request).encode())
with (out/'chi-selected-native-units.json').open('x') as stream:json.dump(native,stream,indent=2);stream.write('\n')
interface=go_source_ast.run(json.dumps({'source':source,'path':'selected.go','selectors':['WrapResponseWriter']}).encode())
with (out/'chi-interface-native-unit.json').open('x') as stream:json.dump(interface,stream,indent=2);stream.write('\n')
units={u['selector']:u for u in native['units']}
properties['C-DISPATCH']=set(units)==set(request['selectors'])
properties['C-READFROM-OWNERSHIP']=units['httpFancyWriter.ReadFrom']['symbol']=='middleware.httpFancyWriter.ReadFrom'
chi_chapter=ROOT/'agent/research/portfolio-vivabem-20261120/chi-wrapper-context-candidate-v2'
go_snippets={lang:re.findall(r'```go\n(.*?)```',(chi_chapter/(lang+'.md')).read_text(),re.S)[0] for lang in ['en','pt-BR']}
assert go_snippets['en']==go_snippets['pt-BR']
wrapped='package ownedexample\nimport ("net/http"; middleware "github.com/go-chi/chi/v5/middleware")\n'+go_snippets['en']
example_native=go_source_ast.run(json.dumps({'source':wrapped,'path':'owned_example.go','selectors':['observe']}).encode())
properties['C-EXAMPLE']=len(example_native['units'])==1 and example_native['source_executed'] is False
with (out/'chi-owned-example-native.json').open('x') as stream:json.dump(example_native,stream,indent=2);stream.write('\n')
for name,text in [('fastapi-owned-example.py',snippets['en']),('chi-owned-example.go',wrapped)]:
    with (out/name).open('x') as stream:stream.write(text)
protocol=json.loads((P/'context-topic-verification-protocol-v1.json').read_text())
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'protocol_sha256':sha((P/'context-topic-verification-protocol-v1.json').read_bytes()),
        'observer_sha256':sha(Path(__file__).read_bytes()),'properties':properties,
        'all_frozen_source_checks_pass':all(properties.values()),
        'fastapi_observations':{'root_solver_keywords':solver_kwargs,'endpoint_keywords':keywords(endpoint),'endpoint_guards':endpoint_guards,
                                'serialization_keywords':keywords(serialization),'serialization_guards':serialization_guards,
                                'recursive_keywords':keywords(recursive),'required_solver_keywords':required,'example_keywords':example_keywords},
        'native_producer_identity':native['producer'],
        'manual_negative_controls':[dict(c,observed='CONTRADICTED',method='Same-agent source adjudication using separately acquired source and AST/native unit evidence; not a generic prose classifier.') for c in protocol['negative_controls']],
        'manual_unknown_controls':[dict(c,observed='INSUFFICIENT',method='Selected lexical source cannot establish the declared global/runtime guarantee.') for c in protocol['unknown_controls']],
        'metric_boundary':'8 finite source-property checks;6 manually adjudicated negative claims and2 unknown claims. No generic semantic FAR, statistical independence, inference or owner approval.',
        'source_programs_executed':False,'owned_native_parser_executed':True,'upstream_tests_executed':False,
        'typecheck_or_import_resolution':False,'model_calls':0,'optimizer_updates':0,'gold':0}
with (P/'context-topic-verification-results-v1.json').open('x') as stream:
    json.dump(result,stream,indent=2,ensure_ascii=False)
    stream.write('\n')
print(json.dumps({'properties':properties,'source_programs_executed':False}))
