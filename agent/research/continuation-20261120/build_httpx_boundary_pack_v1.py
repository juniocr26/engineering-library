"""Source-reviewed caller/context boundary pack for exactly two frozen cuts."""
import ast
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path

P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('boundary_pack_map_profile',P/'transport_mapping_observer_v1.py')
map_profile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(map_profile)
oracle = json.loads((P/'httpx-cross-file-oracle-v1.json').read_text())
rows = []


def method(tree, owner, selector):
    owners = [n for n in tree.body if isinstance(n,ast.ClassDef)and n.name==owner]
    assert len(owners)==1
    selected = [n for n in owners[0].body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))and n.name==selector]
    assert len(selected)==1 and not selected[0].decorator_list
    return selected[0]


for cut in oracle['revisions']:
    base = P/'new-public-sources-v1/encode--httpx'/cut['revision']
    cards,trees = {},{}
    for name,digest in cut['source_sha256'].items():
        raw = (base/name).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==digest
        cards[name] = {'path':name,'source':raw.decode(),'sha256':digest,'revision':cut['revision']}
        trees[name] = ast.parse(raw.decode())
    transport_path,exception_path = 'httpx/_transports/default.py','httpx/_exceptions.py'
    transport,exceptions = trees[transport_path],trees[exception_path]
    units,facts,checks = {},{},{}
    for owner,selector,pool_call in [('HTTPTransport','handle_request','self._pool.handle_request(req)'),('AsyncHTTPTransport','handle_async_request','await self._pool.handle_async_request(req)')]:
        node = method(transport,owner,selector)
        direct = map_profile.shared.without_docstring(node.body)
        scopes = [(i,n)for i,n in enumerate(direct)if isinstance(n,ast.With)]
        assert len(scopes)==1
        index,protected = scopes[0]
        assert len(protected.items)==1 and ast.unparse(protected.items[0].context_expr)=='map_httpcore_exceptions()'
        assert len(protected.body)==1 and isinstance(protected.body[0],ast.Assign)and ast.unparse(protected.body[0].value)==pool_call
        request_index = next(i for i,n in enumerate(direct)if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id=='req')
        response_index = next(i for i,n in enumerate(direct)if isinstance(n,ast.Return)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='Response')
        assert request_index<index<response_index
        request_call = direct[request_index].value
        assert isinstance(request_call,ast.Call)and ast.unparse(request_call.func)=='httpcore.Request'
        key = owner+'.'+selector
        facts[key] = {'direct_statement_kinds':[type(n).__name__ for n in direct], 'pool_call_inside_selected_map_context':pool_call,'request_construction_before_map_context':True,'response_construction_after_map_context':True,'request_arguments':{keyword.arg:ast.unparse(keyword.value)for keyword in request_call.keywords},'response_arguments':{keyword.arg:ast.unparse(keyword.value)for keyword in direct[response_index].value.keywords},'direct_import_statements':[ast.unparse(n)for n in direct if isinstance(n,(ast.Import,ast.ImportFrom))],'actual_runtime_receiver_verified':False}
        units[key] = map_profile.source_unit(cards[transport_path],node,'complete-selected-method')
        checks[key+':pool_call'] = pool_call==cut['expected']['selected_sync_pool_call'if owner=='HTTPTransport'else'selected_async_pool_call']
        checks[key+':request_before'] = facts[key]['request_construction_before_map_context']==cut['expected']['request_construction_outside_selected_map_context']
        checks[key+':response_after'] = facts[key]['response_construction_after_map_context']==cut['expected']['response_construction_outside_selected_map_context']
    for owner,selector,loop_type in [('ResponseStream','__iter__',ast.For),('AsyncResponseStream','__aiter__',ast.AsyncFor)]:
        node = method(transport,owner,selector)
        direct = map_profile.shared.without_docstring(node.body)
        assert len(direct)==1 and isinstance(direct[0],ast.With)
        protected = direct[0]
        assert len(protected.items)==1 and ast.unparse(protected.items[0].context_expr)=='map_httpcore_exceptions()'and len(protected.body)==1 and isinstance(protected.body[0],loop_type)
        loop = protected.body[0]
        assert ast.unparse(loop.iter)=='self._httpcore_stream'and len(loop.body)==1 and isinstance(loop.body[0],ast.Expr)and isinstance(loop.body[0].value,ast.Yield)
        key = owner+'.'+selector
        facts[key] = {'explicit_iteration_map_context':True,'iteration_kind':type(loop).__name__,'stream_expression':ast.unparse(loop.iter),'yield_expression':ast.unparse(loop.body[0]),'source_only':True}
        units[key] = map_profile.source_unit(cards[transport_path],node,'complete-selected-stream-iteration-method')
        checks[key+':context'] = True==cut['expected']['stream_iteration_has_explicit_map_context']
    for owner,selector in [('ResponseStream','close'),('AsyncResponseStream','aclose'),('HTTPTransport','close'),('AsyncHTTPTransport','aclose')]:
        node = method(transport,owner,selector)
        explicit = [n for n in ast.walk(node)if isinstance(n,(ast.With,ast.AsyncWith))and any(ast.unparse(item.context_expr)=='map_httpcore_exceptions()'for item in n.items)]
        key = owner+'.'+selector
        facts[key] = {'selected_body_has_explicit_map_context':bool(explicit),'body_statements':[ast.unparse(n)for n in node.body],'this_is_not_proof_all_close_errors_are_unmapped':True}
        units[key] = map_profile.source_unit(cards[transport_path],node,'complete-selected-close-method')
        checks[key+':no_explicit_context'] = bool(explicit)==cut['expected']['selected_close_methods_have_explicit_map_context']
    context_nodes = [n for n in exceptions.body if isinstance(n,ast.FunctionDef)and n.name=='request_context']
    assert len(context_nodes)==1
    context = context_nodes[0]
    body = map_profile.shared.without_docstring(context.body)
    assert len(body)==1 and isinstance(body[0],ast.Try)and len(body[0].handlers)==1
    handler = body[0].handlers[0]
    assert ast.unparse(handler.type)=='RequestError'and handler.name=='exc'and len(handler.body)==2
    assert map_profile.dump(handler.body[0])==map_profile.dump(ast.parse('if request is not None:\n    exc.request = request\n').body[0])
    assert ast.unparse(handler.body[1])=='raise exc'
    classes = {n.name:n for n in exceptions.body if isinstance(n,ast.ClassDef)}
    status_parent = [ast.unparse(n)for n in classes['HTTPStatusError'].bases]
    assert status_parent==['HTTPError']
    facts['request_context'] = {'written_handler_type':'RequestError','request_attached_only_under_written_condition':'request is not None','written_assignment':'exc.request = request','written_reraise':'raise exc','HTTPStatusError_declared_bases':status_parent,'RequestError_declared_bases':[ast.unparse(n)for n in classes['RequestError'].bases],'all_HTTPError_types_covered_by_this_written_handler_proven':False,'runtime_context_or_exception_executed':False}
    checks['request_context:handler'] = facts['request_context']['written_handler_type']==cut['expected']['request_context_handler_type']
    checks['httpstatuserror:parent'] = status_parent==[cut['expected']['httpstatuserror_declared_parent']]
    checks['request_context:all_errors_not_claimed'] = False==cut['expected']['request_context_covers_all_httperror_types']
    units['request_context'] = map_profile.source_unit(cards[exception_path],context,'complete-decorated-request-context-function')
    units['HTTPStatusError'] = map_profile.source_unit(cards[exception_path],classes['HTTPStatusError'],'complete-status-error-class')
    units['HTTPError'] = map_profile.source_unit(cards[exception_path],classes['HTTPError'],'complete-error-class-with-property-pair')
    constructor = next(n for n in classes['RequestError'].body if isinstance(n,ast.FunctionDef)and n.name=='__init__')
    sig = map_profile.shared.signature(constructor)
    assert sig['defaults']['request']=={'kind':'literal','type':'NoneType','value':None}
    facts['RequestError.__init__'] = {'written_request_default':None,'signature':sig,'body_statements':[ast.unparse(n)for n in constructor.body],'automatic_request_context_attachment_proven':False}
    units['RequestError.__init__'] = map_profile.source_unit(cards[exception_path],constructor,'complete-selected-error-constructor')
    assert all(checks.values())
    rows.append({'tag':cut['tag'],'revision':cut['revision'],'facts':facts,'evidence':units,'checks':checks,'all_checks_pass':True,'source_executed':False})
record = {'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'classification':'SOURCE_REVIEWED_FROZEN_TWO_CUT_BOUNDARY_PACK_NOT_A_GENERAL_RESOLVER','rows':rows,'checks_count':sum(len(row['checks'])for row in rows),'all_checks_pass':True,'source_executed':False,'http_application_requests':0,'model_calls':0,'permanent_tests_or_production_modified':False,'owner_approved':False,'training_gold':False,'training_excluded':True,'limits':['Complete selected physical methods/context/classes at the two frozen source hashes only.','A lack of an explicit local map context is not a guarantee that a downstream implementation never translates errors.','An imported contextmanager name and source-declared hierarchy do not prove all runtime bindings or client-layer behavior.','HTTPError property getter/setter are quoted as a complete class rather than collapsed into one ambiguous member selector.']}
with(P/'httpx-source-boundary-pack-v1.json').open('x')as stream:
    stream.write(json.dumps(record,indent=2)+'\n')
print(json.dumps({'checks':record['checks_count'],'revisions':len(rows),'evidence_units_each':[len(row['evidence'])for row in rows],'source_execution':False}))
