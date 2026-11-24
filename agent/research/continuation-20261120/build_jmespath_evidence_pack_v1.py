"""Assemble pinned physical source units for an isolated source-reviewed chapter."""
import ast
import datetime
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent
REV = '6ff419a8b171d055a9bfc6904605bceb8b7a80ef'
BASE = P / 'new-public-sources-v1/jmespath--jmespath.py' / REV
observations = json.loads((P / 'jmespath-class-member-observations-v1.json').read_text())
signatures = json.loads((P / 'new-public-signatures-v1.json').read_text())
units = {}


def add(key, path, evidence, kind):
    raw = (BASE / path).read_bytes()
    lines = raw.decode().splitlines(keepends=True)
    text = ''.join(lines[evidence['first_line'] - 1:evidence['last_line']])
    if text != evidence['quote'] or hashlib.sha256(text.encode()).hexdigest() != evidence['quote_sha256']:
        raise ValueError('physical evidence mismatch: ' + key)
    if len(text.encode()) > 6144:
        raise ValueError('source quote bound exceeded')
    units[key] = {'source_path': path, 'revision': REV, 'source_sha256': hashlib.sha256(raw).hexdigest(),
                  'kind': kind, 'source_executed': False, 'runtime_bindings_verified': False,
                  'url': 'https://github.com/jmespath/jmespath.py/blob/' + REV + '/' + path + '#L' + str(evidence['first_line']) + '-L' + str(evidence['last_line']),
                  'evidence': dict(evidence)}


for row in observations['rows']:
    if row['revision'] == REV and row['result']['status'] == 'WRITTEN_CLASS_MEMBER':
        r = row['result']
        add(row['selector'], 'jmespath/parser.py', r['evidence'], 'direct-written-class-member')
for row in signatures['cases']:
    if row['language'] == 'python' and row['id'].startswith('jmespath-6ff419a'):
        r = row['result']
        # Shared observer evidence is physical lines and quote but no byte offsets required here.
        add(row['id'].rsplit('-', 1)[-1], 'jmespath/__init__.py', r['evidence'], 'module-callable')
for path in ['jmespath/__init__.py', 'jmespath/parser.py']:
    text = (BASE / path).read_text()
    lines = text.splitlines(keepends=True)
    for node in ast.parse(text).body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            quote = ''.join(lines[node.lineno - 1:node.end_lineno])
            add(path + ':import:' + str(node.lineno), path,
                {'first_line': node.lineno, 'last_line': node.end_lineno, 'quote': quote,
                 'quote_sha256': hashlib.sha256(quote.encode()).hexdigest()}, 'written-import')
size = sum(len(r['evidence']['quote'].encode()) for r in units.values())
if size > 24576:
    raise ValueError('source context pack bound exceeded')
packet = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'repository': 'jmespath/jmespath.py',
          'revision': REV, 'units': units, 'quote_bytes': size, 'context_bound': 24576,
          'training_exclusion': True, 'owner_approved': False,
          'license_path': str((BASE / 'LICENSE').relative_to(P)),
          'license_sha256': hashlib.sha256((BASE / 'LICENSE').read_bytes()).hexdigest(),
          'runtime_import_resolution_verified': False,
          'relationship_scope': 'Written imports and spelled calls between pinned local files, not verified Python import-loader/runtime identity.'}
with (P / 'jmespath-source-evidence-pack-v1.json').open('x') as stream:
    json.dump(packet, stream, indent=2)
print(json.dumps({'units': len(units), 'quote_bytes': size}))
