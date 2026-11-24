"""Physical/source/provenance and paired-language checks; no framework execution."""
import ast
import datetime
import hashlib
import json
from pathlib import Path
import re

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
pack_path = P / 'mlx-admission-chapter-source-pack-v1.json'
ledger_path = P / 'mlx-admission-chapter-ledger-v3.json'
pack, ledger = json.loads(pack_path.read_text()), json.loads(ledger_path.read_text())
checks = []

def check(name, condition):
    checks.append({'check': name, 'pass': bool(condition)})
    assert condition, name

tree = json.loads((P / 'mlx-lm-pinned-adapter-tree-v1.json').read_text())
blobs = {row['path']: row['sha'] for row in tree['tree'] if row['type'] == 'blob'}
for row in pack['sources']:
    raw = (ROOT / row['path']).read_bytes()
    check('source-sha:' + row['upstream_path'], hashlib.sha256(raw).hexdigest() == row['sha256'])
    check('git-blob:' + row['upstream_path'], hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == blobs[row['upstream_path']] == row['git_blob'])
for key, unit in pack['units'].items():
    raw = (ROOT / unit['path']).read_bytes()
    lines = raw.decode().splitlines(keepends=True)
    quote = ''.join(lines[unit['first_line'] - 1:unit['last_line']])
    check('physical-quote:' + key, quote == unit['quote'] and hashlib.sha256(quote.encode()).hexdigest() == unit['quote_sha256'])
    check('revision-url:' + key, unit['revision'] == pack['revision'] and '/blob/' + pack['revision'] + '/' + unit['upstream_path'] in unit['git_url'])
for claim in ledger['claims']:
    check('paired-code:' + claim['id'], re.findall(r'`([^`]+)`', claim['en']) == re.findall(r'`([^`]+)`', claim['pt-br']))
    check('registered-evidence:' + claim['id'], bool(claim['evidence_ids']) and all(identity in pack['units'] for identity in claim['evidence_ids']))
    for name in claim['observation_artifacts']:
        check('observation-exists:' + claim['id'] + ':' + name, (P / name).is_file())
claims = {claim['id']: claim for claim in ledger['claims']}
for faq in ledger['faq']:
    check('faq-parent:' + faq['id'], len(faq['claim_ids']) == 1 and faq['claim_ids'][0] in claims)
    parent = claims[faq['claim_ids'][0]]
    check('faq-answer-and-citations:' + faq['id'], faq['answer'] == {language: parent[language] for language in ['en', 'pt-br']} and faq['evidence_ids'] == parent['evidence_ids'])
    check('faq-not-approved:' + faq['id'], all(faq[flag] is False for flag in ['owner_approved', 'training_gold', 'training_use_approved']))
for file in ledger['files']:
    relative = Path(file['path'])
    assert not relative.is_absolute() and '..' not in relative.parts and '\\' not in file['path']
    path = ROOT / relative
    raw = path.read_bytes()
    check('candidate-hash:' + path.name, hashlib.sha256(raw).hexdigest() == file['sha256'])
    language = path.stem
    text = raw.decode()
    for claim in ledger['claims']:
        check('claim-in-document:' + language + ':' + claim['id'], claim[language] in text)
    for faq in ledger['faq']:
        check('faq-in-document:' + language + ':' + faq['id'], faq['question'][language] in text and faq['answer'][language] in text)
    examples = re.findall(r'```json\n(.*?)\n```', text, re.S)
    check('owned-review-example:' + language, len(examples) == 1 and json.loads(examples[0]) == ledger['example'])
    check('no-launch-command-block:' + language, '```sh' not in text and '```bash' not in text and 'python -m' not in text)
check('source-pack-bound:', ledger['source_pack_sha256'] == hashlib.sha256(pack_path.read_bytes()).hexdigest())
check('license:', hashlib.sha256((ROOT / pack['license']['path']).read_bytes()).hexdigest() == pack['license']['sha256'])
check('no-training-or-publication-authority:', all(ledger[name] is False for name in ['owner_approved', 'training_gold', 'training_use_approved', 'publication_authorized', 'automatic_candidate_applier_supported', 'full_framework_execution']))

manual = [
    ('purpose', 'Both texts distinguish source imports from isolated pure execution and exclude actual framework/model/trainer execution.'),
    ('entry-order', 'Both preserve loading-before-mode-check ordering and distinguish static risk from observed download.'),
    ('merge', 'Both preserve None-only precedence, concrete false/zero defaults and the downstream-validation limit.'),
    ('format-admission', 'Both preserve format precedence, false approval flags, frozen-schema distinction and the two owned failures.'),
    ('local-remote', 'Both preserve missing-vs-present-empty subset behavior, nonexistent-local fallback and empty-validation warning.'),
    ('mask-interface', 'Both preserve last-message/prefix-call roles and deny interpreting raw intervals as actual supervision.'),
    ('batch-arithmetic', 'Both preserve conditional inclusive-bound arithmetic and the absence of actual MLX loss measurement.'),
    ('cache', 'Both preserve raw1/4 versus processed11/3, sort reversal and no performance conclusion.'),
    ('concatenation', 'Both preserve original-row mutation, held-row rerouting,2+3 versus8 observation and native-batching limitation.'),
    ('selection', 'Both preserve omitted-vs-empty keys, zero/negative whole-list slice and separate global-path pass.'),
    ('scale-shapes', 'Both preserve A/B direction, self.scale before local reuse, no rank division and custom-hook limitation.'),
    ('conditional-counts', 'Both preserve conditional2layers/rank4 counts434176/81920 and all unmeasured memory components.'),
    ('resume', 'Both limit the claim to the inspected weights-only payload and new optimizer; no blanket claim about every callback.'),
    ('review-boundary', 'Both preserve rights/owner/evaluation unapproved, data-only example, no launch command and NO-GO.'),
]
record = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'status': 'PHYSICAL_CHECKS_PASS_WITH_EXPLICIT_AGENT_LANGUAGE_REVIEW',
          'source_pack_sha256': hashlib.sha256(pack_path.read_bytes()).hexdigest(),
          'ledger_sha256': hashlib.sha256(ledger_path.read_bytes()).hexdigest(), 'checks': checks,
          'passes': sum(row['pass'] for row in checks), 'count': len(checks),
          'manual_language_review': [{'claim_id': identity, 'assessment': description, 'reviewer': 'campaign-agent', 'owner_approved': False} for identity, description in manual],
          'manual_review_independence': False, 'semantic_equivalence_certified': False,
          'automated_semantic_entailment_claimed': False, 'new_source_execution': False, 'model_calls': 0,
          'training_gold': False, 'publication': False,
          'limitations': 'Structural checks do not prove every prose claim. Agent language review is not an independent reviewer, owner approval, real tokenizer/framework observation or neural holdout.'}
with (P / 'mlx-admission-chapter-verification-v2.json').open('x') as stream:
    json.dump(record, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({'passes': record['passes'], 'checks': len(checks), 'manual_claim_reviews': len(manual), 'owner_gold': 0}))
