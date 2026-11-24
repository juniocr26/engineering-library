"""Owned Go cache/receipt substitutions through the actual HelperRetrieval API."""
import copy
import datetime
import hashlib
import json
from pathlib import Path
import sys
import time

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
sys.path.insert(0, str(ROOT / 'agent/tools'))
import documentation_retrieval as retrieval

phase = sys.argv[1]
assert phase in ['baseline', 'candidate']
oracle_path = P / 'helper-go-cached-unit-oracle-v2.json'
oracle = json.loads(oracle_path.read_text())
if phase == 'baseline':
    assert hashlib.sha256(Path(retrieval.__file__).read_bytes()).hexdigest() == oracle['current_tool_sha256']
out = P / ('helper-go-cached-controls-' + phase + '-v2')
out.mkdir(exist_ok=False)
rows = []
source = oracle['source']
raw = source.encode()
assert hashlib.sha256(raw).hexdigest() == oracle['source_sha256']
for case in oracle['cases']:
    owned = out / case['id']
    source_root, journal = owned / 'source', owned / 'journal'
    source_root.mkdir(parents=True)
    journal.mkdir()
    (source_root / 'owned.go').write_bytes(raw)
    selectors = ['owned.Selected', 'Other', 'One.Selected', 'Two.Selected']
    registry = {'owned': {'root': str(source_root.resolve()), 'revision': 'b' * 40,
                         'files': {'owned.go': {'sha256': oracle['source_sha256'], 'language': 'go', 'selectors': selectors}}}}
    request = {'request_id': 'selected-callable', 'source_id': 'owned', 'revision': 'b' * 40,
               'path': 'owned.go', 'qualified_symbol': case['selector'], 'expected_sha256': oracle['source_sha256']}
    helper = retrieval.HelperRetrieval(registry, str(journal.resolve()))
    initial = helper.request(request)
    assert initial['status'] == 'FOUND', initial
    result_path, receipt_path = journal / 'selected-callable.result.json', journal / 'selected-callable.receipt.json'
    before = result_path.read_bytes()
    cached = json.loads(before)
    unit = cached['evidence']
    mutation = case['mutation']
    if mutation in ['other-callable', 'other-receiver']:
        unit.update(retrieval.extract(source, 'Other' if mutation == 'other-callable' else 'Two.Selected', 'go'))
        unit['selector'] = case['selector']
    elif mutation in ['body-only', 'whole-module']:
        lines = raw.split(b'\n')
        first, last = (unit['first_line'] + 1, unit['first_line'] + 1) if mutation == 'body-only' else (1, len(lines))
        quote = b'\n'.join(lines[first - 1:last])
        unit.update(first_line=first, last_line=last, quote=quote.decode(), quote_sha256=retrieval.sha(quote))
    elif mutation == 'kind':
        unit['declaration_kind'] = 'method'
    elif mutation == 'producer':
        unit['producer']['binary_sha256'] = '0' * 64
    elif mutation == 'limitations':
        unit['limitations'] = ['Owned contradictory claim: complete runtime identity verified.']
    else:
        assert mutation == 'none'
    cached['quote_bytes'] = len(unit['quote'].encode())
    cached['cumulative_quote_bytes'] = cached['quote_bytes']
    encoded = retrieval.canonical(cached)
    result_path.write_bytes(encoded)
    receipt = retrieval.receipt_for(encoded, retrieval.canonical(request), helper.registry_sha256, oracle['source_sha256'], cached['extractor_identity'])
    receipt_path.write_bytes(retrieval.canonical(receipt))
    (owned / 'before-controlled-rewrite.json').write_bytes(before)
    (owned / 'inputs.json').write_text(json.dumps({'request': request, 'registry': registry, 'mutation': mutation}, indent=2) + '\n')
    started = time.monotonic()
    observed = retrieval.HelperRetrieval(registry, str(journal.resolve())).request(request)
    rows.append({'id': case['id'], 'expected_status': case['expected_status'], 'observed': observed,
                 'matches': observed['status'] == case['expected_status'], 'readback_seconds': time.monotonic() - started,
                 'source_unchanged': hashlib.sha256((source_root / 'owned.go').read_bytes()).hexdigest() == oracle['source_sha256'],
                 'coordinated_owned_cache_and_receipt_rewrite': mutation != 'none'})
record = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'phase': phase, 'tool_version': retrieval.VERSION,
          'tool_sha256': hashlib.sha256(Path(retrieval.__file__).read_bytes()).hexdigest(),
          'oracle_sha256': hashlib.sha256(oracle_path.read_bytes()).hexdigest(), 'rows': rows,
          'correct': sum(row['matches'] for row in rows), 'count': len(rows), 'source_executed': False,
          'model_calls': 0, 'permanent_tests_changed': False, 'independent_public_evaluation': False,
          'scope': 'Exact existing verified Go AST parser; selected owned source parsed only. Cache integrity does not establish runtime bindings or external adversarial access.'}
with (P / ('helper-go-cached-unit-results-' + phase + '-v2.json')).open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
print(json.dumps({'phase': phase, 'tool_version': retrieval.VERSION, 'correct': record['correct'], 'count': len(rows),
                  'misses': [row['id'] for row in rows if not row['matches']]}))
