"""Append-only normalization proposal; distinguish Git, source bytes and task IDs."""
from collections import Counter
import datetime
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
manifest = json.loads((ROOT / 'agent/research/documentation-intelligence-20261119/datasets/v10/manifest.json').read_text())
records = []
for file in manifest['files']:
    for line in (ROOT / file['path']).read_text().splitlines():
        if not line.strip():continue
        row = json.loads(line)
        if row.get('source_revision'):continue
        out = {'record_id': row['id'], 'source_family': row['source_family'], 'lineage_group': row['lineage_group'],
               'original_row_sha256': hashlib.sha256(line.encode()).hexdigest(),
               'source_dataset_path': file['path'], 'owner_approved': False, 'training_gold': False,
               'training_export_allowed': False, 'normalization_role': 'METADATA_PROPOSAL_NOT_NEW_TRAINING_RECORD'}
        request = row.get('request')
        if isinstance(request, dict) and isinstance(request.get('revision'), str):
            revision = request['revision'];source_sha = request.get('expected_sha256')
            kind = 'git-commit-reported-by-frozen-request' if len(revision) == 40 else 'content-digest-revision-not-git' if len(revision) == 64 and revision == source_sha else 'opaque-request-revision'
            out.update(identity_kind=kind, reported_revision=revision, physical_source_sha256=source_sha,
                       evidence={'kind': 'inline-frozen-request', 'request_sha256': hashlib.sha256(json.dumps(request, sort_keys=True, separators=(',', ':')).encode()).hexdigest()},
                       upstream_revision_independently_verified=False)
        else:
            ref = row.get('input_ref') or row.get('source_input_ref') or row.get('request_ref')
            if not isinstance(ref, dict):
                out.update(identity_kind='UNRESOLVED_NO_REGISTERED_TASK_REFERENCE')
            else:
                raw = (ROOT / ref['path']).read_bytes()
                if hashlib.sha256(raw).hexdigest() != ref['sha256']:
                    raise ValueError('frozen reference drift')
                payload = json.loads(raw)
                out['evidence'] = {'path': ref['path'], 'sha256': ref['sha256'], 'immutable_snapshot': ref.get('immutable_snapshot')}
                if isinstance(payload.get('current_source'), str) and isinstance(payload.get('previous_source'), str):
                    out.update(identity_kind='paired-source-content-digests-not-git',
                               previous_source_sha256=hashlib.sha256(payload['previous_source'].encode()).hexdigest(),
                               current_source_sha256=hashlib.sha256(payload['current_source'].encode()).hexdigest(),
                               task_snapshot_sha256=ref['sha256'])
                elif isinstance(payload.get('messages'), list):
                    out.update(identity_kind='model-request-snapshot-no-program-revision-asserted',
                               request_snapshot_sha256=ref['sha256'],
                               note='Diagnostic request identity is recoverable; it must not be relabeled as a source repository commit.')
                else:
                    out.update(identity_kind='registered-evidence-snapshot-requires-schema-review', task_snapshot_sha256=ref['sha256'])
        records.append(out)
with (P / 'dataset-revision-normalization-proposals-v1.jsonl').open('x') as stream:
    for record in records:stream.write(json.dumps(record, sort_keys=True) + '\n')
summary = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'proposals': len(records),
           'identity_kinds': dict(Counter(r['identity_kind'] for r in records)),
           'source_dataset_modified': False, 'new_training_rows': 0,
           'semantic_or_license_approval_added': False,
           'limit': 'Git-shaped values are reported frozen-request identity, not newly authenticated upstream commits. Content/request hashes are distinct identity kinds; no fabricated Git history.'}
with (P / 'dataset-revision-normalization-summary-v1.json').open('x') as stream:json.dump(summary, stream, indent=2)
print(json.dumps(summary))
