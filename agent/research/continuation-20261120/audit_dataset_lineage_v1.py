"""Metadata-only graph and integrity audit of preserved V10, no training export."""
from collections import Counter, defaultdict
import datetime
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
manifest_path = ROOT / 'agent/research/documentation-intelligence-20261119/datasets/v10/manifest.json'
manifest = json.loads(manifest_path.read_text())
rows = []
file_checks = []
for entry in manifest['files']:
    path = ROOT / entry['path'];raw = path.read_bytes()
    current = [json.loads(line) for line in raw.decode().splitlines() if line.strip()]
    file_checks.append({'path': entry['path'], 'sha256': hashlib.sha256(raw).hexdigest(), 'records': len(current),
                        'matches_manifest': hashlib.sha256(raw).hexdigest() == entry['sha256'] and len(raw) == entry['bytes'] and len(current) == entry['records']})
    rows.extend(dict(row, audit_file=entry['path']) for row in current)
ids = [row['id'] for row in rows]
lineages = defaultdict(list)
families = defaultdict(list)
for row in rows:
    lineages[str(row.get('lineage_group'))].append(row)
    families[str(row.get('source_family'))].append(row)
pairs = []
for lineage, members in sorted(lineages.items()):
    chapters = [m for m in members if m['category'] == 'SOURCE_REVIEWED_DOCUMENT_CANDIDATE']
    faqs = [m for m in members if m['category'] == 'SOURCE_REVIEWED_FAQ_CANDIDATE']
    if chapters or faqs:
        pairs.append({'lineage_group': lineage, 'source_families': sorted(set(m['source_family'] for m in members)),
                      'chapter_rows': len(chapters), 'faq_rows': len(faqs),
                      'languages': dict(Counter(m.get('language') for m in chapters + faqs)),
                      'chapter_faq_derivative_overlap': bool(chapters and faqs),
                      'faq_question_groups': len(set(json.dumps(m.get('question_identity'), sort_keys=True) for m in faqs)),
                      'split_labels': sorted(set(m.get('split', 'MISSING') for m in members))})
# Ancestry groups use declared source family. Shared review/manifests are not automatically
# equated to source ancestry; that would merge unrelated subjects without evidence.
family_components = []
for family, members in sorted(families.items()):
    family_components.append({'source_family': family, 'records': len(members),
                              'lineage_groups': sorted(set(str(m.get('lineage_group')) for m in members)),
                              'categories': dict(Counter(m['category'] for m in members)),
                              'split_labels': sorted(set(m.get('split', 'MISSING') for m in members)),
                              'owner_approved_rows': sum(m.get('owner_approved') is True for m in members),
                              'training_gold_rows': sum(m.get('training_gold') is True for m in members)})
refs = {}
for row in rows:
    for field, value in row.items():
        if field.endswith('_ref') and isinstance(value, dict) and isinstance(value.get('path'), str) and isinstance(value.get('sha256'), str):
            key = (value['path'], value['sha256'])
            refs.setdefault(key, {'fields': set(), 'row_ids': []})
            refs[key]['fields'].add(field);refs[key]['row_ids'].append(row['id'])
reference_checks = []
for (path, expected), consumers in sorted(refs.items()):
    relative = Path(path)
    if relative.is_absolute() or '..' in relative.parts:
        reference_checks.append({'path': path, 'status': 'UNSAFE_PATH_NOT_READ'})
        continue
    source = ROOT / relative
    if source.is_symlink() or any(parent.is_symlink() for parent in source.parents):
        reference_checks.append({'path': path, 'status': 'SYMLINK_NOT_READ'})
        continue
    if not source.is_file():
        status = 'MISSING'
    else:
        # All are frozen, explicitly registered dataset references under this repo.
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        status = 'MATCH' if digest == expected else 'HASH_MISMATCH'
    reference_checks.append({'path': path, 'expected_sha256': expected, 'status': status,
                              'reference_fields': sorted(consumers['fields']), 'consumer_count': len(consumers['row_ids'])})
rights = manifest['rights_provenance'];raw = (ROOT / rights['path']).read_bytes()
rights_data = json.loads(raw)
rights_checks = []
for repo in rights_data.get('repositories', []):
    checked = []
    for license in repo.get('license_records', []):
        path = ROOT / license['frozen_path']
        raw = path.read_bytes() if path.is_file() else b''
        checked.append({'path': license['frozen_path'], 'matches': len(raw) == license['bytes'] and hashlib.sha256(raw).hexdigest() == license['sha256']})
    rights_checks.append({'repository': repo['repository'], 'frozen_revision': repo.get('frozen_revision'),
                          'license_records': checked, 'rights_status': repo.get('rights_status'),
                          'not_training_approval': True})
report = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'manifest_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
          'file_checks': file_checks, 'total_rows': len(rows), 'unique_row_ids': len(set(ids)),
          'duplicate_ids': [k for k,v in Counter(ids).items() if v > 1],
          'categories': dict(Counter(r['category'] for r in rows)), 'declared_family_count': len(families),
          'declared_lineage_groups': len(lineages), 'family_components': family_components,
          'chapter_faq_groups': pairs, 'reference_checks': reference_checks,
          'reference_status_counts': dict(Counter(r['status'] for r in reference_checks)),
          'rights_snapshot_matches': hashlib.sha256((ROOT / rights['path']).read_bytes()).hexdigest() == rights['sha256'],
          'rights_evidence': rights_checks,
          'flags': {flag: dict(Counter(str(r.get(flag, 'MISSING')) for r in rows)) for flag in ['owner_approved', 'training_gold', 'training_use_approved', 'automatic_trainer_consumer']},
          'rows_without_top_level_source_revision': sum(not r.get('source_revision') for r in rows),
          'revision_warning': 'Missing top-level revision is a schema gap, not proof of unknown source; inspect pinned task/request/evidence references before adjudication.',
          'split_policy': 'Group revisions, language pairs, chapter/FAQ derivatives and helpers under source ancestry; no automatic train/eval split created.',
          'not_independent_examples': True, 'approved_gold_count': sum(r.get('training_gold') is True and r.get('owner_approved') is True for r in rows),
          'training_export_created': False, 'source_datasets_modified': False,
          'rights_interpretation': 'Primary bytes are consistency evidence; license/confidentiality/training approvals remain explicit owner review gates.'}
with (P / 'dataset-lineage-audit-v1.json').open('x') as stream:json.dump(report, stream, indent=2)
print(json.dumps({k: report[k] for k in ['total_rows', 'unique_row_ids', 'declared_family_count', 'declared_lineage_groups', 'reference_status_counts', 'rows_without_top_level_source_revision', 'approved_gold_count']}))
