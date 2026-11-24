"""Materialize owned bilingual review documents and diffs, with physical source pins."""
import collections
import datetime
import difflib
import hashlib
import json
from pathlib import Path
import sys
import tarfile

sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
ROOT = P.parents[2]
sys.path.insert(0, str(ROOT / 'agent/tools'))
from documentation_workspace import directory, read, write_new

pack_path = P / 'cachetools-lifecycle-evidence-pack-v1.json'
supp_path = P / 'cachetools-lifecycle-previous-binding-supplement-v1.json'
pack, supplement = json.loads(pack_path.read_text()), json.loads(supp_path.read_text())
units = {**pack['units'], **supplement['additional_units']}
targets_path = P / 'cachetools-lifecycle-review-targets-v1.jsonl'
targets = [json.loads(line) for line in targets_path.read_text().splitlines()]
bundle = P / 'cachetools-lifecycle-candidates-v1'
bundle.mkdir(exist_ok=False)
for side in ['previous', 'candidate']:
    for language in ['en', 'pt-br']:
        (bundle / side / language).mkdir(parents=True)
source_bindings = {}
with directory(str(ROOT)) as root_fd:
    for identity, unit in units.items():
        raw, meta = read(root_fd, unit['local_evidence_path'], 65536)
        assert meta['sha256'] == unit['source_sha256']
        quote = ''.join(raw.decode().splitlines(keepends=True)[unit['first_line'] - 1:unit['last_line']])
        assert quote == unit['quote'] and hashlib.sha256(quote.encode()).hexdigest() == unit['quote_sha256']
        source_bindings[unit['local_evidence_path']] = {'path': unit['local_evidence_path'], 'sha256': meta['sha256'], 'bytes': len(raw)}

entries = []
diffs = {'en': [], 'pt-br': []}
for target in targets:
    identity, language, action = target['logical_scenario'], target['language'], target['manual_reference_action']
    relative = language + '/' + identity + '.md'
    def document(answer):
        return ('# ' + target['question'] + '\n\n' + answer + '\n').encode()
    before = None if action == 'ADD' else document(target['documentation_before'])
    if action == 'REMOVE':
        after = None
    elif action in ['NO-OP', 'INCONCLUSIVE']:
        after = before
    else:
        after = document(target['candidate_after'])
    for side, raw in [('previous', before), ('candidate', after)]:
        if raw is not None:
            with directory(str(bundle / side)) as fd:
                write_new(fd, relative, raw)
                observed, metadata = read(fd, relative, 16384)
                assert observed == raw and metadata['sha256'] == hashlib.sha256(raw).hexdigest()
        else:
            assert not (bundle / side / relative).exists()
    entry = {'scenario': identity, 'language': language, 'manual_reference_action': action,
             'previous_path': 'previous/' + relative, 'candidate_path': 'candidate/' + relative,
             'previous': {'exists': before is not None, 'sha256': hashlib.sha256(before).hexdigest() if before is not None else None},
             'candidate': {'exists': after is not None, 'sha256': hashlib.sha256(after).hexdigest() if after is not None else None},
             'evidence_ids': target['evidence_ids'] + supplement['target_evidence_additions'].get(identity, []),
             'previous_is_owner_authored': False, 'physical_published_documentation_certified': False,
             'owner_approved': False, 'automatic_candidate_applier_supported': False}
    entries.append(entry)
    diffs[language].extend(difflib.unified_diff((before or b'').decode().splitlines(keepends=True),
        (after or b'').decode().splitlines(keepends=True), fromfile=entry['previous_path'], tofile=entry['candidate_path']))
for language, lines in diffs.items():
    with (bundle / (language + '.patch.diff')).open('x') as stream:
        stream.writelines(lines)
manifest = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'status': 'OWNED_REVIEW_BUNDLE_NOT_PUBLISHED_OR_AUTOMATICALLY_APPLIED', 'entries': entries,
    'source_bindings': list(source_bindings.values()), 'source_pack_sha256': hashlib.sha256(pack_path.read_bytes()).hexdigest(),
    'previous_binding_supplement_sha256': hashlib.sha256(supp_path.read_bytes()).hexdigest(),
    'targets_sha256': hashlib.sha256(targets_path.read_bytes()).hexdigest(),
    'action_counts_language_entries': dict(collections.Counter(row['manual_reference_action'] for row in entries)),
    'physical_owned_document_inputs_verified': True, 'physical_published_documentation_certified': False,
    'retirement_policy': 'Only named currentMRUAPIentry absent from isolated candidate; exact previous text retained in previous/ and preservation archive, primary explicit notice pinned. No active catalog or human-owned content removed.',
    'source_revision_authentication_scope': 'Locally pinned Git-blob-verified snapshots; no installed distribution identity or independently signed commit authentication.',
    'production_candidate_applier_used': False, 'owner_approved': False, 'training_gold': False,
    'training_use_approved': False, 'publication': False, 'source_executed_by_this_builder': False,
    'workflow_limit': 'Manual reference plus concrete isolated paired documents/diffs for review. Original planner/applier do not support this new source profile; no automatic lifecycle accuracy or live application is claimed.'}
with (bundle / 'manifest.json').open('x') as stream:
    json.dump(manifest, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
backup = ROOT / '.local-backups/continuation-20261120/cachetools-lifecycle-review-v1'
backup.mkdir(exist_ok=False)
archive = backup / 'owned-review-documents-and-patches.tar.gz'
files = sorted(path for path in bundle.rglob('*') if path.is_file())
members = [{'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size} for path in files]
with tarfile.open(archive, 'w:gz') as tar:
    for path in files:
        assert not path.is_symlink()
        tar.add(path, arcname=str(path.relative_to(ROOT)), recursive=False)
with tarfile.open(archive) as tar:
    by_name = {row['path']: row for row in members}
    assert len(tar.getmembers()) == len(members)
    for member in tar.getmembers():
        assert member.isfile()
        raw = tar.extractfile(member).read()
        assert hashlib.sha256(raw).hexdigest() == by_name[member.name]['sha256']
receipt = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'status': manifest['status'],
    'bundle': str(bundle.relative_to(ROOT)), 'members': members, 'source_bindings': list(source_bindings.values()),
    'archive': str(archive.relative_to(ROOT)), 'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
    'archive_bytes': archive.stat().st_size, 'all_archive_members_verified': True,
    'logical_scenarios': 7, 'language_entries': len(entries), 'created_physical_document_files': sum(row[side]['exists'] for row in entries for side in ['previous', 'candidate']),
    'published_files_changed': 0, 'owner_gold': 0, 'optimizer_steps': 0,
    'no_actual_human_authored_documentation_used_or_removed': True}
with (P / 'cachetools-owned-review-bundle-receipt-v1.json').open('x') as stream:
    json.dump(receipt, stream, indent=2)
    stream.write('\n')
print(json.dumps({'members': len(members), 'logical_scenarios': 7, 'language_entries': len(entries), 'source_files_pinned': len(source_bindings), 'archive_bytes': archive.stat().st_size}))
