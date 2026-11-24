"""Separate bounded source queries. Public Git objects are read, never imported."""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
REVISION = '05e6df7e906c3decba377c37548019973f40bf15'


def require(value, message):
    if not value:
        raise ValueError(message)


def unique(items, label):
    require(len(items) == 1, 'unique ' + label)
    return items[0]


def direct_function(body, name):
    return unique([n for n in body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                   and n.name == name], name)


def call_named(node, name):
    return unique([n for n in ast.walk(node) if isinstance(n, ast.Call)
                   and isinstance(n.func, ast.Name) and n.func.id == name], name)


def keywords(call):
    require(all(k.arg is not None for k in call.keywords), 'no keyword unpacking')
    require(len({k.arg for k in call.keywords}) == len(call.keywords), 'unique keyword names')
    return {k.arg: ast.unparse(k.value) for k in call.keywords}


def binding_events(node, target):
    events = []
    for item in ast.walk(node):
        kind = None
        if isinstance(item, ast.Name) and item.id == target and isinstance(item.ctx, (ast.Store, ast.Del)):
            kind = type(item.ctx).__name__
        elif isinstance(item, ast.arg) and item.arg == target:
            kind = 'parameter'
        elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and item.name == target:
            kind = 'declaration'
        elif isinstance(item, ast.alias) and (item.asname or item.name.split('.')[0]) == target:
            kind = 'import'
        elif isinstance(item, ast.ExceptHandler) and item.name == target:
            kind = 'exception-target'
        elif isinstance(item, (ast.Global, ast.Nonlocal)) and target in item.names:
            kind = 'scope-declaration'
        elif isinstance(item, ast.MatchAs) and item.name == target:
            kind = 'match-target'
        elif isinstance(item, ast.MatchStar) and item.name == target:
            kind = 'match-star-target'
        elif isinstance(item, ast.MatchMapping) and item.rest == target:
            kind = 'match-rest-target'
        if kind:
            events.append(kind)
    return sorted(events)


