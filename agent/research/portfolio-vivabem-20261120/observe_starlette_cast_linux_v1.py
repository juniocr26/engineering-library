import ast,json,hashlib,platform
ALLOWED_NODES = {'FunctionDef', 'arguments', 'arg', 'If', 'BoolOp', 'Or', 'And', 'Compare', 'Name', 'Load', 'Store', 'Is', 'Constant', 'Return', 'Call', 'Dict', 'Assign', 'Attribute', 'NotIn', 'Raise', 'JoinedStr', 'FormattedValue', 'Subscript', 'Try', 'ExceptHandler', 'Tuple'}

ALLOWED_NAMES = {'self', 'key', 'value', 'cast', 'bool', 'str', 'isinstance', 'mapping', 'ValueError', 'TypeError', 'cast_name', 'getattr', 'type'}

ALLOWED_CALLS = {'isinstance', 'ValueError', 'cast', 'value.lower', 'getattr', 'type'}

ALLOWED_ATTRIBUTES = {'value.lower', 'cast.__name__', 'type(cast).__name__'}

SAFE_BUILTINS = {'bool': bool, 'str': str, 'isinstance': isinstance, 'ValueError': ValueError, 'TypeError': TypeError, 'getattr': getattr, 'type': type}

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

def matches(observation, expected):
    if 'error' in expected:
        return observation.get('error') == expected['error'] and expected['message_contains'] in observation.get('message', '')
    return observation.get('type') == expected['type'] and observation.get('value') == expected['value'] and ('error' not in observation)

