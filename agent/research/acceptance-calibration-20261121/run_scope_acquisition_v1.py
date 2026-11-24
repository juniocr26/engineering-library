"""Finite owned research snapshots: independently filter retirement proposals."""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROTOCOL = HERE / 'independent-scope-acquisition-protocol-v1.json'
protocol = json.loads(PROTOCOL.read_text())
bounds = protocol['gate_frozen']
sys.path.insert(0, str(ROOT / 'agent/tools'))
planner = runpy.run_path(str(ROOT / 'agent/tools/documentation_lifecycle.py'))


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def metadata_inventory(root):
    result = []
    stack = [(root, 0)]
    while stack:
        directory, depth = stack.pop()
        if depth > 4:
            raise ValueError('Directory depth outside finite profile')
        for entry in sorted(os.scandir(directory), key=lambda value: value.name):
            path = Path(entry.path)
            relative = path.relative_to(root).as_posix()
            info = entry.stat(follow_symlinks=False)
            if entry.is_symlink():
                result.append({'path': relative, 'kind': 'symlink', 'target': os.readlink(path)})
            elif entry.is_dir(follow_symlinks=False):
                stack.append((path, depth + 1))
            elif entry.is_file(follow_symlinks=False):
                result.append({'path': relative, 'kind': 'file', 'bytes': info.st_size,
                               'inode': info.st_ino, 'mtime_ns': info.st_mtime_ns})
            else:
                result.append({'path': relative, 'kind': 'unsupported-filesystem-entry'})
    return sorted(result, key=lambda value: value['path'])


def acquire(case, packet):
    root = ROOT / case['source_root']
    if root.is_symlink():
        raise ValueError('Symlink source root refused')
    root.resolve().relative_to(HERE.resolve())
    initial_root = root.stat()
    before = metadata_inventory(root)
    reasons = []
    files = []
    retirements = []
    total_bytes = 0
    if len(before) > bounds['max_files']:
        reasons.append('FILE_COUNT_BOUND')
    for entry in before:
        relative = entry['path']
        if entry['kind'] != 'file':
            reasons.append('UNACQUIRED_ENTRY:' + relative)
            files.append(entry)
            continue
        total_bytes += entry['bytes']
        if entry['bytes'] > bounds['max_file_bytes']:
            reasons.append('FILE_BYTE_BOUND:' + relative)
            files.append(entry)
            continue
        if total_bytes > bounds['max_total_bytes']:
            reasons.append('TOTAL_BYTE_BOUND')
            files.append(entry)
            continue
        if Path(relative).suffix != '.py':
            reasons.append('UNSUPPORTED_SOURCE_LANGUAGE:' + relative)
            files.append(entry)
            continue
        raw = (root / relative).read_bytes()
        files.append({**entry, 'sha256': digest(raw)})
        try:
            tree = ast.parse(raw.decode('utf-8'), filename=relative)
        except (SyntaxError, UnicodeError, ValueError, RecursionError) as error:
            reasons.append('SOURCE_UNPARSED:' + relative + ':' + type(error).__name__)
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == packet['metadata']['selector']:
                    reasons.append('POTENTIAL_CONTINUING_DECLARATION:' + relative + ':' + str(node.lineno))
                if node.name == '__getattr__':
                    reasons.append('DYNAMIC_EXPORT:' + relative)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store) and node.id == packet['metadata']['selector']:
                reasons.append('POTENTIAL_CONTINUING_BINDING:' + relative + ':' + str(node.lineno))
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                reasons.append('IMPORT_SCOPE_UNRESOLVED:' + relative)
            if isinstance(node, ast.Call):
                name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else None
                if name in bounds['dynamic_names']:
                    reasons.append('DYNAMIC_OPERATION:' + relative + ':' + str(node.lineno))
            if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'RETIRED_CONTRACTS' for target in node.targets):
                try:
                    value = ast.literal_eval(node.value)
                    if not isinstance(value, dict):
                        raise ValueError('Nonmapping retirement registry')
                    if packet['logical_contract_id'] in value:
                        retirements.append({'path': relative, 'line': node.lineno,
                                            'reason': value[packet['logical_contract_id']]})
                except (ValueError, TypeError, SyntaxError, RecursionError):
                    reasons.append('NONLITERAL_RETIREMENT_REGISTRY:' + relative)
    positive = packet['positive_retirement_evidence']['reason']
    if not any(item['path'] == 'api.py' and item['reason'] == positive for item in retirements):
        reasons.append('NO_INDEPENDENT_MATCHED_POSITIVE_RETIREMENT')
    if any(item['reason'] != positive for item in retirements):
        reasons.append('CONFLICTING_RETIREMENT_RECORDS')
    after = metadata_inventory(root)
    final_root = root.stat()
    if before != after or (initial_root.st_dev, initial_root.st_ino) != (final_root.st_dev, final_root.st_ino):
        reasons.append('SOURCE_INVENTORY_OR_ROOT_DRIFT')
    for entry in files:
        if 'sha256' in entry and digest((root / entry['path']).read_bytes()) != entry['sha256']:
            reasons.append('SOURCE_BYTE_DRIFT:' + entry['path'])
    return {'root': case['source_root'], 'independently_enumerated_files': files,
            'retirement_records': retirements, 'refusal_reasons': sorted(set(reasons)),
            'closed_snapshot_remove_admissible': not reasons,
            'source_executed': False, 'not_generic_semantic_or_runtime_proof': True,
            'generator_scope_flags_used_as_proof': False}


