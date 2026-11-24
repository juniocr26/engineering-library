"""Execute only hash-pinned, reviewed exception definitions in owned namespaces."""
import ast
import __future__
import builtins
import contextlib
import datetime
import hashlib
import json
from pathlib import Path
import platform
import sys
import types

P=Path(__file__).resolve().parent
protocol=json.loads((P/'httpx-exception-composition-protocol-v1.json').read_text())
for relative,expected in protocol['source_files'].items():
    assert hashlib.sha256((P/relative).read_bytes()).hexdigest()==expected
x=P/'new-public-sources-v1/encode--httpx/26d48e0634e6ee9cdc0533996db289ce4b430177'
c=P/'new-public-sources-v1/encode--httpcore/98209758cc14e1a5f966fe1dfdc1064b94055d8c'
core_tree=ast.parse((c/'httpcore/_exceptions.py').read_text())
core_classes=[n for n in core_tree.body if isinstance(n,ast.ClassDef)]
for node in core_classes:
    assert not node.decorator_list and not node.keywords
    assert len(node.bases)==1 and isinstance(node.bases[0],ast.Name)
    assert len(node.body)==1 and isinstance(node.body[0],ast.Pass)
bridge=ast.parse((c/'httpcore/__init__.py').read_text())
exports=next(n for n in bridge.body if isinstance(n,ast.ImportFrom)and n.module=='_exceptions')
assert {n.name for n in exports.names}=={n.name for n in core_classes}
assert all(n.asname is None for n in exports.names)
allowed_builtins={key:getattr(builtins,key)for key in ['__build_class__','Exception','RuntimeError','property','super','str','len','isinstance','issubclass']}
core={'__name__':'owned_httpcore_exception_definitions','__builtins__':allowed_builtins}
exec(compile(ast.Module(body=core_classes,type_ignores=[]),'frozen-httpcore-exception-classes','exec'),core)
core_namespace=types.SimpleNamespace(**{n.name:core[n.name]for n in core_classes})
x_tree=ast.parse((x/'httpx/_exceptions.py').read_text())
classes={n.name:n for n in x_tree.body if isinstance(n,ast.ClassDef)}
selected={b for a,b in protocol['source_pairs']}|{'HTTPStatusError'}
while True:
    added={base.id for name in selected for base in classes[name].bases if isinstance(base,ast.Name)and base.id in classes}
    if added<=selected:break
    selected|=added
class_nodes=[n for n in x_tree.body if isinstance(n,ast.ClassDef)and n.name in selected]
transport=ast.parse((x/'httpx/_transports/default.py').read_text())
functions=[n for n in x_tree.body+transport.body if isinstance(n,ast.FunctionDef)and n.name in {'request_context','_load_httpcore_exceptions','map_httpcore_exceptions'}]
assert len(functions)==3 and len(class_nodes)==18
# Reviewed source has no I/O calls. Refuse added imports, dynamic execution or unknown call shapes.
permitted_calls={'super','super().__init__','RuntimeError','len','_load_httpcore_exceptions','HTTPCORE_EXC_MAP.items','isinstance','issubclass','str','mapped_exc','contextlib.contextmanager'}
for root in class_nodes+functions:
    for node in ast.walk(root):
        if isinstance(node,ast.Import):assert root.name=='_load_httpcore_exceptions'and len(node.names)==1 and node.names[0].name=='httpcore'and node.names[0].asname is None
        if isinstance(node,ast.ImportFrom):raise AssertionError('unexpected source import')
        if isinstance(node,ast.Call):assert ast.unparse(node.func)in permitted_calls,ast.unparse(node.func)
        if isinstance(node,ast.Attribute):assert not node.attr.startswith('__')or node.attr=='__init__'
        if isinstance(node,ast.ClassDef):assert not node.decorator_list and not node.keywords
future=ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)
module=ast.fix_missing_locations(ast.Module(body=class_nodes+functions,type_ignores=[]))
code=compile(module,'frozen-httpx-selected-exception-definitions','exec',flags=__future__.annotations.compiler_flag,dont_inherit=True)

