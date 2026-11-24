"""Exact candidate syntax and selected lexical stores; no target execution."""
from pathlib import Path
import argparse
import ast
import datetime
import hashlib
import json
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
parser.add_argument('--stdout-only', action='store_true')
args = parser.parse_args()
P = args.root/'agent/research/final-intensive-20261121'
sys.dont_write_bytecode = True
sys.path.insert(0, str(args.root/'agent/tools'))
import go_source_ast

sha = lambda b: hashlib.sha256(b).hexdigest()
protocol = json.loads((P/'priority-pair-example-observation-protocol-v1.json').read_text())
by_topic = {}
for case in protocol['cases']:
    assert sha((args.root/case['path']).read_bytes()) == case['document_sha256']
    assert sha(case['code'].encode()) == case['code_sha256']
    by_topic.setdefault(case['topic'], []).append(case['code'])
assert all(codes[0] == codes[1] for codes in by_topic.values())
ast.parse(by_topic['fastapi-cache'][0])
python_negative = False
try:
    ast.parse('async def owned_example(:\n    pass\n')
except SyntaxError:
    python_negative = True
assert python_negative
source = (P/'reacquired-public-sources/fastapi/fastapi/dependencies/utils.py').read_text()
module = ast.parse(source)
solver = next(node for node in module.body if isinstance(node, ast.AsyncFunctionDef) and node.name == 'solve_dependencies')


def owned_nodes(owner):
    for child in ast.iter_child_nodes(owner):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            continue
        yield child
        yield from owned_nodes(child)


stores = [node.lineno for node in owned_nodes(solver)
          if isinstance(node, ast.Name) and node.id == 'dependency_cache' and isinstance(node.ctx, ast.Store)]
assert stores == [701]
wrapped = ('package ownedexample\nimport cobra "github.com/spf13/cobra"\n'
           'func reviewExample() {\n'+by_topic['cobra-validation'][0]+'\n}\n')
request = {'source': wrapped, 'path':'owned_example.go', 'selectors':['reviewExample']}
native = go_source_ast.run(json.dumps(request).encode())
assert len(native['units']) == 1 and native['source_executed'] is False
go_negative = False
try:
    go_source_ast.run(json.dumps({'source':'package ownedexample\nfunc reviewExample( {',
                                 'path':'owned_bad.go','selectors':['reviewExample']}).encode())
except ValueError as error:
    go_negative = str(error)
assert go_negative
result = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'protocol_sha256':sha((P/'priority-pair-example-observation-protocol-v1.json').read_bytes()),
          'python_example_syntax_valid':True, 'python_owned_malformed_refused':python_negative,
          'solver_direct_dependency_cache_store_lines':stores,
          'go_owned_wrapped_input':request, 'go_native_result':native,
          'go_owned_malformed_refusal':go_negative, 'target_code_executed':False,
          'typecheck_or_import_resolution':False, 'neural_calls':0,
          'scope':'Exact candidate examples syntax; one selected lexical store query. Not application suites, semantic model accuracy or whole-function runtime proof.'}
if not args.stdout_only:
    with (P/'priority-pair-example-observation-results-v1.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
print(json.dumps(result))