labels = ['ADD', 'MODIFY', 'REMOVE', 'NO-OP', 'INCONCLUSIVE']
matrices = {condition: {reference: {observed: 0 for observed in labels} for reference in labels}
            for condition in ['selected-planner', 'independent-scope-filter']}
records = []
for case in protocol['cases']:
    packet_path = ROOT / case['packet']
    if digest(packet_path.read_bytes()) != case['packet_sha256']:
        raise RuntimeError('Frozen packet changed')
    packet = json.loads(packet_path.read_text())
    root = ROOT / case['source_root']
    for source in case['files']:
        path = root / source['path']
        if source['kind'] == 'symlink':
            if not path.is_symlink() or os.readlink(path) != source['target']:
                raise RuntimeError('Frozen symlink changed')
        elif digest(path.read_bytes()) != source['sha256']:
            raise RuntimeError('Frozen source changed')
    original = planner['decision'](packet)
    baseline_action = original['action']
    evidence = acquire(case, packet)
    filtered = baseline_action
    if baseline_action == 'REMOVE' and not evidence['closed_snapshot_remove_admissible']:
        filtered = 'INCONCLUSIVE'
    reference = case['reference_action']
    matrices['selected-planner'][reference][baseline_action] += 1
    matrices['independent-scope-filter'][reference][filtered] += 1
    observation = {'id': case['id'], 'reference': reference, 'reference_reason': case['reference_reason'],
                   'actual_selected_planner': original, 'filtered_action': filtered,
                   'independent_acquisition': evidence, 'document_changes_applied': False}
    output = packet_path.parent / 'observation-v1.json'
    with output.open('x') as stream:
        json.dump(observation, stream, indent=2)
        stream.write('\n')
    records.append(observation)


def rate(numerator, denominator):
    return {'numerator': numerator, 'denominator': denominator,
            'ratio': numerator / denominator if denominator else None}


metrics = {}
for condition, matrix in matrices.items():
    support = {label: sum(matrix[label].values()) for label in labels}
    metrics[condition] = {
        'exact_label_agreement': rate(sum(matrix[label][label] for label in labels), len(records)),
        'false_remove': rate(sum(matrix[label]['REMOVE'] for label in labels if label != 'REMOVE'),
                             len(records) - support['REMOVE']),
        'missed_modify': rate(support['MODIFY'] - matrix['MODIFY']['MODIFY'], support['MODIFY']),
        'justified_abstention': rate(matrix['INCONCLUSIVE']['INCONCLUSIVE'], support['INCONCLUSIVE']),
        'unnecessary_abstention_on_remove': rate(matrix['REMOVE']['INCONCLUSIVE'], support['REMOVE']),
        'reference_support': support,
    }

result = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'protocol_sha256': digest(PROTOCOL.read_bytes()), 'planner_version': planner['VERSION'],
          'planner_sha256': digest((ROOT / 'agent/tools/documentation_lifecycle.py').read_bytes()),
          'prototype_sha256': digest(Path(__file__).read_bytes()),
          'records': records, 'matrices_reference_rows_observed_columns': matrices, 'metrics': metrics,
          'new_model_calls': 0, 'production_source_modified': False, 'permanent_tests_created': False,
          'owner_approved': False, 'training_gold': False, 'optimizer_updates': 0,
          'limits': protocol['limits'],
          'interpretation': 'Finite owned development observations only. Filtering a false REMOVE into '
                            'INCONCLUSIVE does not recover correct MODIFY or prove whole-project scope.'}
destination = HERE / 'independent-scope-acquisition-results-v1.json'
with destination.open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(json.dumps(metrics, indent=2), flush=True)
