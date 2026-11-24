"""Restore and consume actual renderer inputs; retain every challenge output."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import time
import binding_envelope_v1 as binding

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
PRIOR = ROOT/'agent/research/acceptance-calibration-20261121'
relative_prior = PRIOR.relative_to(ROOT)
protocol_raw = (P/'renderer-recovery-protocol-v1.json').read_bytes()
protocol = json.loads(protocol_raw)
anchor = json.loads((P/'trusted-binding-anchor-v1.json').read_text())
for item in protocol['dependencies']:
    assert hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest() == item['sha256']
output = P/'renderer-recovery-v1'
output.mkdir()
capsule = output/'original-consumer-inputs.tar.gz'
with tarfile.open(capsule, 'x:gz') as tar:
    for item in protocol['dependencies']:
        tar.add(ROOT/item['path'], arcname=item['path'], recursive=False)
os.chmod(capsule, 0o600)
restore = Path(tempfile.mkdtemp(prefix='el-renderer-inputs-', dir='/private/tmp'))
with tarfile.open(capsule) as tar:
    tar.extractall(restore, filter='data')
for item in protocol['dependencies']:
    assert binding.digest((restore/item['path']).read_bytes()) == item['sha256']
freeze = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'protocol_sha256': binding.digest(protocol_raw),
          'producer_sha256': binding.digest(Path(__file__).read_bytes()), 'capsule_sha256': binding.digest(capsule.read_bytes()),
          'restored_original_dependencies_verified': len(protocol['dependencies']), 'restored_root': str(restore)}
with (P/'renderer-recovery-producer-freeze-v1.json').open('x') as stream:
    json.dump(freeze, stream, indent=2)
    stream.write('\n')
rows = []
for case in protocol['cases']:
    task, kind = case['task'], case['kind']
    case_root = Path(tempfile.mkdtemp(prefix='el-renderer-case-', dir='/private/tmp'))
    case_prior = case_root/relative_prior
    directory = output/case['id']
    directory.mkdir()
    omitted = set()
    relative_output = str(relative_prior/'verified-fact-render-v1'/task/'K/rendered-note-v1.json')
    # Preserve originals in the immutable capsule; replay creates a separate output.
    omitted.add(relative_output)
    if kind == 'missing-schema-module':
        omitted.add(str(relative_prior/'frozen_schema_subset_v2.py'))
    elif kind == 'missing-source':
        omitted.add(next(x['path'] for x in anchor[task]['dependencies'] if x['role']=='source'))
    elif kind == 'missing-review':
        omitted.add(str(relative_prior/'verified-fact-render-v1'/task/'K/semantic-review-v1.json'))
    for item in protocol['dependencies']:
        if item['path'] in omitted:
            continue
        target = case_root/item['path']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(restore/item['path'], target)
    overlay = {}
    mutation_path = None
    if kind == 'stale-content':
        mutation_path = relative_prior/'verified-fact-render-v1'/task/'K/model-content.txt'
        data = json.loads((case_root/mutation_path).read_text())
        first = next(iter(data['facts']))
        data['facts'][first]['en'] += ' Extra unsupported assertion.'
    elif kind == 'wrong-reference-revision':
        mutation_path = relative_prior/'atomic-reference-ledger-v2.json'
        data = json.loads((case_root/mutation_path).read_text())
        for ref in data['claims']:
            if ref['task'] == task:
                ref['source_revision'] = '0'*40
    elif kind == 'invented-metadata-test-claim':
        mutation_path = relative_prior/'verified-fact-render-protocol-v1.json'
        data = json.loads((case_root/mutation_path).read_text())
        data['metadata'][task]['scope']['en'] += ' All upstream tests passed in this campaign.'
    if mutation_path is not None:
        raw = json.dumps(data, indent=2, ensure_ascii=False).encode()+b'\n'
        (case_root/mutation_path).write_bytes(raw)
        with (directory/'mutated-input.json').open('xb') as stream:
            stream.write(raw)
        overlay[str(mutation_path)] = raw
    command = [os.sys.executable, '-B', str(case_prior/'render_verified_fact_note_v1.py'), '--task', task]
    started = time.monotonic()
    process = subprocess.run(command, capture_output=True, timeout=30, env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'})
    for name, raw in [('stdout.txt', process.stdout), ('stderr.txt', process.stderr)]:
        with (directory/name).open('xb') as stream:
            stream.write(raw)
    candidate = case_root/relative_output
    assembled = False
    payload_matches = None
    unsafe_marker = False
    if candidate.is_file():
        raw = candidate.read_bytes()
        with (directory/'rendered-output.json').open('xb') as stream:
            stream.write(raw)
        new = json.loads(raw)
        assembled = new.get('status') == 'ASSEMBLED_PENDING_COMPLETE_DIMENSION_REVIEW'
        if kind == 'baseline':
            original = json.loads((ROOT/relative_output).read_text())
            new.pop('at', None)
            original.pop('at', None)
            payload_matches = new == original
        if kind == 'wrong-reference-revision':
            unsafe_marker = '0'*40 in json.dumps(new.get('notes', {}))
        elif kind == 'invented-metadata-test-claim':
            unsafe_marker = 'All upstream tests passed in this campaign.' in json.dumps(new.get('notes', {}))
    # Check envelope against original trusted input space; no output candidate check
    # here, because a new timestamp is expected from the consumer. Inject only the
    # changed upstream dependency into the frozen original bundle.
    dependency_refused = bool(binding.validate(binding.canonical(anchor[task]), anchor[task], ROOT, overlays=overlay)) if overlay else None
    if case['expected'] == 'ASSEMBLED_EXACT_SEMANTIC_PAYLOAD':
        matched = assembled and payload_matches
    elif case['expected'] == 'NO_ASSEMBLY':
        matched = not assembled
    else:
        matched = dependency_refused is True
    rows.append({**case, 'command': command, 'case_root': str(case_root), 'exit_code': process.returncode,
                 'wall_seconds': time.monotonic()-started, 'output_exists': candidate.is_file(), 'assembled': assembled,
                 'baseline_payload_equal_except_timestamp': payload_matches, 'unsafe_marker_in_assembled_notes': unsafe_marker,
                 'frozen_dependency_envelope_refuses_mutation': dependency_refused,
                 'matches_predeclared_expectation': bool(matched), 'technical_acceptance_granted': False,
                 'source_program_executed': False, 'new_model_call': False})
result = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'protocol_sha256': binding.digest(protocol_raw),
          'capsule': str(capsule.relative_to(ROOT)), 'capsule_sha256': binding.digest(capsule.read_bytes()),
          'restored_dependencies': len(protocol['dependencies']), 'records': rows,
          'baseline_exact_semantic_payload_replays': {'numerator': sum(r['baseline_payload_equal_except_timestamp'] is True for r in rows), 'denominator': 3},
          'missing_or_stale_inputs_prevent_assembly': {'numerator': sum(not r['assembled'] for r in rows if r['expected']=='NO_ASSEMBLY'), 'denominator': 12},
          'tampered_dependency_unsafe_assembly': {'numerator': sum(r['assembled'] and r['unsafe_marker_in_assembled_notes'] for r in rows if r['expected']=='REQUIRES_DEPENDENCY_PIN'), 'denominator': 6},
          'dependency_envelope_refuses_tampering': {'numerator': sum(r['frozen_dependency_envelope_refuses_mutation'] is True for r in rows if r['expected']=='REQUIRES_DEPENDENCY_PIN'), 'denominator': 6},
          'scope': 'Owned research renderer and tampered caller-owned dependencies; not production source defect certification or semantic-admission FAR. Assembly still requires complete-note review; no negative output promoted.',
          'model_calls': 0, 'optimizer_updates': 0, 'gold': 0}
with (P/'renderer-recovery-results-v1.json').open('x') as stream:
    json.dump(result, stream, indent=2, ensure_ascii=False)
    stream.write('\n')
print(json.dumps({key: result[key] for key in ['baseline_exact_semantic_payload_replays', 'missing_or_stale_inputs_prevent_assembly', 'tampered_dependency_unsafe_assembly', 'dependency_envelope_refuses_tampering']}))
