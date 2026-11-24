"""Isolated static research observation; never imports or runs external source."""
import ast
import copy
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT / 'revision-evidence-v1/starlette'
OLD = '9b403a0c33f0e2eebba099e9e6aa1c1e9535daec'
NEW = '271c277da0ff64e2048a4d46ecc812b9d61db5f6'


def selected(tree):
    owners = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Config']
    if len(owners) != 1:
        raise ValueError('unique Config owner required')
    funcs = [n for n in owners[0].body if isinstance(n, ast.FunctionDef) and n.name == '_perform_cast']
    if len(funcs) != 1:
        raise ValueError('unique method required')
    return funcs[0]


def normalized(node):
    return ast.dump(node, include_attributes=False)


def compare(before, after):
    old, new = selected(before), selected(after)
    old_try, new_try = old.body[-1], new.body[-1]
    if not isinstance(old_try, ast.Try) or not isinstance(new_try, ast.Try):
        raise ValueError('terminal try required')
    expected_old = ast.parse('try:\n return cast(value)\nexcept (TypeError, ValueError):\n raise ValueError(f"Config \'{key}\' has value \'{value}\'. Not a valid {cast.__name__}.")').body[0]
    expected_new = ast.parse('try:\n return cast(value)\nexcept (TypeError, ValueError):\n cast_name = getattr(cast, "__name__", type(cast).__name__)\n raise ValueError(f"Config \'{key}\' has value \'{value}\'. Not a valid {cast_name}.")').body[0]
    if normalized(old_try) != normalized(expected_old) or normalized(new_try) != normalized(expected_new):
        raise ValueError('unrecognized selected branch')
    old_prefix, new_prefix = copy.deepcopy(old), copy.deepcopy(new)
    old_prefix.body.pop()
    new_prefix.body.pop()
    if normalized(old_prefix) != normalized(new_prefix):
        raise ValueError('other selected-method behavior changed')
    return {'decision': 'MODIFY', 'old_lines': [old_try.lineno, old_try.end_lineno], 'new_lines': [new_try.lineno, new_try.end_lineno], 'unchanged_prefix_ast': True, 'cast_invocation_unchanged': True, 'except_types_unchanged': True}


def main():
    files = [BASE / rev / 'starlette/config.py' for rev in (OLD, NEW)]
    trees = [ast.parse(f.read_text()) for f in files]
    result = compare(*trees)
    controls = []
    for name in ('missing-fallback', 'wrong-owner', 'changed-cast-target'):
        changed = copy.deepcopy(trees[1])
        method = selected(changed)
        if name == 'missing-fallback':
            method.body[-1].handlers[0].body[0].value.args.pop()
        elif name == 'wrong-owner':
            next(n for n in changed.body if isinstance(n, ast.ClassDef) and n.name == 'Config').name = 'Other'
        else:
            method.body[-1].body[0].value.func.id = 'other_cast'
        try:
            compare(trees[0], changed)
            refused = False
        except ValueError:
            refused = True
        controls.append({'name': name, 'unsupported_shape_refused': refused})
    assert all(c['unsupported_shape_refused'] for c in controls)
    output = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'protocol': 'starlette-revision-maintenance-protocol-v1.json', 'sources': [{'path': str(f.relative_to(ROOT)), 'sha256': hashlib.sha256(f.read_bytes()).hexdigest()} for f in files], 'observation': result, 'negative_shape_controls': controls, 'external_source_executed': False, 'scope': 'One closed selected method and real revision; synthetic controls are development checks, not independent evaluation cases.'}
    target = ROOT / 'starlette-revision-static-observation-v1.json'
    if target.exists():
        raise FileExistsError(target)
    target.write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output))


if __name__ == '__main__':
    main()
