"""Bounded execution of two copied public pure method bodies on owned constant inputs.

Never imports Starlette, constructs Config, reads environments, or executes upstream tests.
"""
import ast
import copy
import datetime
import hashlib
import json
from pathlib import Path
import platform

ROOT = Path(__file__).resolve().parent
ALLOWED_NODES = {
    'FunctionDef', 'arguments', 'arg', 'If', 'BoolOp', 'Or', 'And', 'Compare',
    'Name', 'Load', 'Store', 'Is', 'Constant', 'Return', 'Call', 'Dict', 'Assign',
    'Attribute', 'NotIn', 'Raise', 'JoinedStr', 'FormattedValue', 'Subscript',
    'Try', 'ExceptHandler', 'Tuple',
}
ALLOWED_NAMES = {
    'self', 'key', 'value', 'cast', 'bool', 'str', 'isinstance', 'mapping',
    'ValueError', 'TypeError', 'cast_name', 'getattr', 'type',
}
ALLOWED_CALLS = {'isinstance', 'ValueError', 'cast', 'value.lower', 'getattr', 'type'}
ALLOWED_ATTRIBUTES = {'value.lower', 'cast.__name__', 'type(cast).__name__'}
SAFE_BUILTINS = {'bool': bool, 'str': str, 'isinstance': isinstance,
                 'ValueError': ValueError, 'TypeError': TypeError,
                 'getattr': getattr, 'type': type}


class OwnedInvalidCallable:
    def __call__(self, value):
        raise ValueError('owned-invalid')


class OwnedNameLookupRaises:
    def __call__(self, value):
        raise ValueError('owned-invalid')

    def __getattribute__(self, name):
        if name == '__name__':
            raise RuntimeError('owned-name-lookup')
        return object.__getattribute__(self, name)


def owned_named_invalid(value):
    raise ValueError('owned-invalid')


def owned_type_invalid(value):
    raise TypeError('owned-invalid')


def owned_runtime_invalid(value):
    raise RuntimeError('owned-callback-runtime')


