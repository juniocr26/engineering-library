"""Read-only public Python AST context index; never imports the inspected project."""
import ast
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SELECTED_CALLS = {
    'get_request_handler', 'solve_dependencies', 'run_endpoint_function',
    'serialize_response', 'request_response', 'SolvedDependency',
}
SELECTED_OWNERS = {
    'APIRoute.get_route_handler', 'get_request_handler', 'get_request_handler.app',
    'run_endpoint_function', 'serialize_response', 'solve_dependencies',
}


def observe(source, path):
    tree = ast.parse(source, filename=path)
    calls, declarations, cache_events = [], [], []

    def location(node):
        return {'lines': [node.lineno, node.end_lineno],
                'quote': ast.get_source_segment(source, node)}

    def visit(node, owners, controls):
        owner = '.'.join(owners)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            owners = owners + [node.name]
            owner = '.'.join(owners)
            if owner in SELECTED_OWNERS:
                declarations.append({'owner': owner, 'kind': type(node).__name__,
                                     'lines': [node.lineno, node.end_lineno],
                                     'arguments': ast.unparse(node.args)})
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in SELECTED_CALLS:
            calls.append({'owner': owner, 'callee': node.func.id,
                          'keyword_unpacking_present': any(k.arg is None for k in node.keywords),
                          'keywords': {k.arg: ast.unparse(k.value) for k in node.keywords if k.arg},
                          'controls': controls, **location(node)})
        if owner in SELECTED_OWNERS and isinstance(node, (ast.Assign, ast.AnnAssign, ast.Return)):
            text = ast.unparse(node)
            if 'dependency_cache' in text and len(text) < 1600:
                cache_events.append({'owner': owner, 'node': type(node).__name__,
                                     'controls': controls, **location(node)})
        if isinstance(node, ast.If):
            visit(node.test, owners, controls)
            for branch_name, body in [('then', node.body), ('else', node.orelse)]:
                for child in body:
                    visit(child, owners, controls + [{'kind': 'if', 'test': ast.unparse(node.test),
                                                      'branch': branch_name, 'line': node.lineno}])
            return
        if isinstance(node, (ast.For, ast.AsyncFor)):
            for child in node.body:
                visit(child, owners, controls + [{'kind': 'loop', 'target': ast.unparse(node.target),
                                                  'iterator': ast.unparse(node.iter), 'line': node.lineno}])
            for child in node.orelse:
                visit(child, owners, controls + [{'kind': 'loop-else', 'line': node.lineno}])
            return
        for child in ast.iter_child_nodes(node):
            visit(child, owners, controls)

    visit(tree, [], [])
    imports = [{'module': n.module, 'names': [{'name': a.name, 'alias': a.asname} for a in n.names],
                'lines': [n.lineno, n.end_lineno]} for n in tree.body if isinstance(n, ast.ImportFrom)
               and n.module in {'fastapi.dependencies.utils', 'fastapi.dependencies.models'}]
    return {'path': path, 'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
            'imports': imports, 'selected_declarations': declarations,
            'selected_name_calls': calls, 'cache_events': cache_events,
            'source_executed': False,
            'limits': 'Lexical paths/if-loop context only; no general control-flow, name-binding, runtime or whole-project proof.'}


def main():
    frozen = json.loads((ROOT / 'source-freeze-v1.json').read_text())['files']
    rows = []
    for relative in ['fastapi/routing.py', 'fastapi/dependencies/utils.py']:
        entry = next(x for x in frozen if x['repository'] == 'fastapi' and x['path'] == relative)
        source = Path(entry['evidence_path']).read_bytes()
        if hashlib.sha256(source).hexdigest() != entry['sha256']:
            raise ValueError('frozen source mismatch')
        rows.append(observe(source.decode(), relative))
    target = ROOT / 'fastapi-request-context-observation-v1.json'
    if target.exists():
        raise FileExistsError(target)
    result = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'protocol': 'fastapi-request-context-protocol-v1.json', 'sources': rows,
              'source_executed': False, 'owner_approved': False, 'training_gold': False}
    target.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'sources': len(rows), 'selected_calls': sum(len(x['selected_name_calls']) for x in rows)}))


if __name__ == '__main__':
    main()