def namespace(fail_import=False):
    calls=[]
    marker=ImportError('owned dependency import unavailable')
    def importer(name,globals=None,locals=None,fromlist=(),level=0):
        assert name=='httpcore'and level==0 and not fromlist
        calls.append(name)
        if fail_import:raise marker
        return core_namespace
    ns={'__name__':'owned_httpx_exception_definitions','__builtins__':dict(allowed_builtins,__import__=importer),'contextlib':contextlib,'HTTPCORE_EXC_MAP':{}}
    exec(code,ns)
    return ns,calls,marker

rows=[]
for case in protocol['cases']:
    ns,calls,marker=namespace(case['kind']=='loader-import-failure-before-yield')
    mapper=ns['map_httpcore_exceptions']; request_context=ns['request_context']; checks={}
    kind=case['kind']
    if kind=='mapping':
        original=core[case['source_class']](case['message'])
        try:
            with mapper():raise original
        except Exception as mapped:
            checks['exact_target_class']=type(mapped)is ns[case['target_class']]
            checks['exact_message']=str(mapped)==case['message']
            checks['explicit_cause_identity']=mapped.__cause__ is original
            try:mapped.request
            except RuntimeError as error:checks['request_unset']=str(error)=='The .request property has not been set.'
            else:checks['request_unset']=False
    elif kind in {'unmatched-identity','baseexception-identity'}:
        original=(ValueError if kind=='unmatched-identity'else KeyboardInterrupt)('owned exception')
        try:
            with mapper():raise original
        except BaseException as result:checks['same_object']=result is original
    elif kind=='request-context-attaches':
        sentinel=object(); original=core['ReadTimeout']('owned timeout')
        try:
            with request_context(sentinel):
                with mapper():raise original
        except ns['ReadTimeout']as result:
            checks={'request_identity':result.request is sentinel,'cause_identity':result.__cause__ is original}
    elif kind=='request-context-none-preserves':
        sentinel=object(); original=ns['ReadError']('owned',request=sentinel)
        try:
            with request_context(None):raise original
        except ns['ReadError']as result:checks={'same_object':result is original,'request_identity':result.request is sentinel}
    elif kind=='status-sibling-not-caught':
        sentinel=object(); replacement=object(); original=ns['HTTPStatusError']('owned',request=sentinel,response=object())
        try:
            with request_context(replacement):raise original
        except ns['HTTPStatusError']as result:checks={'same_object':result is original,'original_request_preserved':result.request is sentinel}
    elif kind=='loader-import-failure-before-yield':
        entered=False
        try:
            with mapper():entered=True
        except ImportError as result:checks={'same_import_error':result is marker,'body_not_entered':not entered,'cache_still_empty':ns['HTTPCORE_EXC_MAP']=={}}
    elif kind=='lazy-cache-once':
        with mapper():pass
        cache=ns['HTTPCORE_EXC_MAP']
        with mapper():pass
        checks={'one_import':calls==['httpcore'],'same_cache_object':ns['HTTPCORE_EXC_MAP']is cache,'fourteen_pairs':len(cache)==14}
    else:raise AssertionError(kind)
    assert checks
    rows.append({'id':case['id'],'checks':checks,'all_pass':all(checks.values()),'intercepted_imports':len(calls)})
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':hashlib.sha256((P/'httpx-exception-composition-protocol-v1.json').read_bytes()).hexdigest(),'python':sys.version,'platform':platform.platform(),'cases':rows,'all_pass':all(r['all_pass']for r in rows),'selected_source_classes_executed':{'httpcore':len(core_classes),'httpx':len(class_nodes)},'selected_source_functions_executed':3,'whole_packages_imported':False,'application_http_requests':0,'transport_objects_created':0,'model_calls':0,'training_steps':0,'owner_approved':False,'certified_neural_holdout':False,'limitations':['Owned namespace bindings, not real package import/deployment.','httpcore package __module__ rewriting not executed.','One pinned pair of source revisions; HTTPX permits a range of httpcore versions.','No network, retry, TLS, proxy, connection pool or live request observation.']}
output=P/('httpx-exception-composition-'+sys.argv[1]+'-v1.json')
with output.open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'cases':len(rows),'checks':sum(len(r['checks'])for r in rows),'all_pass':record['all_pass'],'output':output.name})