def prepare(entry):
    raw = Path(entry['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != entry['file_sha256']:
        raise ValueError('frozen public source changed')
    tree = ast.parse(raw)
    owners = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Config']
    if len(owners) != 1:
        raise ValueError('unique Config owner')
    methods = [n for n in owners[0].body if isinstance(n, ast.FunctionDef) and n.name == '_perform_cast']
    if len(methods) != 1:
        raise ValueError('unique selected method')
    original = methods[0]
    original_body = ast.dump(ast.Module(body=original.body, type_ignores=[]), include_attributes=False)
    if hashlib.sha256(original_body.encode()).hexdigest() != entry['body_ast_sha256']:
        raise ValueError('body identity mismatch')
    node = copy.deepcopy(original)
    node.returns = None
    for argument in node.args.posonlyargs + node.args.args + node.args.kwonlyargs:
        argument.annotation = None
    if node.decorator_list or node.args.vararg or node.args.kwarg or node.args.kwonlyargs:
        raise ValueError('unsupported method signature')
    if [a.arg for a in node.args.args] != ['self', 'key', 'value', 'cast']:
        raise ValueError('unexpected argument names')
    if len(node.args.defaults) != 1 or not isinstance(node.args.defaults[0], ast.Constant) or node.args.defaults[0].value is not None:
        raise ValueError('unexpected default')
    for item in ast.walk(node):
        if type(item).__name__ not in ALLOWED_NODES:
            raise ValueError('unsafe/unreviewed AST node: ' + type(item).__name__)
        if isinstance(item, ast.Name) and item.id not in ALLOWED_NAMES:
            raise ValueError('unreviewed name')
        if isinstance(item, ast.Call) and ast.unparse(item.func) not in ALLOWED_CALLS:
            raise ValueError('unreviewed call')
        if isinstance(item, ast.Attribute) and ast.unparse(item) not in ALLOWED_ATTRIBUTES:
            raise ValueError('unreviewed attribute')
        if isinstance(item, ast.Name) and item.id == 'self' and isinstance(item.ctx, ast.Load):
            raise ValueError('self must be unused')
    if sum(isinstance(n, ast.FunctionDef) for n in ast.walk(node)) != 1:
        raise ValueError('no nested code')
    if ast.dump(ast.Module(body=node.body, type_ignores=[]), include_attributes=False) != original_body:
        raise ValueError('body changed while stripping annotations')
    module = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
    return module, ast.unparse(module)


def matches(observation, expected):
    if 'error' in expected:
        return observation.get('error') == expected['error'] and expected['message_contains'] in observation.get('message', '')
    return observation.get('type') == expected['type'] and observation.get('value') == expected['value'] and 'error' not in observation


def main():
    protocol = json.loads((ROOT / 'starlette-cast-bounded-runtime-protocol-v1.json').read_text())
    oracle = json.loads((ROOT / 'starlette-cast-bounded-runtime-oracle-v1.json').read_text())
    target = ROOT / 'starlette-cast-bounded-runtime-observation-v1.json'
    if target.exists():
        raise FileExistsError(target)
    prepared = [(entry, *prepare(entry)) for entry in protocol['sources']]
    cast_registry = {'none': None, 'int': int, 'bool': bool,
                     'owned-instance': OwnedInvalidCallable(), 'owned-named': owned_named_invalid,
                     'owned-type': owned_type_invalid, 'owned-runtime': owned_runtime_invalid,
                     'owned-name-lookup': OwnedNameLookupRaises()}
    if len(oracle['cases']) != 12 or len(prepared) != 2:
        raise ValueError('bounded invocation count')
    if any(type(c['value']) not in {str, int, bool, type(None)} for c in oracle['cases']):
        raise ValueError('owned literal values only')
    if any(c['cast_registry_key'] not in cast_registry for c in oracle['cases']):
        raise ValueError('owned callback registry only')
    prepared_receipt = ROOT / 'starlette-cast-bounded-prepared-source-v1.json'
    if prepared_receipt.exists():
        raise FileExistsError(prepared_receipt)
    prepared_receipt.write_text(json.dumps({'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                          'sources': [{'phase': e['phase'], 'source': text,
                                                       'body_ast_sha256': e['body_ast_sha256']}
                                                      for e, module, text in prepared],
                                          'safety_review_complete_before_exec': True}, indent=2) + '\n')
    results = []
    for entry, module, text in prepared:
        namespace = {'__builtins__': dict(SAFE_BUILTINS)}
        # This is intentional, explicitly bounded public copied source execution.
        # Only the reviewed function definition/body is present, not the module/class.
        exec(compile(module, 'owned-starlette-' + entry['phase'] + '-method.py', 'exec'), namespace, namespace)
        function = namespace['_perform_cast']
        for case in oracle['cases']:
            try:
                value = function(None, oracle['key'], case['value'], cast_registry[case['cast_registry_key']])
                observation = {'type': type(value).__name__, 'value': value}
            except Exception as error:
                observation = {'error': type(error).__name__, 'message': str(error)}
            expected = case[entry['phase'] + '_expected']
            results.append({'phase': entry['phase'], 'id': case['id'], 'expected': expected,
                            'observation': observation, 'matches_frozen_reference': matches(observation, expected)})
    output = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'protocol': 'starlette-cast-bounded-runtime-protocol-v1.json',
              'python': platform.python_version(), 'system': platform.system(), 'machine': platform.machine(),
              'method_invocations': len(results), 'results': results,
              'all_match_frozen_reference': all(r['matches_frozen_reference'] for r in results),
              'copied_public_method_body_executed': True, 'original_module_imported': False,
              'Config_constructed': False, 'upstream_test_suite_executed': False,
              'external_repository_writes': 0, 'private_inputs': False,
              'scope': '24 correlated owned body/binding observations, not full Config integration or 24 independent project tests.',
              'owner_approved': False, 'training_gold': False, 'optimizer_steps': 0}
    target.write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({'observations': len(results), 'all_match': output['all_match_frozen_reference'],
                      'copied_public_body_executed': True, 'upstream_tests': False,
                      'mismatches': [{'id': r['id'], 'phase': r['phase']} for r in results if not r['matches_frozen_reference']]}))


if __name__ == '__main__':
    main()
