"""Evidence-bound documentation review, independent of reference similarity.

Human judgments remain explicit assertions. Hashes establish artifact identity,
not semantic truth. Missing reviews never become perfect scores.
"""
import argparse
import hashlib
import json
from pathlib import Path


POLICY = {
    'schema': 2,
    'status': 'initial operational policy; not scientifically validated',
    'weights': {'factual': .35, 'coverage': .20, 'organization': .15,
                'resources': .10, 'bilingual': .10, 'incremental': .10},
    'criteria': {
        'factual': ['claim_accuracy', 'source_traceability', 'limitations'],
        'coverage': ['purpose_architecture_modules', 'contracts_configuration_flows',
                     'build_testing_operations_errors'],
        'organization': ['heading_hierarchy', 'indexes_navigation', 'portable_links'],
        'resources': ['usefulness_or_justified_absence', 'source_supported_content',
                      'syntax_and_portability'],
        'bilingual': ['technical_equivalence', 'terminology_readability', 'navigation_parity'],
        'incremental': ['relevant_irrelevant_and_removal', 'no_op_and_preservation',
                        'interruption_restoration_and_bilingual_update'],
    },
    'ratings': {'complete': 1.0, 'partial': .5, 'missing': 0.0, 'pending': None},
    'claim_states': ['complete', 'partial', 'missing', 'incorrect', 'unsupported',
                     'contradictory', 'pending'],
    'partial_claim_credit': .5,
    'coverage': 'Rate source-oriented breadth/depth criteria independently of reference overlap. '
                'Required-claim partial coverage remains a separate diagnostic and does not cap '
                'the absolute quality dimension. Criteria judgments still require source review.',
    'grouped_control': 'Group required claims by frozen group (default: claim ID). '
                       'A strict group receives credit only when every claim is complete; '
                       'report alongside atomic partial coverage, never as a historical rescore.',
    'scope': 'Frozen required claims and criteria; never extrapolate a component score to a project.',
    'publication': 'Critical factual errors block readiness. Similarity is not an acceptance gate. '
                   'Complete review and all criteria complete are required for publication-ready; '
                   'owner approval is recorded separately and never inferred.',
    'provisional': 'Only incremental may be not-evaluated for initial documentation; '
                   'report earned points out of 90 and the normalized provisional percentage.',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def policy_hash():
    return sha(json.dumps(POLICY, sort_keys=True).encode())


def unique_ids(rows, label):
    if not isinstance(rows, list):
        raise ValueError('Expected list: '+label)
    ids = [r.get('id') for r in rows]
    if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
        raise ValueError('Invalid or duplicate IDs: '+label)
    return set(ids)


def score(packet):
    if packet.get('policy_sha256') != policy_hash():
        raise ValueError('Quality policy differs from frozen policy')
    if packet.get('scope') not in {'component', 'section', 'chapter', 'project'}:
        raise ValueError('Explicit review scope required')
    artifacts = packet.get('artifacts', [])
    unique_ids(artifacts, 'artifacts')
    if not artifacts:
        raise ValueError('Frozen artifacts required')
    for item in artifacts:
        if sha(Path(item['path']).read_bytes()) != item['sha256']:
            raise ValueError('Artifact changed after freeze: '+item['id'])
    evidence = packet.get('evidence', [])
    evidence_ids = unique_ids(evidence, 'evidence')
    for item in evidence:
        data = Path(item['path']).read_bytes()
        if sha(data) != item['source_sha256']:
            raise ValueError('Evidence changed after freeze: '+item['id'])
        start, end = item['line_start'], item['line_end']
        lines = data.splitlines(keepends=True)
        if type(start) is not int or type(end) is not int or not 1 <= start <= end <= len(lines):
            raise ValueError('Invalid evidence line span')
        if sha(b''.join(lines[start-1:end])) != item['quote_sha256']:
            raise ValueError('Evidence span hash mismatch')
    claims = packet.get('claims', [])
    unique_ids(claims, 'claims')
    if not claims or packet.get('inventory_complete') is not True:
        inventory_complete = False
    else:
        inventory_complete = True
    for claim in claims:
        if claim.get('state') not in POLICY['claim_states']:
            raise ValueError('Invalid claim state')
        if type(claim.get('required')) is not bool or type(claim.get('critical')) is not bool:
            raise ValueError('Explicit required/critical claim flags required')
        if not isinstance(claim.get('reason'), str) or not claim['reason'].strip():
            raise ValueError('Claim judgment needs a reason')
        refs = claim.get('evidence', [])
        if not isinstance(refs, list) or any(ref not in evidence_ids for ref in refs):
            raise ValueError('Unknown claim evidence')
        if claim['state'] in {'complete', 'partial', 'incorrect', 'contradictory'} and not refs:
            raise ValueError('Source judgments require frozen evidence')
    counts = {state: sum(c['state'] == state for c in claims) for state in POLICY['claim_states']}
    critical = [c['id'] for c in claims if c['critical'] and c['state'] in
                {'incorrect', 'unsupported', 'contradictory'}]
    required = [c for c in claims if c['required']]
    groups = {}
    for claim in required:
        group = claim.get('group', claim['id'])
        if not isinstance(group, str) or not group:
            raise ValueError('Invalid frozen claim group')
        groups.setdefault(group, []).append(claim)
    partial_coverage = None if not required or not inventory_complete or counts['pending'] else (
        100 * sum(1 if c['state'] == 'complete' else .5 if c['state'] == 'partial' else 0
                  for c in required) / len(required))
    strict_group_coverage = None if partial_coverage is None else 100 * sum(
        all(c['state'] == 'complete' for c in group) for group in groups.values()) / len(groups)
    reviews = packet.get('dimensions', {})
    if set(reviews) != set(POLICY['weights']):
        raise ValueError('Every dimension must be explicit')
    scores = {}
    for dimension, criteria in POLICY['criteria'].items():
        review = reviews[dimension]
        if review == 'not-evaluated' and dimension == 'incremental':
            scores[dimension] = None
            continue
        if not isinstance(review, dict) or set(review) != set(criteria):
            raise ValueError('Invalid criterion inventory: '+dimension)
        values = []
        for criterion in criteria:
            item = review[criterion]
            rating = item.get('rating')
            if rating not in POLICY['ratings']:
                raise ValueError('Invalid criterion rating')
            if not isinstance(item.get('reason'), str) or not item['reason'].strip():
                raise ValueError('Criterion judgment needs a reason')
            refs = item.get('evidence', [])
            if not isinstance(refs, list) or any(ref not in evidence_ids for ref in refs):
                raise ValueError('Unknown criterion evidence')
            if rating in {'complete', 'partial'} and not refs:
                raise ValueError('Positive criterion judgments require evidence')
            values.append(POLICY['ratings'][rating])
        scores[dimension] = None if None in values else 100 * sum(values) / len(values)
    # A factual rubric cannot override the explicit claim inventory.
    unreviewed = not inventory_complete or counts['pending'] > 0
    emitted = len(claims)-counts['missing']
    accuracy = None if unreviewed or not emitted else 100 * (counts['complete']+counts['partial']) / emitted
    if unreviewed:
        scores['factual'] = None
    elif accuracy is not None and scores['factual'] is not None:
        scores['factual'] = min(scores['factual'], accuracy)
    evaluated = {k: v for k, v in scores.items() if v is not None}
    missing = set(scores)-set(evaluated)
    provisional = missing == {'incremental'}
    complete = not missing and not unreviewed
    earned = sum(POLICY['weights'][k]*v for k, v in evaluated.items())
    available = 100 * sum(POLICY['weights'][k] for k in evaluated)
    quality = earned if complete else None
    provisional_quality = 100 * earned / available if provisional and not unreviewed else None
    if critical:
        category = 'rejected-critical-factual-errors'
    elif not complete:
        category = 'incomplete'
    elif any(counts[s] for s in ['incorrect', 'unsupported', 'contradictory']):
        category = 'useful-requires-review'
    elif all(v == 100 for v in scores.values()) and not counts['partial'] and not counts['missing']:
        category = 'publication-ready'
    else:
        category = 'useful-requires-review'
    return {'policy_sha256': policy_hash(), 'scope': packet['scope'],
            'source_revision': packet['source_revision'], 'scores': scores,
            'quality': quality, 'provisional_quality': provisional_quality,
            'earned_points': earned, 'evaluated_weight': available,
            'claim_counts': counts, 'claim_partial_coverage': partial_coverage,
            'strict_group_coverage_control': strict_group_coverage,
            'required_claims': len(required), 'required_groups': len(groups),
            'factual_claim_accuracy': accuracy,
            'critical_errors': critical, 'classification': category,
            'owner_acceptance': packet.get('owner_acceptance', 'not supplied'),
            'similarity': 'not measured by this quality evaluator'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packet', type=Path, nargs='?')
    parser.add_argument('--policy', action='store_true')
    args = parser.parse_args()
    if args.policy:
        print(json.dumps({'policy': POLICY, 'sha256': policy_hash()}, indent=2))
    elif args.packet:
        print(json.dumps(score(json.loads(args.packet.read_text())), indent=2))
    else:
        parser.error('Provide --policy or a review packet')
