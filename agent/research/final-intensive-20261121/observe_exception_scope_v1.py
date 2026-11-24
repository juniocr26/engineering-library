"""Inspect exact lexical owners and try-body handlers; execute no source text."""
import ast
import datetime
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent


def owner(tree, class_name, function_name):
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name]
    if len(classes) != 1:
        raise ValueError('Expected exactly one class owner')
    methods = [n for n in classes[0].body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == function_name]
    if len(methods) != 1:
        raise ValueError('Expected exactly one method owner')
    return methods[0]


def handler_names(node):
    if node is None:
        return ['BARE_EXCEPT']
    if isinstance(node, ast.Tuple):
        return [ast.unparse(item) for item in node.elts]
    return [ast.unparse(node)]


def observe(source, class_name, method_name, function_text):
    tree = ast.parse(source)
    target = owner(tree, class_name, method_name)
    parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    rows = []
    for call in ast.walk(target):
        if not isinstance(call, ast.Call) or ast.unparse(call.func) != function_text:
            continue
        node = call
        nearest_function = None
        while node in parents:
            node = parents[node]
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                nearest_function = node
                break
        if nearest_function is not target:
            continue
        protections = []
        node = call
        while node is not target:
            parent = parents[node]
            if isinstance(parent, ast.Try) and node in parent.body:
                protections.append({'try_line': parent.lineno, 'handlers': [name for h in parent.handlers for name in handler_names(h.type)]})
            node = parent
        rows.append({'line': call.lineno, 'call': ast.unparse(call), 'protecting_try_bodies': protections})
    return rows


def flags(helper, job):
    cached = observe(helper, 'HelperRetrieval', '_request', 'validate_cached')
    fresh = observe(helper, 'HelperRetrieval', '_request', 'validate_unit')
    wrapper = observe(job, 'JobBoundRetrieval', 'request', 'self.helper.request')
    explicit = lambda rows, name: any(name in guard['handlers'] for row in rows for guard in row['protecting_try_bodies'])
    return {'cached_outer_explicit_subprocess_catch': explicit(cached, 'subprocess.SubprocessError') if cached else None,
            'fresh_explicit_subprocess_catch': explicit(fresh, 'subprocess.SubprocessError'),
            'job_explicit_exception_catch': explicit(wrapper, 'Exception'),
            'cached_call_count': len(cached)}, {'cached_calls': cached, 'fresh_calls': fresh, 'wrapper_calls': wrapper}


if __name__ == '__main__':
    protocol_raw = (P/'exception-scope-protocol-v1.json').read_bytes()
    protocol = json.loads(protocol_raw)
    rows = []
    for case in protocol['cases']:
        helper = (P/case['helper']).read_bytes()
        job = (P/case['job']).read_bytes()
        assert hashlib.sha256(helper).hexdigest() == case['helper_sha256']
        assert hashlib.sha256(job).hexdigest() == case['job_sha256']
        actual, evidence = flags(helper.decode(), job.decode())
        rows.append({**case, 'actual': actual, 'matches_frozen_expectation': actual == case['expected'], 'evidence': evidence})
    result = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'protocol_sha256': hashlib.sha256(protocol_raw).hexdigest(),
              'observer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'records': rows,
              'matched_profiles': {'numerator': sum(r['matches_frozen_expectation'] for r in rows), 'denominator': len(rows)},
              'source_executed': False, 'model_calls': 0,
              'scope': 'Literal lexical-handler ownership only. No semantic-admission metric, exception-class graph, dynamic binding, runtime or generic proof.',
              'all_originals_unchanged': True, 'optimizer_updates': 0, 'gold': 0}
    with (P/'exception-scope-results-v1.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(result['matched_profiles']))
