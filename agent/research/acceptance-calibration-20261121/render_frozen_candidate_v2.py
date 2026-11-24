"""Research projection only: preserve model prose, never certify source truth."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--task', choices=['fastapi', 'cobra', 'zod'], required=True)
parser.add_argument('--method', choices=['B', 'D', 'F'], required=True)
args = parser.parse_args()
task = next(t for t in json.loads((HERE / 'bounded-task-freeze-v2.json').read_text())['tasks']
            if t['task'] == args.task)
protocol = json.loads((HERE / 'generation-comparison-protocol-v1.json').read_text())
source_method = 'D' if args.method == 'F' else args.method
items = [i for i in protocol['calls'] if i['task'] == args.task and i['method'] == source_method]
records = {'en': [], 'pt-BR': []}
inputs = []
refusals = []

for item in items:
    folder = (ROOT / item['request']).parent
    outcome_path = folder / 'outcome.json'
    if not outcome_path.is_file():
        refusals.append('Missing terminal transport outcome: ' + str(folder.relative_to(ROOT)))
        continue
    outcome = json.loads(outcome_path.read_text())
    content_path = folder / 'model-content.txt'
    inputs.append({'path': str(outcome_path.relative_to(ROOT)),
                   'sha256': hashlib.sha256(outcome_path.read_bytes()).hexdigest()})
    if outcome.get('exit_code') != 0 or not content_path.is_file():
        refusals.append('Transport failed; no prose reconstructed')
        continue
    inputs.append({'path': str(content_path.relative_to(ROOT)),
                   'sha256': hashlib.sha256(content_path.read_bytes()).hexdigest()})
    try:
        data = json.loads(content_path.read_text())
        if source_method == 'D':
            for claim in data['claims']:
                for lang in records:
                    records[lang].append({'id': claim['id'], 'text': claim[lang],
                                          'source': claim['source']})
            uncertainty = data['uncertainty']
            for lang in records:
                records[lang].append({'id': uncertainty['id'], 'text': uncertainty[lang],
                                      'source': None})
        else:
            for lang in records:
                if not isinstance(data[lang], list):
                    raise ValueError('Section must be a list')
                for claim in data[lang]:
                    records[lang].append({'id': claim['id'], 'text': claim['text'],
                                          'source': claim.get('source')})
    except (KeyError, ValueError, TypeError) as error:
        refusals.append('Invalid original output; no repair: ' + type(error).__name__)

expected = set(task['required_claim_ids']) | {task['uncertainty_question']['id']}
for lang, claims in records.items():
    if any(not isinstance(c['id'], str) or not isinstance(c['text'], str) or not c['text'].strip()
           for c in claims):
        refusals.append('Missing/invalid original language text: ' + lang)
    actual = {c['id'] for c in claims if isinstance(c['id'], str)}
    if actual != expected:
        refusals.append('Missing or extra claim IDs in ' + lang + ': ' +
                        json.dumps({'missing': sorted(expected - actual), 'extra': sorted(actual - expected)}))

if args.method == 'F':
    review_path = HERE / 'generation-v1' / args.task / 'D' / 'semantic-review-v1.json'
    if not review_path.is_file():
        refusals.append('No separate D semantic review; gated assembly refused')
    else:
        review = json.loads(review_path.read_text())
        inputs.append({'path': str(review_path.relative_to(ROOT)),
                       'sha256': hashlib.sha256(review_path.read_bytes()).hexdigest()})
        if review.get('content_sha256') != hashlib.sha256((HERE / 'generation-v1' / args.task / 'D' / 'model-content.txt').read_bytes()).hexdigest() or review.get('source_revision') != task['revision']:
            refusals.append('Semantic review is not bound to exact D prose and frozen source revision')
        if review.get('all_generated_claims_reviewed') is not True or review.get('all_required_claims_covered') is not True:
            refusals.append('Separate semantic review incomplete; no gated assembly')
        if review.get('critical_unsupported_claims', 1) != 0 or review.get('bilingual_equivalence') is not True:
            refusals.append('Separate semantic/bilingual gate failed; no gated assembly')

candidate = {
    'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'task': args.task, 'method': args.method, 'source_method': source_method,
    'inputs': inputs, 'model_records_verbatim': records, 'refusals': refusals,
    'structural_projection_complete': not refusals,
    'source_truth_certified_by_renderer': False,
    'complete_document_accepted': None,
    'owner_approved': False, 'training_gold': False, 'optimizer_updates': 0,
    'authorship': {'model': 'All behavior and uncertainty prose, copied without correction',
                  'deterministic': 'Scope, section labels, revision, frozen bilingual first-question wording and execution/approval metadata'},
    'limits': 'Repeated IDs are retained for cross-occurrence semantic review, never counted as independent facts. '
              'Missing text is never filled from reference answers. Full document review remains necessary.',
}
if not refusals:
    questions_pt = {'fastapi': 'Qual é o valor padrão escrito de use_cache?', 'cobra': 'Qual é a assinatura do tipo de função PositionalArgs?', 'zod': 'Qual flag async a arrow síncrona retornada define?'}
    candidate['bounded_note'] = {}
    for lang in records:
        claims = records[lang]
        first = next(c for c in claims if c['id'] == task['required_claim_ids'][0])
        unknown = [c for c in claims if c['id'] == task['uncertainty_question']['id']]
        candidate['bounded_note'][lang] = {
            'scope': {'family': task['family'], 'revision': task['revision'], 'static_selected_source_only': True},
            'behavior': [c for c in claims if c['id'] != task['uncertainty_question']['id']],
            'error_boundaries': {'requires_semantic_review_of_original_behavior': True, 'general_exception_safety_certified': False},
            'faq': {'question': task['questions'][0]['question'] if lang == 'en' else questions_pt[args.task], 'answer_verbatim': first['text'],
                    'question_language': lang, 'question_authorship': 'frozen manual wrapper metadata; not neural translation'},
            'limitations': {'model_uncertainty_verbatim': unknown,
                            'external_tests_executed': False, 'examples_or_commands_verified': False,
                            'publication_or_training_approved': False},
        }
    # Both fixed questions are pre-reviewed wrapper metadata, not model outputs.

destination = HERE / ('rendered-' + args.task + '-' + args.method + '-v2.json')
with destination.open('x') as stream:
    json.dump(candidate, stream, indent=2, ensure_ascii=False)
    stream.write('\n')
print(json.dumps({'path': str(destination.relative_to(ROOT)),
                  'structural_projection_complete': not refusals, 'refusals': refusals,
                  'semantic_acceptance': None}), flush=True)
