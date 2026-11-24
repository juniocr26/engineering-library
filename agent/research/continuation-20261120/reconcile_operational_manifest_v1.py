"""Preserve old lock, verify exact minimal reconciliation, then replace atomically."""
import copy
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
TARGET = ROOT / 'agent/recovery/manifest.json'
spec = importlib.util.spec_from_file_location('recovery_bootstrap', ROOT / 'agent/recovery/bootstrap.py')
bootstrap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bootstrap)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    original = TARGET.read_bytes()
    baseline = json.loads((P / 'baseline.json').read_text())
    # Freeze exact before state; do not absorb concurrent owner changes.
    expected_before = 'b378150267ec47d67248c86c48e271556e36be0387bd457a4aa8462c46c82e6b'
    if sha(original) != expected_before:
        raise ValueError('operational manifest no longer equals inspected preimage')
    before = json.loads(original)
    old_candidate = json.loads((ROOT / 'agent/research/documentation-intelligence-20261120/recovery-manifest-candidate-v1.json').read_text())
    approved_changes = old_candidate['documentation_intelligence_20261120_candidate_supplement']['changes']
    new = copy.deepcopy(before)
    changes = []
    for change in approved_changes:
        matches = [i for i, entry in enumerate(new['operational_files']) if entry == change['before']]
        if len(matches) != 1:
            raise ValueError('expected before entry not unique')
        after = change['after']
        raw = (ROOT / after['path']).read_bytes()
        if len(raw) != after['size'] or sha(raw) != after['sha256']:
            raise ValueError('replacement evidence bytes changed')
        new['operational_files'][matches[0]] = copy.deepcopy(after)
        changes.append(change)
    if len(changes) != 3 or new['model'] != before['model']:
        raise ValueError('unexpected reconciliation scope')
    bootstrap.check_knowledge(new)
    bootstrap.model_metadata(new)
    archive_root = ROOT / '.local-backups/continuation-20261120/recovery-manifests'
    archive_root.mkdir(parents=True, exist_ok=True)
    archive = archive_root / (sha(original) + '.json')
    with archive.open('xb') as stream:
        stream.write(original);stream.flush();os.fsync(stream.fileno())
    if archive.read_bytes() != original:
        raise ValueError('preimage preservation failed')
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    supplement = {'at': now, 'authorization': 'authorized-request.txt section2: safe report-reference/manifest migration; exact content preserved and recovery verified.',
                  'prior_manifest': str(archive.relative_to(ROOT)), 'prior_manifest_sha256': sha(original),
                  'changes': changes, 'reason': 'Reconcile pre-existing missing historical root report and two stale current-tool identities without recreating the old report or changing model artifacts.',
                  'old_sealed_manifests_modified': False, 'model_object_changed': False,
                  'owner_approved_training_gold': False, 'remote_or_cold_boot_recovery_claimed': False}
    new.setdefault('continuation_20261120_manifest_reconciliations', []).append(supplement)
    encoded = (json.dumps(new, indent=2, ensure_ascii=False) + '\n').encode()
    candidate = P / 'operational-manifest-reconciled-v1.json'
    with candidate.open('xb') as stream:
        stream.write(encoded)
    bootstrap.check_knowledge(json.loads(encoded))
    bootstrap.model_metadata(json.loads(encoded))
    if TARGET.read_bytes() != original:
        raise ValueError('owner manifest changed before replacement; preserved candidate only')
    temporary = TARGET.with_name('manifest.continuation-20261120.tmp')
    with temporary.open('xb') as stream:
        stream.write(encoded);stream.flush();os.fsync(stream.fileno())
    if temporary.read_bytes() != encoded or TARGET.read_bytes() != original:
        raise ValueError('manifest replacement preconditions changed')
    os.replace(temporary, TARGET)
    descriptor = os.open(TARGET.parent, os.O_RDONLY)
    try:os.fsync(descriptor)
    finally:os.close(descriptor)
    installed = json.loads(TARGET.read_bytes())
    bootstrap.check_knowledge(installed)
    bootstrap.model_metadata(installed)
    if TARGET.read_bytes() != encoded or installed['model'] != before['model']:
        raise ValueError('post-install identity mismatch; preserve both states for owner review')
    receipt = {'at': now, 'status': 'RECONCILED_AND_NORMAL_KNOWLEDGE_VALIDATION_PASSES',
               'manifest_before_sha256': sha(original), 'manifest_after_sha256': sha(encoded),
               'operational_files': len(installed['operational_files']), 'changes': changes,
               'archive': str(archive.relative_to(ROOT)), 'model_object_unchanged': True,
               'baseline_head': baseline.get('head'), 'neural_training': False,
               'cold_boot_verified': False, 'remote_persistence_verified': False}
    with (P / 'operational-manifest-reconciliation-receipt-v1.json').open('x') as stream:
        json.dump(receipt, stream, indent=2)
    print(json.dumps({k:v for k,v in receipt.items() if k != 'changes'}))


if __name__ == '__main__':
    main()
