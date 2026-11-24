"""Verify physical, paired-code and ledger identity; semantic review remains manual."""
import datetime
import hashlib
import json
from pathlib import Path
import re

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
ledger_path = P / 'boltons-chapter-ledger-v2.json'
ledger = json.loads(ledger_path.read_text())
sha = lambda raw: hashlib.sha256(raw).hexdigest()
checks = {}
for key, unit in ledger['units'].items():
    raw = (ROOT / unit['path']).read_bytes()
    quote = ''.join(raw.decode().splitlines(keepends=True)[unit['first_line'] - 1:unit['last_line']])
    checks['source:' + key] = sha(raw) == unit['source_sha256'] and quote == unit['quote'] and sha(quote.encode()) == unit['quote_sha256']
    checks['quote_bound:' + key] = len(quote.encode()) <= 6144
for name, receipt in ledger['runtime_receipts'].items():
    raw = (P / name).read_bytes()
    result = json.loads(raw)
    checks['runtime_receipt:' + name] = sha(raw) == receipt['sha256'] and result['correct'] == result['n'] and result['whole_public_module_imported'] is False
texts = {}
for file, expected in ledger['files'].items():
    path = P / file
    raw = path.read_bytes()
    checks['file_identity:' + file] = sha(raw) == expected['sha256'] and len(raw) == expected['bytes']
    if path.suffix != '.md':
        compile(raw, '<illustrative-only>', 'exec', dont_inherit=True)
        checks['example_static_syntax'] = True
        continue
    language = path.stem
    text = raw.decode()
    texts[language] = text
    for claim in ledger['claims']:
        checks['claim_text:' + language + ':' + claim['id']] = claim[language] in text
    for faq in ledger['faq']:
        checks['faq_text:' + language + ':' + faq['id']] = faq[language + '_q'] in text and faq[language + '_a'] in text
    checks['license_visible_link:' + language] = bool(re.search(r'^\[source-license\]$', text, re.M))
    for identifier, target in re.findall(r'^\[([^\]]+)\]: (\S+)', text, re.M):
        relative = target.split('#')[0]
        checks['physical_link:' + language + ':' + identifier] = (path.parent / relative).resolve().is_file()
checks['paired_inline_code'] = re.findall(r'`([^`\n]+)`', texts['en']) == re.findall(r'`([^`\n]+)`', texts['pt-br'])
checks['paired_code_blocks'] = re.findall(r'```[^\n]*\n(.*?)\n```', texts['en'], re.S) == re.findall(r'```[^\n]*\n(.*?)\n```', texts['pt-br'], re.S)
checks['seven_faqs_each'] = all(len(re.findall(r'^### ', text, re.M)) == 7 for text in texts.values())
checks['not_gold_or_published'] = ledger['owner_approved'] is False and ledger['training_gold'] is False and ledger['training_exclusion'] is True and ledger['published'] is False
record = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'ledger_sha256': sha(ledger_path.read_bytes()), 'checks': checks, 'checks_count': len(checks), 'all_passed': all(checks.values()), 'manual_question_relevance_review': {'reviewer': 'Codex', 'question_pairs': 7, 'conclusion': 'Each question is addressed by its assigned source/observation claim; not independent human review.'}, 'full_prose_entailment_or_semantic_equivalence_certified': False, 'example_executed': False, 'source_execution_scope': 'Only rotate_file and iter_find_files in the preserved restricted-facade receipts; no whole module imports or additional library execution during chapter generation/verification.'}
with (P / 'boltons-chapter-verification-v2.json').open('x') as stream:
    stream.write(json.dumps(record, indent=2) + '\n')
print(json.dumps({'checks': len(checks), 'all_passed': record['all_passed'], 'failed': [k for k, v in checks.items() if not v]}))
