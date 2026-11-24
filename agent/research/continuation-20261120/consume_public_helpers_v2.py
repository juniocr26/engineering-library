"""Actual optional HelperRetrieval consumer; isolated research, no Ruby routing."""
import datetime
import hashlib
import json
from pathlib import Path
import sys

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
sys.path.insert(0, str(ROOT / 'agent/tools'))
from documentation_retrieval import HelperRetrieval


def main():
    rev = '6ff419a8b171d055a9bfc6904605bceb8b7a80ef'
    source_root = (P / 'new-public-sources-v1/jmespath--jmespath.py' / rev).resolve()
    journal = (P / 'helper-journal-public-v1').resolve()
    if not journal.is_dir(): raise ValueError("explicit recovery journal required")
    files = {
        'jmespath/__init__.py': ['compile', 'search'],
        'jmespath/parser.py': ['Parser.parse', 'Parser._do_parse', 'ParsedResult.search'],
    }
    registry = {'jmespath': {'root': str(source_root), 'revision': rev, 'files': {
        name: {'sha256': hashlib.sha256((source_root / name).read_bytes()).hexdigest(),
               'language': 'python', 'selectors': selectors}
        for name, selectors in files.items()}}}
    registry_path = P / 'helper-public-registry-v1.json'
    if json.loads(registry_path.read_text()) != registry: raise ValueError('registry changed during recovery')
    prior_raw = (journal / 'facade-compile.result.json').read_bytes()
    prior_receipt = json.loads((journal / 'facade-compile.receipt.json').read_text())
    if hashlib.sha256(prior_raw).hexdigest() != prior_receipt['result_sha256']:
        raise ValueError('durable first result receipt mismatch')
    prior = json.loads(prior_raw)
    if prior['status'] != 'FOUND' or prior['step_count'] != 1:
        raise ValueError('unexpected first operation state')
    helper = HelperRetrieval(registry, str(journal), max_steps=3, max_quote_bytes=24576-prior['quote_bytes'])
    plans = [('facade-compile', 'jmespath/__init__.py', 'compile'),
             ('facade-search', 'jmespath/__init__.py', 'search'),
             ('parser-cache', 'jmespath/parser.py', 'Parser.parse'),
             ('parser-errors', 'jmespath/parser.py', 'Parser._do_parse'),
             ('result-search-outside-budget', 'jmespath/parser.py', 'ParsedResult.search')]
    pack = json.loads((P / 'jmespath-source-evidence-pack-v1.json').read_text())
    rows = []
    for rid, path, selector in plans:
        request = {'request_id': rid, 'source_id': 'jmespath', 'revision': rev, 'path': path,
                   'qualified_symbol': selector, 'expected_sha256': registry['jmespath']['files'][path]['sha256']}
        result = helper.request(request)
        recovery_validation = None
        if rid == 'facade-compile':
            recovery_validation = result
            if result['status'] != 'DUPLICATE' or result.get('original_status') != 'FOUND':
                raise ValueError('first durable result not revalidated as completed duplicate')
            result = prior
        expected = 'FOUND' if rid != 'result-search-outside-budget' else 'BUDGET_EXHAUSTED'
        matches = result['status'] == expected
        if result['status'] == 'FOUND':
            e = result['evidence'];physical = pack['units'][selector]['evidence']
            matches = matches and e['quote'] == physical['quote'] and e['first_line'] == physical['first_line'] and e['last_line'] == physical['last_line']
        rows.append({'request': request, 'expected_status': expected, 'matches': matches, 'result': result, 'recovery_validation': recovery_validation})
    receipt = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'rows': rows,
               'steps': 1+helper.steps, 'quote_bytes': prior['quote_bytes']+helper.quote_bytes, 'recovered_prior_steps': 1, 'new_steps': helper.steps,
               'correct': sum(r['matches'] for r in rows), 'n': len(rows),
               'source_executed': False, 'model_calls': 0, 'ruby_generation_routing_changed': False,
               'scope': 'Actual direct research consumer of optional Python API; not autonomous model tool use.',
               'full_chapter_helper_only_coverage': False,
               'coverage_limit': 'Four budgeted callable quotes; class constant/import units remain separate static evidence. Fifth callable must remain unavailable to this helper session.'}
    with (P / 'helper-public-consumption-v2.json').open('x') as stream:
        json.dump(receipt, stream, indent=2)
    print(json.dumps({'statuses': [r['result']['status'] for r in rows], 'matches': receipt['correct'], 'n': len(rows), 'steps': 1+helper.steps, 'quote_bytes': prior['quote_bytes']+helper.quote_bytes, 'recovered_prior_steps': 1, 'new_steps': helper.steps}))


if __name__ == '__main__':
    main()