def verify(routing_source, solver_source):
    routing, solver_tree = ast.parse(routing_source), ast.parse(solver_source)
    route = unique([n for n in routing.body if isinstance(n, ast.ClassDef) and n.name == 'APIRoute'], 'APIRoute')
    factory = direct_function(route.body, 'get_route_handler')
    require(len(factory.body) == 4, 'route factory statement shape')
    require(ast.unparse(factory.body[0]) == 'route = cast(_APIRouteLike, self)', 'initial route view')
    require(ast.unparse(factory.body[1]) == 'effective_context = _effective_route_context_var.get()', 'context lookup')
    require(isinstance(factory.body[2], ast.If) and len(factory.body[2].body) == 1 and not factory.body[2].orelse and ast.unparse(factory.body[2].body[0]) == 'route = cast(_APIRouteLike, effective_context)', 'effective route view')
    factory_call = call_named(factory, 'get_request_handler')
    require(isinstance(factory.body[-1], ast.Return) and factory.body[-1].value is factory_call, 'returned factory call')
    fkw = keywords(factory_call)
    require(fkw['dependant'] == 'route.dependant', 'route dependency handoff')
    require(fkw['dependency_overrides_provider'] == 'route.dependency_overrides_provider', 'override handoff')
    require(any(isinstance(n, ast.If) and ast.unparse(n.test) == 'effective_context is not None and effective_context.original_route is self' for n in factory.body), 'effective-context branch')
    imported = [a for n in routing.body if isinstance(n, ast.ImportFrom) and n.module == 'fastapi.dependencies.utils'
                for a in n.names if a.name == 'solve_dependencies' and a.asname is None]
    require(len(imported) == 1, 'direct solver import')
    handler = direct_function(routing.body, 'get_request_handler')
    app = direct_function(handler.body, 'app')
    require(isinstance(app, ast.AsyncFunctionDef), 'async app')
    require(isinstance(handler.body[-1], ast.Return) and ast.unparse(handler.body[-1].value) == 'app', 'return nested app')
    root_call = call_named(app, 'solve_dependencies')
    root_keywords = keywords(root_call)
    require('dependency_cache' not in root_keywords, 'root call omits cache')
    require(root_keywords['request'] == 'request' and root_keywords['dependant'] == 'dependant', 'root argument names')
    solver = direct_function(solver_tree.body, 'solve_dependencies')
    require(binding_events(routing, 'solve_dependencies') == ['import'], 'unmodeled routing solver binding')
    require(binding_events(app, 'dependant') == [], 'unmodeled handler dependant binding')
    require(binding_events(app, 'solve_dependencies') == [], 'unmodeled handler solver binding')
    require(binding_events(solver, 'dependency_cache') == ['Store', 'parameter'], 'unmodeled cache binding')
    require(binding_events(solver, 'solve_dependencies') == ['declaration'], 'unmodeled recursive solver binding')

    defaults = dict(zip([a.arg for a in solver.args.kwonlyargs], solver.args.kw_defaults))
    for variable, key in [('request_astack', 'fastapi_inner_astack'), ('function_astack', 'fastapi_function_astack')]:
        require(any(isinstance(n, ast.Assign) and ast.unparse(n) == variable + " = request.scope.get('" + key + "')" for n in solver.body), 'scope stack read')
        require(any(isinstance(n, ast.Assert) and ast.unparse(n.test) == 'isinstance(' + variable + ', AsyncExitStack)' for n in solver.body), 'written scope stack assertion')
    required_keywords = [name for name, default in defaults.items() if default is None]
    require(required_keywords == ['request', 'dependant', 'async_exit_stack', 'embed_body_fields'], 'required solver keywords')

    require(isinstance(defaults['dependency_cache'], ast.Constant) and defaults['dependency_cache'].value is None, 'cache default None')
    initializer = unique([n for n in solver.body if isinstance(n, ast.If)
                          and ast.unparse(n.test) == 'dependency_cache is None'], 'cache initializer')
    require(len(initializer.body) == 1 and not initializer.orelse, 'initializer shape')
    assignment = initializer.body[0]
    require(isinstance(assignment, ast.Assign) and len(assignment.targets) == 1
            and ast.unparse(assignment.targets[0]) == 'dependency_cache'
            and isinstance(assignment.value, ast.Dict) and not assignment.value.keys, 'empty local dictionary')
    recursive = call_named(solver, 'solve_dependencies')
    require(keywords(recursive)['dependency_cache'] == 'dependency_cache', 'recursive cache handoff')
    result = call_named(solver, 'SolvedDependency')
    require(keywords(result)['dependency_cache'] == 'dependency_cache', 'returned cache handoff')
    endpoint = call_named(app, 'run_endpoint_function')
    require(keywords(endpoint)['values'] == 'solved_result.values', 'endpoint values handoff')
    serializer = call_named(app, 'serialize_response')
    require(keywords(serializer)['response_content'] == 'raw_response', 'serializer result handoff')
    parents = {child: node for node in ast.walk(app) for child in ast.iter_child_nodes(node)}

    def enclosing_if(call):
        found, child = [], call
        while child in parents:
            parent = parents[child]
            if isinstance(parent, ast.If):
                branch = 'then' if child in parent.body else 'else' if child in parent.orelse else 'test'
                found.append({'test': ast.unparse(parent.test), 'branch': branch, 'line': parent.lineno})
            child = parent
        return list(reversed(found))

    expected = [('not errors', 'then'), ('is_sse_stream', 'else'), ('is_json_stream', 'else'),
                ('_is_async_gen_callable(dependant.call) or _is_gen_callable(dependant.call)', 'else')]
    eguards, sguards = enclosing_if(endpoint), enclosing_if(serializer)
    require([(g['test'], g['branch']) for g in eguards] == expected, 'ordinary endpoint conditions')
    require([(g['test'], g['branch']) for g in sguards] == expected + [('isinstance(raw_response, Response)', 'else')], 'serialization conditions')
    endpoint_function = direct_function(routing.body, 'run_endpoint_function')
    endpoint_branch = unique([n for n in endpoint_function.body if isinstance(n, ast.If) and ast.unparse(n.test) == 'is_coroutine'], 'endpoint helper branch')
    direct_calls = [n for n in ast.walk(endpoint_branch) if isinstance(n, ast.Call) and ast.unparse(n.func) == 'dependant.call']
    direct_call = unique(direct_calls, 'direct async endpoint invocation')
    require(not direct_call.args and len(direct_call.keywords) == 1 and direct_call.keywords[0].arg is None and ast.unparse(direct_call.keywords[0].value) == 'values', 'endpoint values expansion')
    require(direct_call in list(ast.walk(endpoint_branch.body[0])), 'async invocation in then branch')
    sync_call = call_named(endpoint_branch, 'run_in_threadpool')
    require(len(sync_call.args) == 1 and ast.unparse(sync_call.args[0]) == '_run_sync_endpoint' and keywords(sync_call) == {'function': 'dependant.call', 'arguments': 'values'}, 'sync helper delegation')
    require(sync_call in list(ast.walk(endpoint_branch.orelse[0])), 'sync delegation in else branch')
    serialization_function = direct_function(routing.body, 'serialize_response')
    field_branch = unique([n for n in serialization_function.body if isinstance(n, ast.If) and ast.unparse(n.test) == 'field'], 'response field branch')
    response_error_if = unique([n for n in field_branch.body if isinstance(n, ast.If) and ast.unparse(n.test) == 'errors'], 'response validation error guard')
    response_error_call = call_named(response_error_if, 'ResponseValidationError')
    require(any(isinstance(n, ast.Raise) and n.exc is response_error_call for n in response_error_if.body), 'response validation raise')
    no_field_return = unique(field_branch.orelse, 'no-field branch')
    require(isinstance(no_field_return, ast.Return) and ast.unparse(no_field_return.value) == 'jsonable_encoder(response_content)', 'no-field encoder')
    error_if = unique([n for n in app.body if isinstance(n, ast.If) and ast.unparse(n.test) == 'errors'], 'request error guard')
    require(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'RequestValidationError' for n in ast.walk(error_if)), 'request validation error construction')
    require(any(isinstance(n, ast.Raise) for n in error_if.body), 'request error raise')
    return {'factory': [factory_call.lineno, factory_call.end_lineno], 'root_solver_call': [root_call.lineno, root_call.end_lineno],
            'cache_initializer': [initializer.lineno, initializer.end_lineno],
            'recursive_solver_call': [recursive.lineno, recursive.end_lineno],
            'returned_cache': [result.lineno, result.end_lineno],
            'endpoint_call': [endpoint.lineno, endpoint.end_lineno], 'endpoint_guards': eguards,
            'serialization_call': [serializer.lineno, serializer.end_lineno], 'serialization_guards': sguards,
            'request_error_branch': [error_if.lineno, error_if.end_lineno],
            'source_only': True, 'global_request_cache_lifetime_verified': False, 'required_solver_keywords': required_keywords, 'additional_helpers_verified': ['run_endpoint_function async/sync argument paths', 'serialize_response error/no-field branches', 'scope stack reads/written assertions', 'effective route view assignment']}


