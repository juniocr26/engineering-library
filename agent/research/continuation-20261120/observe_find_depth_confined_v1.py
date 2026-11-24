"""Run the exact selected generator under an owned native-walk observation facade."""
import ast
import datetime
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import platform
import posixpath
import re
import stat
import sys
import types

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def observe(root_override=None):
    protocol = json.loads((P / 'find-depth-confined-protocol-v1.json').read_text())
    raw = (ROOT / protocol['source_path']).read_bytes()
    assert sha(raw) == protocol['source_sha256']
    nodes = [n for n in ast.parse(raw.decode()).body if isinstance(n, ast.FunctionDef) and n.name == protocol['selector']]
    assert len(nodes) == 1
    node = nodes[0]
    quote = ''.join(raw.decode().splitlines(keepends=True)[node.lineno - 1:node.end_lineno])
    assert sha(quote.encode()) == protocol['quote_sha256']
    assert node.decorator_list == [] and not node.args.kwarg and not node.args.vararg
    assert [a.arg for a in node.args.args] == ['directory', 'patterns', 'ignored', 'include_dirs', 'max_depth']
    assert [ast.literal_eval(v) for v in node.args.defaults] == [None, False, None]
    assert sorted({ast.unparse(n.func) for n in ast.walk(node) if isinstance(n, ast.Call)}) == protocol['calls']
    assert not any(isinstance(n, (ast.Import, ast.ImportFrom, ast.ClassDef, ast.Global, ast.Nonlocal, ast.While, ast.Try, ast.With, ast.Lambda)) for n in ast.walk(node))
    assert sum(isinstance(n, ast.FunctionDef) for n in ast.walk(node)) == 1
    assert sum(1 for _ in ast.walk(node)) < 600
    allowed = {'os.walk', 'os.path', 'os.path.sep', 'os.path.join', 're.compile', 'fnmatch.translate', "'|'.join", 'directory.split', 'root.split', 'pats_re.match', 'ign_re.match'}
    assert all(ast.unparse(n) in allowed for n in ast.walk(node) if isinstance(n, ast.Attribute))
    code = compile(ast.Module(body=[node], type_ignores=[]), '<exact-reviewed-iter_find_files>', 'exec')
    base = Path(root_override or '/private/tmp/el-find-depth-confined-20261120-macos-v1')
    base.mkdir(mode=0o700, exist_ok=False)
    rows = []
    for case in protocol['cases']:
        owned = base / case['id']
        owned.mkdir()
        tree = owned / 'tree'
        (tree / 'deep/nested').mkdir(parents=True)
        names = ['root.txt', 'root.skip', 'deep/deep.txt', 'deep/nested/leaf.txt']
        for name in names:
            (tree / name).write_text('OWNED DEPTH CONTROL: ' + name + '\n')
        before = {str(p.relative_to(owned)): sha(p.read_bytes()) for p in tree.rglob('*') if p.is_file()}
        walk_calls = []

        def walk(directory):
            if directory != 'tree':
                raise ValueError('facade requires the single owned tree')
            for actual_root, dirs, files in os.walk(tree, topdown=True, followlinks=False):
                root = 'tree' + ('' if Path(actual_root) == tree else '/' + str(Path(actual_root).relative_to(tree)))
                if root not in protocol['expected_native_roots_for_every_case']:
                    raise ValueError('native walker escaped the registered three-directory tree')
                for name in dirs + files:
                    entry = os.lstat(Path(actual_root) / name)
                    if stat.S_ISLNK(entry.st_mode):
                        raise ValueError('facade does not admit symlinks')
                event = {'root': root, 'dirs_before_consumer': list(dirs), 'files': list(files)}
                walk_calls.append(event)
                if len(walk_calls) > 3:
                    raise ValueError('tree cardinality exceeded')
                yield root, dirs, files
                event['dirs_after_consumer'] = list(dirs)

        facade = types.SimpleNamespace(walk=walk, path=types.SimpleNamespace(sep='/', join=posixpath.join))
        namespace = {'__builtins__': {'isinstance': isinstance, 'str': str, 'len': len}, 'os': facade, 're': re, 'fnmatch': fnmatch}
        exec(code, namespace)
        result = list(namespace['iter_find_files']('tree', case.get('patterns', '*.txt'), ignored=case.get('ignored'), include_dirs=case.get('include_dirs', False), max_depth=case['max_depth']))
        after = {str(p.relative_to(owned)): sha(p.read_bytes()) for p in tree.rglob('*') if p.is_file()}
        unchanged_dirs = all(e['dirs_before_consumer'] == e['dirs_after_consumer'] for e in walk_calls)
        roots_match = [e['root'] for e in walk_calls] == protocol['expected_native_roots_for_every_case']
        matches = sorted(result) == sorted(case['expected_yields']) and roots_match and unchanged_dirs and before == after
        rows.append({'id': case['id'], 'matches': matches, 'expected_yields': case['expected_yields'], 'observed_yields_in_native_order': result, 'walk_events': walk_calls, 'all_three_roots_visited': roots_match, 'native_dirs_not_pruned_by_consumer': unchanged_dirs, 'owned_file_hashes_before': before, 'owned_file_hashes_after': after, 'public_function_executed': True, 'whole_module_imported': False, 'source_file_modified': False})
    return {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'platform': platform.platform(), 'python': sys.version, 'source_revision': protocol['source_revision'], 'source_sha256': protocol['source_sha256'], 'quote_sha256': protocol['quote_sha256'], 'owned_root': str(base), 'correct': sum(r['matches'] for r in rows), 'n': len(rows), 'rows': rows, 'selected_public_generator_executed': True, 'whole_public_module_imported': False, 'only_owned_temporary_tree_traversed': True, 'source_or_user_files_written': False, 'model_calls': 0, 'neural_training': False, 'windows_verified': False, 'limits': protocol['scope_limits']}


if __name__ == '__main__':
    record = observe()
    with (P / 'find-depth-confined-macos-v1.json').open('x') as stream:
        stream.write(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'correct': record['correct'], 'n': record['n'], 'all_roots_visited_every_case': all(r['all_three_roots_visited'] for r in record['rows']), 'dirs_never_pruned': all(r['native_dirs_not_pruned_by_consumer'] for r in record['rows']), 'public_function_executed': True, 'only_owned_tree_traversed': True}))
