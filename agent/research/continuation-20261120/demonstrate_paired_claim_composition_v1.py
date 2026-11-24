"""Compare hypothetical last-child selection with real bounded batch composition."""
import copy
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path

P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('composition_demo_batch', P / 'registered_claim_batch_v1.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
preimage = Path('/private/tmp/el-claim-batch-controls-20261120-v1/two-shared-document-modifications/exact-inputs.json')
raw = preimage.read_bytes()
initial = json.loads(raw)
requests = copy.deepcopy(initial['requests'])
requests[0]['replacements']['en'] = 'slugify has an allow_unicode parameter.\n'
batch = module.RegisteredClaimBatch(initial['registration'])
children = [batch.children[request['claim_id']].prepare(request['packet'], request['replacements'], request['action']) for request in requests]
assert all(row['status'] == 'PREPARED' for row in children)
last = children[-1]
for language in ['en', 'pt-br']:
    assert requests[0]['packet']['documentation'][language] in last['candidates'][language]['markdown']
    assert requests[0]['replacements'][language].strip() not in last['candidates'][language]['markdown']
forward = batch.prepare(requests)
reverse = batch.prepare(list(reversed(requests)))
assert forward['status'] == reverse['status'] == 'PREPARED'
for language in ['en', 'pt-br']:
    assert forward['candidates'][language]['candidate_sha256'] == reverse['candidates'][language]['candidate_sha256']
    for request in requests:
        assert request['replacements'][language].strip() in forward['candidates'][language]['markdown']
    actual = Path(initial['registration']['documentation_root']) / initial['registration']['documents'][language]['path']
    assert actual.read_text() == initial['original_documents'][language]
record = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'exact_control_preimage_sha256': hashlib.sha256(raw).hexdigest(), 'review_presentation_change': 'Use grammatical an allow_unicode rather than a allow_unicode in the illustrative replacement. No source claim or action changed.',
          'counterfactual_comparator': {'description': 'Select the last of two independently prepared full-document child outputs.', 'is_existing_production_behavior': False, 'both_children_individually_valid': True, 'first_change_lost_if_last_child_selected': True, 'last_child_output_hashes': {lang: row['candidate_sha256'] for lang, row in last['candidates'].items()}},
          'bounded_batch': forward, 'reverse_order_candidate_hashes': {lang: row['candidate_sha256'] for lang, row in reverse['candidates'].items()}, 'independent_nonoverlapping_operation_order_preserves_candidate_bytes': True,
          'original_files_unchanged_after_prepare': True, 'reviewable_demonstration_only': True, 'documentation_is_owned_synthetic_not_active_catalog': True, 'source_family': 'un33k/python-slugify', 'source_executed': False, 'model_calls': 0, 'new_independent_evaluation_cases': 0, 'production_integration': False, 'owner_approved': False, 'training_gold': False, 'publication_authorized': False}
with (P / 'paired-change-composition-demonstration-v1.json').open('x') as stream:
    stream.write(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'counterfactual_loses_first_change': True, 'batch_preserves_both': True, 'independent_order_candidate_hashes_identical': True, 'original_files_unchanged': True, 'existing_production_bug_claimed': False}))
