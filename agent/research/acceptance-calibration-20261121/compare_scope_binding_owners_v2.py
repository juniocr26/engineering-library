"""Owned development comparison; no production patch or general semantic proof."""
import ast
import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
original_protocol_path = HERE / 'independent-scope-acquisition-protocol-v1.json'
challenge_path = HERE / 'scope-binding-owner-challenge-protocol-v2.json'
original = json.loads(original_protocol_path.read_text())
challenge = json.loads(challenge_path.read_text())
if hashlib.sha256(original_protocol_path.read_bytes()).hexdigest() != challenge['original_cases_sha256']:
    raise RuntimeError('Original protocol changed')
previous_result = json.loads((HERE / 'independent-scope-acquisition-results-v1.json').read_text())
previous = {record['id']: record for record in previous_result['records']}
prototype_path = HERE / 'run_scope_acquisition_v1.py'
prototype_tree = ast.parse(prototype_path.read_text())
# Compile definitions from our own previously preserved prototype only. Its
# entrypoint loop is deliberately excluded, so old observations are not rerun.
selected = [node for node in prototype_tree.body
            if isinstance(node, ast.FunctionDef) and node.name in ['digest', 'metadata_inventory', 'acquire']]
if len(selected) != 3:
    raise RuntimeError('Unexpected original prototype definition inventory')
namespace = {'ast': ast, 'os': os, 'Path': Path, 'hashlib': hashlib,
             'ROOT': ROOT, 'HERE': HERE, 'bounds': original['gate_frozen']}
exec(compile(ast.Module(body=selected, type_ignores=[]), str(prototype_path), 'exec'), namespace)
acquire_v1 = namespace['acquire']
sys.path.insert(0, str(ROOT / 'agent/tools'))
planner = runpy.run_path(str(ROOT / 'agent/tools/documentation_lifecycle.py'))


def own_scope_declarations(function):
    globals_found = set()
    nonlocals_found = set()
    stack = list(function.body)
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            continue
        if isinstance(node, ast.Global):
            globals_found.update(node.names)
        if isinstance(node, ast.Nonlocal):
            nonlocals_found.update(node.names)
        stack.extend(ast.iter_child_nodes(node))
    return globals_found, nonlocals_found


def binding_owner(node, parents, name):
    owner = parents.get(node)
    while owner is not None:
        if isinstance(owner, ast.Module):
            return 'MODULE'
        if isinstance(owner, ast.ClassDef):
            return 'CLASS:' + owner.name
        if isinstance(owner, (ast.FunctionDef, ast.AsyncFunctionDef)):
            global_names, nonlocal_names = own_scope_declarations(owner)
            if name in global_names:
                return 'GLOBAL_DECLARED_IN_FUNCTION:' + owner.name
            if name in nonlocal_names:
                return 'NONLOCAL_UNRESOLVED:' + owner.name
            return 'FUNCTION_LOCAL:' + owner.name
        owner = parents.get(owner)
    return 'UNKNOWN'


