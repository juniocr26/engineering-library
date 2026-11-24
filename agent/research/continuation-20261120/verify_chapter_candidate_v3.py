"""Verify physical provenance and bilingual syntax invariants, not prose entailment."""
import datetime
import hashlib
import json
from pathlib import Path
import re

P = Path(__file__).resolve().parent
ledger = json.loads((P / 'jmespath-chapter-ledger-v3.json').read_text())
pack_path = P / 'jmespath-source-evidence-pack-v1.json'
pack = json.loads(pack_path.read_text())
checks = {'source_pack_identity': hashlib.sha256(pack_path.read_bytes()).hexdigest() == ledger['source_pack_sha256']}
base = P / 'new-public-sources-v1/jmespath--jmespath.py' / pack['revision']
for identifier, unit in pack['units'].items():
    raw = (base / unit['source_path']).read_bytes()
    e = unit['evidence']
    quote = ''.join(raw.decode().splitlines(keepends=True)[e['first_line'] - 1:e['last_line']])
    checks['physical_source:' + identifier] = hashlib.sha256(raw).hexdigest() == unit['source_sha256'] and quote == e['quote'] and hashlib.sha256(quote.encode()).hexdigest() == e['quote_sha256']
texts = {}
for path, expected in ledger['files'].items():
    raw = (P / path).read_bytes();lang = Path(path).stem;texts[lang] = raw.decode()
    checks['candidate_identity:' + lang] = len(raw) == expected['bytes'] and hashlib.sha256(raw).hexdigest() == expected['sha256']
    refs = re.findall(r'\[source:([^\]]+)\]', raw.decode())
    checks['registered_references:' + lang] = bool(refs) and all(ref in pack['units'] for ref in refs)
    for claim in ledger['claims']:
        checks['ledger_text:' + lang + ':' + claim['id']] = claim[lang] in raw.decode()
    for faq in ledger['faq']:
        checks['faq_question_and_answer:' + lang + ':' + faq['id']] = faq[lang + '_q'] in raw.decode() and faq[lang + '_a'] in raw.decode()
    # Commands and examples are syntax checked without invoking the command or example.
    snippet = re.search(r'```python\n(.*?)\n```', raw.decode(), re.S).group(1)
    compile(snippet, 'candidate-illustrative-example', 'exec', dont_inherit=True)
    checks['example_static_syntax:' + lang] = True
checks['all_inline_identifiers_identical'] = re.findall(r'`([^`\n]+)`', texts['en']) == re.findall(r'`([^`\n]+)`', texts['pt-br'])
checks['code_blocks_identical'] = re.findall(r'```[^\n]*\n(.*?)\n```', texts['en'], re.S) == re.findall(r'```[^\n]*\n(.*?)\n```', texts['pt-br'], re.S)
checks['faq_count_both_six'] = all(len(re.findall(r'^### ', t, re.M)) == 6 for t in texts.values())
checks['no_owner_or_training_promotion'] = ledger['owner_approved'] is False and ledger['training_gold'] is False and ledger['training_exclusion'] is True
report = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'checks': checks,
          'all_checks_pass': all(checks.values()), 'checks_count': len(checks),
          'scope': 'Physical source identity, registered citations, renderer text identity and bilingual code invariants only.',
          'general_prose_entailment_validated': False, 'semantic_equivalence_certified': False,
          'runtime_examples_executed': False, 'publication_authorized': False,
          'manual_agent_source_review': {'claims': 9, 'faq_pairs': 6, 'revision': 'v3',
              'findings': ['V3 revises the remaining facade-vs-cache lifecycle question to written-cache-size; V2 source-fact validity did not establish question relevance. The prior entry-point question correction is retained.',
                           'Class value512 and parser-error owner refer to pinned physical units.',
                           'Unknown guarantees remain explicit; no fixed output type inferred from source calls.',
                           'Source-family exposure and FAQ/chapter overlap exclude this material from training.']}}
with (P / 'chapter-candidate-verification-v3.json').open('x') as stream:
    json.dump(report, stream, indent=2)
print(json.dumps({'all_checks_pass': report['all_checks_pass'], 'checks_count': len(checks), 'failed': [k for k,v in checks.items() if not v]}))