def main():
    inventory = json.loads((ROOT / 'collection-inventory-v2.json').read_text())['repositories']
    repository = next(r for r in inventory if r['repository'] == 'fastapi')['absolute_path']
    frozen = json.loads((ROOT / 'source-freeze-v1.json').read_text())['files']
    sources, lineage = [], []
    for name in ['fastapi/routing.py', 'fastapi/dependencies/utils.py']:
        raw = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', '-C', repository,
                                       'show', REVISION + ':' + name], env=dict(os.environ, GIT_OPTIONAL_LOCKS='0'))
        entry = next(e for e in frozen if e['repository'] == 'fastapi' and e['path'] == name)
        require(hashlib.sha256(raw).hexdigest() == entry['sha256'], 'fresh Git bytes match')
        sources.append(raw.decode())
        lineage.append({'path': name, 'sha256': entry['sha256'], 'fresh_git_matches': True})
    output = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'sources': lineage,
              'observation': verify(*sources), 'source_executed': False,
              'scope': 'Independent selected AST queries, not a general control-flow/type/runtime verifier.',
              'owner_approved': False, 'training_gold': False}
    target = ROOT / 'fastapi-request-context-independent-review-v3.json'
    require(not target.exists(), 'immutable output absent')
    target.write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output))


if __name__ == '__main__':
    main()