def acquire_v2(case, packet):
    evidence = copy.deepcopy(acquire_v1(case, packet))
    reasons = set(evidence['refusal_reasons'])
    owners = []
    root = ROOT / case['source_root']
    target = packet['metadata']['selector']
    for entry in evidence['independently_enumerated_files']:
        if 'sha256' not in entry:
            continue
        raw = (root / entry['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != entry['sha256']:
            reasons.add('SOURCE_BYTE_DRIFT:' + entry['path'])
            continue
        try:
            tree = ast.parse(raw.decode('utf-8'))
        except (SyntaxError, UnicodeError, ValueError, RecursionError):
            continue
        parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
        for node in ast.walk(tree):
            declared = isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == target
            assigned = isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store) and node.id == target
            if declared or assigned:
                owner = binding_owner(node, parents, target)
                relevant = owner == 'MODULE' or owner.startswith(('GLOBAL_DECLARED_', 'NONLOCAL_')) or owner == 'UNKNOWN'
                owners.append({'path': entry['path'], 'line': node.lineno,
                               'node_kind': type(node).__name__, 'binding_owner': owner,
                               'potential_old_module_contract_binding': relevant})
                marker = entry['path'] + ':' + str(node.lineno)
                if not relevant:
                    reasons.discard('POTENTIAL_CONTINUING_DECLARATION:' + marker)
                    reasons.discard('POTENTIAL_CONTINUING_BINDING:' + marker)
                elif isinstance(node, ast.ClassDef):
                    reasons.add('MODULE_CLASS_BINDING_CONTINUITY_UNRESOLVED:' + marker)
            if isinstance(node, ast.Call):
                reasons.add('UNRESOLVED_CALL_SCOPE:' + entry['path'] + ':' + str(node.lineno))
            possible_string_binding = (
                isinstance(node, ast.ExceptHandler) and node.name == target
                or isinstance(node, (ast.MatchAs, ast.MatchStar)) and node.name == target
                or isinstance(node, ast.MatchMapping) and node.rest == target
            )
            if possible_string_binding:
                reasons.add('UNADMITTED_BINDING_FORM:' + entry['path'] + ':' + str(node.lineno))
    evidence['binding_owner_observations'] = owners
    evidence['refusal_reasons'] = sorted(reasons)
    evidence['closed_snapshot_remove_admissible'] = not reasons
    evidence['prototype'] = 'V2_OWNER_QUALIFIED_FINITE_PROFILE'
    evidence['not_generic_python_binding_or_feature_semantics'] = True
    return evidence


records = []
for case in original['cases'] + challenge['new_cases']:
    packet_path = ROOT / case['packet']
    if hashlib.sha256(packet_path.read_bytes()).hexdigest() != case['packet_sha256']:
        raise RuntimeError('Frozen packet changed')
    root = ROOT / case['source_root']
    for source in case['files']:
        path = root / source['path']
        if source['kind'] == 'symlink':
            if not path.is_symlink() or os.readlink(path) != source['target']:
                raise RuntimeError('Frozen symlink changed')
        elif hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
            raise RuntimeError('Frozen source changed')
    packet = json.loads(packet_path.read_text())
    if case['id'] in previous:
        old_record = previous[case['id']]
        baseline = copy.deepcopy(old_record['actual_selected_planner'])
        v1 = copy.deepcopy(old_record['independent_acquisition'])
        origin = 'Reused exact terminal V1/planner observations from same immutable original case; no rerun'
    else:
        baseline = planner['decision'](packet)
        v1 = acquire_v1(case, packet)
        origin = 'New frozen ownership challenge; first planner/V1 observation'
    v2 = acquire_v2(case, packet)
    def filtered(evidence):
        return 'INCONCLUSIVE' if baseline['action'] == 'REMOVE' and not evidence['closed_snapshot_remove_admissible'] else baseline['action']
    record = {'id': case['id'], 'cohort': 'original-exposed-11' if case['id'] in previous else 'new-owner-challenge-7',
              'reference': case['reference_action'], 'reference_reason': case['reference_reason'],
              'baseline_action': baseline['action'], 'v1_action': filtered(v1), 'v2_action': filtered(v2),
              'baseline_observation': baseline, 'v1_evidence': v1, 'v2_evidence': v2,
              'observation_origin': origin, 'document_changes_applied': False}
    with (packet_path.parent / 'binding-owner-observation-v2.json').open('x') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')
    records.append(record)

labels = ['ADD', 'MODIFY', 'REMOVE', 'NO-OP', 'INCONCLUSIVE']


def ratio(numerator, denominator):
    return {'numerator': numerator, 'denominator': denominator,
            'ratio': numerator / denominator if denominator else None}


cohorts = []
for cohort in ['original-exposed-11', 'new-owner-challenge-7']:
    cases = [record for record in records if record['cohort'] == cohort]
    conditions = {}
    for field in ['baseline_action', 'v1_action', 'v2_action']:
        matrix = {reference: {observed: 0 for observed in labels} for reference in labels}
        for case in cases:
            matrix[case['reference']][case[field]] += 1
        support = {label: sum(matrix[label].values()) for label in labels}
        conditions[field] = {
            'matrix_reference_rows_observed_columns': matrix,
            'reference_support': support,
            'exact_agreement': ratio(sum(matrix[label][label] for label in labels), len(cases)),
            'false_remove': ratio(sum(matrix[label]['REMOVE'] for label in labels if label != 'REMOVE'), len(cases) - support['REMOVE']),
            'missed_modify': ratio(support['MODIFY'] - matrix['MODIFY']['MODIFY'], support['MODIFY']),
            'justified_abstention': ratio(matrix['INCONCLUSIVE']['INCONCLUSIVE'], support['INCONCLUSIVE']),
            'unnecessary_abstention_on_remove': ratio(matrix['REMOVE']['INCONCLUSIVE'], support['REMOVE']),
        }
    cohorts.append({'cohort': cohort, 'cases': len(cases), 'conditions': conditions})

result = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'challenge_protocol_sha256': hashlib.sha256(challenge_path.read_bytes()).hexdigest(),
          'prototype_v1_sha256': hashlib.sha256(prototype_path.read_bytes()).hexdigest(),
          'prototype_v2_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'planner_sha256': hashlib.sha256((ROOT / 'agent/tools/documentation_lifecycle.py').read_bytes()).hexdigest(),
          'planner_version': planner['VERSION'], 'cohorts': cohorts, 'records': records,
          'model_calls': 0, 'training_steps': 0, 'production_changes': False,
          'permanent_tests_created': False, 'owner_approved': False, 'training_gold': False,
          'interpretation': 'Development-only finite scope filtering. Namespace qualification reduces known false abstention; '
                            'class binding exposes why V1 zero false REMOVE on its original eight negatives was not generic safety. '
                            'Neither version recovers correct MODIFY automatically or proves runtime feature retirement.',
          'limits': ['No ADD/NO-OP references in these cohorts; zero denominators remain null.',
                     'All source acquisition budgets and incomplete-context refusals retained.',
                     'All calls and unadmitted pattern/exception bindings conservatively refuse V2 retirement.',
                     'Qualified lexical binding observations are not arbitrary Python resolution, project comprehension, independent holdout or production integration.']}
with (HERE / 'scope-binding-owner-comparison-results-v2.json').open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
for cohort in cohorts:
    print(json.dumps({'cohort': cohort['cohort'],
                      'rates': {key: {metric: value for metric, value in record.items() if metric not in ['matrix_reference_rows_observed_columns', 'reference_support']}
                                for key, record in cohort['conditions'].items()}}, indent=2), flush=True)
