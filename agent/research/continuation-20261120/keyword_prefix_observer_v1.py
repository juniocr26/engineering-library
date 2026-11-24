"""Bounded complete-statement kwargs prefix facts, never whole-callable semantics."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import warnings

P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('keyword_shared_module_observer', P / 'module_contract_observer_v5.py')
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
OWN_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
SHARED_SHA = hashlib.sha256(Path(shared.__file__).read_bytes()).hexdigest()
RESERVED = {'TypeError', 'callable', 'isinstance', 'str', 'tuple', 'list', 'set'}


def dump(node):
    return ast.dump(node, include_attributes=False)


def guard(node, kwargs):
    if not isinstance(node, ast.If) or not isinstance(node.test, ast.Name) or node.test.id != kwargs or node.orelse or len(node.body) != 1:
        return False
    expected = ast.parse("if " + kwargs + ":\n    raise TypeError('unexpected keyword arguments: %r' % " + kwargs + ".keys())\n").body[0]
    return dump(node) == dump(expected)


def callable_guard(node, parameters):
    if not isinstance(node, ast.If) or node.orelse or len(node.body) != 1 or not isinstance(node.body[0], ast.Raise):
        return False
    test = node.test
    if not isinstance(test, ast.UnaryOp) or not isinstance(test.op, ast.Not) or not isinstance(test.operand, ast.Call):
        return False
    call = test.operand
    if not isinstance(call.func, ast.Name) or call.func.id != 'callable' or len(call.args) != 1 or call.keywords or not isinstance(call.args[0], ast.Name) or call.args[0].id not in parameters:
        return False
    raised = node.body[0]
    if raised.cause is not None or not isinstance(raised.exc, ast.Call) or not isinstance(raised.exc.func, ast.Name) or raised.exc.func.id != 'TypeError' or len(raised.exc.args) != 1 or raised.exc.keywords:
        return False
    message = raised.exc.args[0]
    return isinstance(message, ast.BinOp) and isinstance(message.op, ast.Mod) and isinstance(message.left, ast.Constant) and type(message.left.value) is str and isinstance(message.right, ast.Name) and message.right.id == call.args[0].id


def bound_names(node):
    names = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Name) and isinstance(child.ctx, (ast.Store, ast.Del)):
            names.add(child.id)
        elif isinstance(child, ast.arg):
            names.add(child.arg)
        elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(child.name)
        elif isinstance(child, (ast.Import, ast.ImportFrom)):
            names.update(a.asname or (a.name.split('.')[0] if isinstance(child, ast.Import) else a.name) for a in child.names)
        elif isinstance(child, (ast.MatchAs, ast.MatchStar)) and child.name:
            names.add(child.name)
        elif isinstance(child, ast.MatchMapping) and child.rest:
            names.add(child.rest)
        elif isinstance(child, ast.ExceptHandler) and child.name:
            names.add(child.name)
    return names


def normalization_shapes(local):
    # Explicit historical trace syntax shapes, not arbitrary condition evaluation.
    texts = [
        "if {v} is True:\n    {v} = ('visit', 'enter', 'exit')\nelif isinstance({v}, str):\n    {v} = ({v},)\n",
        "if not isinstance({v}, (tuple, list, set)):\n    raise TypeError('trace expected tuple of event names, not: %r' % {v})\n",
        "trace_enter, trace_exit, trace_visit = ('enter' in {v}, 'exit' in {v}, 'visit' in {v})\n",
    ]
    return {dump(ast.parse(text.format(v=local)).body[0]) for text in texts}


def observe(card, selector, keyword):
    result = {'version': '0.0.1-research', 'status': 'INCONCLUSIVE', 'source_executed': False,
              'runtime_bindings_verified': False, 'physical_source_paths_authenticated': False,
              'owner_approved': False, 'training_gold': False, 'publication_authorized': False,
              'model_calls': 0, 'writes': 0, 'producer_sha256': OWN_SHA}
    try:
        if hashlib.sha256(Path(__file__).read_bytes()).hexdigest() != OWN_SHA or hashlib.sha256(Path(shared.__file__).read_bytes()).hexdigest() != SHARED_SHA:
            raise ValueError('loaded keyword/shared observer changed; reload required')
        card = copy.deepcopy(card)
        if type(card) is not dict or set(card) != {'path', 'revision', 'source', 'sha256'} or any(type(v) is not str for v in card.values()):
            raise ValueError('closed string source card required')
        shared.retrieval.relative_path(card['path'])
        if not card['path'].endswith('.py') or len(card['path'].encode()) > 1024 or not 1 <= len(card['revision'].encode()) <= 256:
            raise ValueError('bounded Python path/revision required')
        if any(type(v) is not str or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,127}', v) for v in [selector, keyword]):
            raise ValueError('explicit bounded selector/keyword required')
        raw = card['source'].encode()
        if len(raw) > 65536 or b'\0' in raw or hashlib.sha256(raw).hexdigest() != card['sha256']:
            raise ValueError('module byte/hash bound')
        with warnings.catch_warnings(record=True):
            warnings.simplefilter('always')
            tree = ast.parse(card['source'], type_comments=True)
            if sum(1 for _ in ast.walk(tree)) > 16384:
                raise ValueError('module node bound')
            compile(tree, card['path'], 'exec', dont_inherit=True)
        bindings, dynamic = shared.module_bindings(tree)
        if dynamic or '*' in bindings or RESERVED.intersection(bindings):
            raise ValueError('module namespace unresolved or selected builtins shadowed')
        nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == selector]
        if len(nodes) != 1 or nodes[0].decorator_list or getattr(nodes[0], 'type_params', []):
            raise ValueError('unique unconditional undecorated function required')
        node = nodes[0]
        if RESERVED.intersection(bound_names(node)) or any(isinstance(n, (ast.Global, ast.Nonlocal)) for n in ast.walk(node)):
            raise ValueError('local scope shadows selected builtins or changes scope')
        if any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in {'exec', 'eval', 'globals', 'locals', 'vars', '__import__'} for n in ast.walk(node)):
            raise ValueError('dynamic namespace outside prefix profile')
        if node.args.kwarg is None:
            raise ValueError('actual variadic keyword parameter required')
        kwargs = node.args.kwarg.arg
        parameters = {a.arg for a in node.args.posonlyargs + node.args.args + node.args.kwonlyargs}
        if keyword in parameters:
            raise ValueError('keyword is an explicit formal parameter, outside kwargs profile')
        statements = shared.without_docstring(node.body)
        prefix, pops, seen_locals, normalizations = [], [], set(), set()
        remainder = None
        for statement in statements:
            if guard(statement, kwargs):
                remainder = statement
                prefix.append(statement)
                break
            if callable_guard(statement, parameters):
                prefix.append(statement)
                continue
            if isinstance(statement, ast.Assign) and len(statement.targets) == 1 and isinstance(statement.targets[0], ast.Name) and isinstance(statement.value, ast.Call):
                call = statement.value
                if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name) and call.func.value.id == kwargs and call.func.attr == 'pop' and len(call.args) == 2 and not call.keywords:
                    key, default = call.args
                    if not isinstance(key, ast.Constant) or type(key.value) is not str or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,127}', key.value):
                        raise ValueError('literal bounded keyword pop required')
                    try:
                        default_value = ast.literal_eval(default)
                    except (ValueError, TypeError):
                        raise ValueError('literal keyword default required')
                    if type(default_value) not in (bool, int, str, type(None), tuple) or isinstance(default_value, tuple) and default_value:
                        raise ValueError('default outside closed scalar/empty-tuple profile')
                    local = statement.targets[0].id
                    if local in parameters or local in {kwargs} | RESERVED or local in seen_locals or key.value in {p['keyword'] for p in pops}:
                        raise ValueError('ambiguous/rebound pop target or duplicate keyword')
                    seen_locals.add(local)
                    pops.append({'keyword': key.value, 'local': local, 'default_expression': ast.unparse(default), 'line': statement.lineno})
                    if key.value == 'trace':
                        normalizations.update(normalization_shapes(local))
                    prefix.append(statement)
                    continue
            if dump(statement) in normalizations:
                prefix.append(statement)
                continue
            raise ValueError('statement before remainder guard is outside closed prefix profile')
        if remainder is None:
            raise ValueError('complete direct unexpected-keyword remainder guard not established')
        lines = raw.splitlines(keepends=True)
        first, last = prefix[0], prefix[-1]
        if lines[first.lineno - 1][:first.col_offset].strip() or lines[last.end_lineno - 1][last.end_col_offset:].strip():
            raise ValueError('same-line content outside selected complete statement prefix')
        quote = b''.join(lines[first.lineno - 1:last.end_lineno])
        header = b''.join(lines[node.lineno - 1:node.body[0].lineno - 1])
        if not header or not quote or len(header) + len(quote) > 6144:
            raise ValueError('complete prefix/header quote budget exceeded')
        result.update(status='WRITTEN_KEYWORD_PREFIX_FACTS', selector=selector, keyword=keyword,
                      keyword_recognized_by_direct_pop=keyword in {p['keyword'] for p in pops},
                      kwargs_parameter=kwargs, ordered_direct_pops=pops,
                      source_card={k: v for k, v in card.items() if k != 'source'},
                      signature=shared.signature(node),
                      callable_full_ast_sha256=hashlib.sha256(dump(node).encode()).hexdigest(),
                      full_callable_quote_included=False,
                      evidence={'header': {'first_line': node.lineno, 'last_line': node.body[0].lineno - 1,
                                           'quote': header.decode(), 'sha256': hashlib.sha256(header).hexdigest()},
                                'complete_statement_prefix': {'first_line': first.lineno, 'last_line': last.end_lineno,
                                                              'quote': quote.decode(), 'sha256': hashlib.sha256(quote).hexdigest(),
                                                              'complete_ast_statements': True, 'complete_callable': False}},
                      limitations=['Only the complete written prefix before its exact unexpected-keyword guard is certified.',
                                   'Recognizing a keyword does not prove accepted values, later traversal, runtime bindings or absence of other exceptions.',
                                   'Whole module syntax/hash and whole callable AST hash are retained; no whole-callable quote or semantic proof is claimed.',
                                   'No physical path/upstream authentication, natural-language generalization, publication or retirement authority.'])
    except (ValueError, TypeError, KeyError, SyntaxError, UnicodeError, RecursionError) as error:
        result['reason'] = str(error)
    if len(json.dumps(result, ensure_ascii=False).encode()) > 65536:
        return {'status': 'INCONCLUSIVE', 'reason': 'response bound', 'source_executed': False}
    return result