payload=json.loads('{"sources": [{"phase": "before", "source": "def _perform_cast(self, key, value, cast=None):\\n    if cast is None or value is None:\\n        return value\\n    elif cast is bool and isinstance(value, str):\\n        mapping = {\'true\': True, \'1\': True, \'false\': False, \'0\': False}\\n        value = value.lower()\\n        if value not in mapping:\\n            raise ValueError(f\\"Config \'{key}\' has value \'{value}\'. Not a valid bool.\\")\\n        return mapping[value]\\n    try:\\n        return cast(value)\\n    except (TypeError, ValueError):\\n        raise ValueError(f\\"Config \'{key}\' has value \'{value}\'. Not a valid {cast.__name__}.\\")", "source_sha256": "4d29f456a3e8d614eeaca3a9f430f2636f6f304ccdaed9530b029f5c2119752d"}, {"phase": "after", "source": "def _perform_cast(self, key, value, cast=None):\\n    if cast is None or value is None:\\n        return value\\n    elif cast is bool and isinstance(value, str):\\n        mapping = {\'true\': True, \'1\': True, \'false\': False, \'0\': False}\\n        value = value.lower()\\n        if value not in mapping:\\n            raise ValueError(f\\"Config \'{key}\' has value \'{value}\'. Not a valid bool.\\")\\n        return mapping[value]\\n    try:\\n        return cast(value)\\n    except (TypeError, ValueError):\\n        cast_name = getattr(cast, \'__name__\', type(cast).__name__)\\n        raise ValueError(f\\"Config \'{key}\' has value \'{value}\'. Not a valid {cast_name}.\\")", "source_sha256": "a3ce54998b4698f02c336a7257602ef7928364894388c70a044a4063b5d97927"}], "key": "OWNED_KEY", "cases": [{"id": "none-cast", "value": "abc", "cast_registry_key": "none", "before_expected": {"type": "str", "value": "abc"}, "after_expected": {"type": "str", "value": "abc"}}, {"id": "none-value", "value": null, "cast_registry_key": "int", "before_expected": {"type": "NoneType", "value": null}, "after_expected": {"type": "NoneType", "value": null}}, {"id": "bool-true", "value": "TRUE", "cast_registry_key": "bool", "before_expected": {"type": "bool", "value": true}, "after_expected": {"type": "bool", "value": true}}, {"id": "bool-false", "value": "0", "cast_registry_key": "bool", "before_expected": {"type": "bool", "value": false}, "after_expected": {"type": "bool", "value": false}}, {"id": "bool-invalid", "value": "unknown", "cast_registry_key": "bool", "before_expected": {"error": "ValueError", "message_contains": "Not a valid bool."}, "after_expected": {"error": "ValueError", "message_contains": "Not a valid bool."}}, {"id": "int-valid", "value": "7", "cast_registry_key": "int", "before_expected": {"type": "int", "value": 7}, "after_expected": {"type": "int", "value": 7}}, {"id": "int-invalid", "value": "bad", "cast_registry_key": "int", "before_expected": {"error": "ValueError", "message_contains": "Not a valid int."}, "after_expected": {"error": "ValueError", "message_contains": "Not a valid int."}}, {"id": "missing-callable-name", "value": "bad", "cast_registry_key": "owned-instance", "before_expected": {"error": "AttributeError", "message_contains": "__name__"}, "after_expected": {"error": "ValueError", "message_contains": "Not a valid OwnedInvalidCallable."}}, {"id": "named-value-error", "value": "bad", "cast_registry_key": "owned-named", "before_expected": {"error": "ValueError", "message_contains": "Not a valid owned_named_invalid."}, "after_expected": {"error": "ValueError", "message_contains": "Not a valid owned_named_invalid."}}, {"id": "named-type-error", "value": "bad", "cast_registry_key": "owned-type", "before_expected": {"error": "ValueError", "message_contains": "Not a valid owned_type_invalid."}, "after_expected": {"error": "ValueError", "message_contains": "Not a valid owned_type_invalid."}}, {"id": "runtime-callback-error", "value": "bad", "cast_registry_key": "owned-runtime", "before_expected": {"error": "RuntimeError", "message_contains": "owned-callback-runtime"}, "after_expected": {"error": "RuntimeError", "message_contains": "owned-callback-runtime"}}, {"id": "name-lookup-runtime-error", "value": "bad", "cast_registry_key": "owned-name-lookup", "before_expected": {"error": "RuntimeError", "message_contains": "owned-name-lookup"}, "after_expected": {"error": "RuntimeError", "message_contains": "owned-name-lookup"}}]}')
assert len(payload['sources'])==2 and len(payload['cases'])==12
registry={'none':None,'int':int,'bool':bool,'owned-instance':OwnedInvalidCallable(),'owned-named':owned_named_invalid,'owned-type':owned_type_invalid,'owned-runtime':owned_runtime_invalid,'owned-name-lookup':OwnedNameLookupRaises()}
results=[]
for entry in payload['sources']:
    assert hashlib.sha256(entry['source'].encode()).hexdigest()==entry['source_sha256']
    module=ast.parse(entry['source'])
    assert len(module.body)==1 and isinstance(module.body[0],ast.FunctionDef)
    assert module.body[0].name=='_perform_cast'
    for item in ast.walk(module.body[0]):
        assert type(item).__name__ in ALLOWED_NODES
        if isinstance(item,ast.Name): assert item.id in ALLOWED_NAMES
        if isinstance(item,ast.Call): assert ast.unparse(item.func) in ALLOWED_CALLS
        if isinstance(item,ast.Attribute): assert ast.unparse(item) in ALLOWED_ATTRIBUTES
        assert not (isinstance(item,ast.Name) and item.id=='self' and isinstance(item.ctx,ast.Load))
    namespace={'__builtins__':dict(SAFE_BUILTINS)}
    exec(compile(module,'owned-public-starlette-body.py','exec'),namespace,namespace)
    for case in payload['cases']:
        assert type(case['value']) in {str,int,bool,type(None)}
        try:
            value=namespace['_perform_cast'](None,payload['key'],case['value'],registry[case['cast_registry_key']])
            observation={'type':type(value).__name__,'value':value}
        except Exception as error:
            observation={'error':type(error).__name__,'message':str(error)}
        expected=case[entry['phase']+'_expected']
        results.append({'phase':entry['phase'],'id':case['id'],'expected':expected,'observation':observation,'matches_frozen_reference':matches(observation,expected)})
print(json.dumps({'python':platform.python_version(),'system':platform.system(),'machine':platform.machine(),'method_invocations':len(results),'results':results,'all_match_frozen_reference':all(r['matches_frozen_reference'] for r in results),'copied_public_method_body_executed':True,'original_module_imported':False,'Config_constructed':False,'upstream_test_suite_executed':False,'external_repository_writes':0}))
