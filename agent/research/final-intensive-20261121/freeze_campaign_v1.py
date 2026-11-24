"""Freeze new research questions before observations; never modify prior evidence."""
from pathlib import Path
import datetime
import hashlib
import json

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
PRIOR = ROOT / 'agent/research/acceptance-calibration-20261121'


def write(name, value):
    with (P / name).open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


gates = [
    ('G1', 'SOURCE_IDENTITY', 'Repository, immutable revision, source paths and exact reviewed bytes match; working-tree drift is recorded separately.'),
    ('G2', 'FACTUAL_CORRECTNESS', 'Every factual proposition reviewed; no critical contradiction, invented API or unsupported runtime guarantee.'),
    ('G3', 'ARCHITECTURAL_CONTEXT', 'All frozen relevant callers, callees, configuration, dependencies, state, errors and lifecycle covered within declared boundary.'),
    ('G4', 'REQUIRED_COMPLETENESS', 'Every predeclared mandatory requirement covered; no retrospective narrowing.'),
    ('G5', 'EXAMPLES_AND_TESTS', 'Execution claims match actual receipts; static checks are labelled static; required examples validated at authorized level.'),
    ('G6', 'BILINGUAL_SEMANTICS', 'Both required languages convey equivalent propositions, conditions, negations and identifiers.'),
    ('G7', 'DOCUMENTATION_MAINTENANCE', 'ADD/MODIFY/REMOVE/NO-OP/INCONCLUSIVE supported by separately acquired scope evidence; absence in one file never authorizes REMOVE.'),
    ('G8', 'INDEPENDENT_VERIFICATION', 'Separate source acquisition/verification procedure challenges output and negative controls; identify same-agent limits, never imply independent human review.'),
    ('G9', 'RECOVERABILITY_AND_PROVENANCE', 'Candidate, frozen criteria, reviewed sources, references, model identity, evaluations and limitations recoverable with verified bindings.'),
]
contract = {
    'version': 'documentation-done/3.0-research',
    'frozen_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'extends': 'agent/research/acceptance-calibration-20261121/acceptance-protocol-v2.json',
    'prior_sha256': hashlib.sha256((PRIOR/'acceptance-protocol-v2.json').read_bytes()).hexdigest(),
    'scope': 'New bounded research evaluations only; does not overwrite historical verdicts.',
    'mandatory_gates': [{'id': i, 'name': n, 'requirement': r} for i, n, r in gates],
    'gate_states': ['PASS', 'FAIL', 'INCONCLUSIVE', 'N/A'],
    'pass_rule': 'All nine gates PASS, except predeclared justified N/A. Unknown critical evidence is INCONCLUSIVE. Any mandatory FAIL rejects. No critical unreviewed claim.',
    'freeze_fields': ['project_identity', 'source_revision', 'source_inventory', 'document_type', 'audience', 'interfaces_and_responsibilities', 'architecture_and_dependencies', 'behavior_and_errors', 'tests_and_examples', 'languages', 'lifecycle_action_scope', 'uncertainty_and_exclusions', 'independent_verification_criteria', 'gate_applicability'],
    'approval_levels': {
        'TECHNICALLY_ACCEPTED': 'Exact reviewed candidate passes all applicable gates within frozen scope; not publication/training authorization.',
        'PUBLICATION_APPROVED': 'Technical acceptance plus separately authorized editorial, licensing, confidentiality and publication review.',
        'TRAINING_GOLD_APPROVED': 'Explicit owner training-use approval of exact example, cleared rights, lineage and evaluation exclusion; never inherited from technical acceptance.',
    },
    'model_readiness': {
        'status': 'INSUFFICIENT_EVIDENCE',
        'provisional_thresholds': {'complete_acceptance': 0.8, 'critical_unsupported_claims_in_accepted': 0, 'unsafe_automatic_remove': 0, 'identifier_preservation': 0.95, 'required_bilingual_coverage': 1.0, 'uncertainty_promotion': 0, 'matched_baseline_regression': 0},
        'sampling': 'Freeze diverse family-disjoint evaluation-only task groups, related dependency/revision/translation exclusions, reviewer and sample-size justification before inference. No sufficient independent sample currently established.',
        'not_certification': True,
    },
    'metric_fields': ['numerator', 'denominator', 'population', 'method', 'baseline', 'confidence_limitations'],
    'zero_denominator': None,
    'independence': 'Separate verification implementation is procedural independence only. Same-agent semantic judgments are not independent-human approval.',
    'training_default_deny': True,
}
write('documentation-done-v3.json', contract)
queue = {
    'frozen_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'target_hours': 12,
    'start_reference': 'baseline.json',
    'no_owner_questions': True,
    'hypotheses': [
        {'id': 'H1', 'question': 'Can current missing canonical reports be recovered exactly from the latest preserved checkpoint?', 'state': 'OBSERVED_BEFORE_THIS_QUEUE', 'result_reference': 'canonical-recovery-v1.json'},
        {'id': 'H2', 'question': 'Can a pinned acceptance envelope reject stale content, source, criterion, requirement and review bindings without treating hashes as semantic truth?', 'unit': 'owned envelope mutation', 'freeze_required': True},
        {'id': 'H3', 'question': 'Does every cited exact evidence string occur at its declared line range in all 28 K reference propositions, and do corresponding current Git source objects match?', 'unit': 'reference proposition; duplicate language occurrences not independent', 'freeze_required': True},
        {'id': 'H4', 'question': 'Can a small exact-source bilingual correction candidate resolve the already identified Zod reviewer-provenance ambiguity without changing original files?', 'unit': 'separate candidate pair; no historical score replacement', 'freeze_required': True},
        {'id': 'H5', 'question': 'Do selected real current revisions change documentation-relevant contracts, and is source-scope sufficient for lifecycle action?', 'unit': 'pinned revision pair and exact existing document', 'freeze_required': True},
        {'id': 'H6', 'question': 'Do accepted research artifacts survive path relocation, missing dependencies and replay of their actual consumers?', 'unit': 'restored owned artifact graph', 'freeze_required': True},
    ],
    'fallbacks': {'docker_denied': 'No escalation/questions; static source research and owned standard-library prototypes.', 'local_inference_unavailable': 'Preserve exact reason; no external inference or unchanged repeat.', 'fine_tuning': 'Prepare only; all nine gates remain NO_GO until separately approved conditions verified.', 'blocked_production_fix': 'Preserve concrete proposal; no source/test integration.'},
    'checkpoint_policy': 'Approximately every 30 minutes and critical results; include bytes, modes, source identities and actual restore evidence. No artificial waits.',
    'scope': 'Only new isolated research directory and exactly four canonical root reports; prior artifacts immutable.',
}
write('research-queue-v1.json', queue)
print(json.dumps({'contract': 'documentation-done-v3.json', 'hypotheses': len(queue['hypotheses'])}))
