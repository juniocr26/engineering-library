"""Freeze a finite acceptance-receipt integrity study, not a semantic benchmark."""
from pathlib import Path
import datetime
import hashlib
import json

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
PRIOR = ROOT/'agent/research/acceptance-calibration-20261121'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, data):
    with path.open('x') as stream:
        json.dump(data, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def edge(path, role):
    raw = path.read_bytes()
    return {'path': str(path.relative_to(ROOT)), 'role': role, 'sha256': sha(raw), 'bytes': len(raw)}


protocol = json.loads((PRIOR/'verified-fact-render-protocol-v1.json').read_text())
refs = json.loads((PRIOR/'atomic-reference-ledger-v2.json').read_text())['claims']
bundles = {}
for task in ['fastapi', 'cobra', 'zod']:
    folder = PRIOR/'verified-fact-render-v1'/task/'K'
    dependencies = [edge(folder/name, role) for name, role in [
        ('rendered-note-v1.json', 'candidate'), ('semantic-review-v1.json', 'semantic_review'),
        ('complete-note-review-v1.json', 'complete_review'), ('model-content.txt', 'model_content'),
        ('request.json', 'request'), ('raw-response.json', 'raw_response'), ('outcome.json', 'outcome')]]
    dependencies += [edge(PRIOR/name, role) for name, role in [
        ('acceptance-protocol-v2.json', 'acceptance_criteria'),
        ('verified-fact-render-protocol-v1.json', 'generation_protocol'),
        ('atomic-reference-ledger-v2.json', 'references')]]
    for path in sorted({r['source_path'] for r in refs if r['task'] == task}):
        dependencies.append(edge(PRIOR/'frozen-public-sources'/task/path, 'source'))
    bundles[task] = {
        'task': task, 'source_identity': {k: protocol['metadata'][task][k] for k in ['family', 'revision', 'required_ids']},
        'dependencies': dependencies,
        'allowed_status': 'HISTORICAL_RESEARCH_REVIEW_BINDINGS_VALID',
        'review_independence': 'same-agent; separate source acquisition only',
        'owner_approved': False, 'publication_approved': False, 'training_gold_approved': False,
        'dataset_role': 'DEVELOPMENT_EXPOSED_TRAINING_EXCLUDED',
    }
save(P/'trusted-binding-anchor-v1.json', bundles)
cases = []
for task in bundles:
    # Mutations are overlay payloads; originals are never rewritten.
    variants = [
        ('unchanged', 'identity', None, 'VALID'),
        ('missing-candidate', 'missing_role', 'candidate', 'REFUSED'),
        ('changed-candidate', 'append_bytes', 'candidate', 'REFUSED'),
        ('changed-source', 'append_bytes', 'source', 'REFUSED'),
        ('changed-criteria', 'append_bytes', 'acceptance_criteria', 'REFUSED'),
        ('changed-reference', 'append_bytes', 'references', 'REFUSED'),
        ('changed-review', 'append_bytes', 'semantic_review', 'REFUSED'),
        ('changed-complete-review', 'append_bytes', 'complete_review', 'REFUSED'),
        ('changed-request', 'append_bytes', 'request', 'REFUSED'),
        ('changed-response', 'append_bytes', 'raw_response', 'REFUSED'),
        ('changed-content', 'append_bytes', 'model_content', 'REFUSED'),
        ('wrong-revision', 'change_envelope', ['source_identity', 'revision', '0'*40], 'REFUSED'),
        ('dropped-requirement', 'drop_requirement', None, 'REFUSED'),
        ('promote-publication', 'change_envelope', ['publication_approved', True], 'REFUSED'),
        ('promote-gold', 'change_envelope', ['training_gold_approved', True], 'REFUSED'),
        ('assert-independent-human', 'change_envelope', ['review_independence', 'independent human'], 'REFUSED'),
        ('changed-body-rehashed-envelope', 'rehash_candidate', None, 'REFUSED'),
        ('duplicate-json-key', 'duplicate_json', None, 'REFUSED'),
        ('unsafe-relative-path', 'change_path', '../../outside', 'REFUSED'),
        ('absolute-source-path', 'change_path', '/private/tmp/outside', 'REFUSED'),
        ('symlink-source', 'symlink_role', 'source', 'REFUSED'),
    ]
    for name, mutation, value, expected in variants:
        cases.append({'id': task+'-'+name, 'task': task, 'mutation': mutation, 'value': value, 'expected': expected})
save(P/'binding-study-protocol-v1.json', {
    'frozen_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'hypothesis': 'A caller-owned pinned envelope rejects stale/tampered acceptance dependencies and unauthorized promotion while preserving original exact bundles.',
    'anchor_path': 'trusted-binding-anchor-v1.json', 'anchor_sha256': sha((P/'trusted-binding-anchor-v1.json').read_bytes()),
    'cases': cases, 'positive_controls': 3, 'negative_controls': len(cases)-3,
    'unit': 'owned integrity mutation, not factual proposition or document-generation trial',
    'threat_boundary': 'Anchor is caller-owned frozen input. Attacker cannot replace anchor or validator. Full anchor compromise defeats this profile. Symlink/path checks are static preflight, not race-proof concurrent file-open design.',
    'semantic_boundary': 'Hashes prove byte bindings only. Valid envelopes retain historical source-only review; no new semantic acceptance, publication, Gold, independent human certification or production integration.',
    'new_model_calls': 0, 'optimizer_updates': 0, 'gold': 0,
})
print(json.dumps({'frozen_cases': len(cases), 'positive': 3, 'negative': len(cases)-3}))
