"""Normalize only explicit current candidate schemas into a root-relative review index."""
import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys

sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
ROOT = P.parents[2]
sys.path.insert(0, str(ROOT / 'agent/tools'))
import documentation_workspace as workspace

audit = json.loads((P / 'faq-identity-overlap-audit-v8.json').read_text())
chapters, failures, files_read = [], [], {}

def relative(path):
    assert not Path(path).is_absolute(), 'absolute metadata path refused: ' + str(path)
    text = PurePosixPath(path).as_posix()
    workspace.relative_path(text)
    return text

def beneath_research(path):
    return relative(str(P.relative_to(ROOT) / relative(path)))

def read(fd, path):
    path = relative(path)
    if path not in files_read:
        raw, meta = workspace.read(fd, path, 1024 * 1024)
        files_read[path] = (raw, meta)
    return files_read[path]

with workspace.directory(str(ROOT)) as root_fd:
    for ledger_name, family in audit['selected_current_chapter_versions']:
        ledger_path = beneath_research(ledger_name)
        ledger_raw, ledger_meta = read(root_fd, ledger_path)
        ledger = json.loads(ledger_raw)
        assert ledger['owner_approved'] is False and ledger['training_gold'] is False
        if ledger_name.startswith('jmespath-'):
            pack = json.loads((P / 'jmespath-source-evidence-pack-v1.json').read_text())
            units = pack['units']
        elif ledger_name.startswith('self-'):
            pack = json.loads((P / 'self-chapter-supplement-evidence-v4.json').read_text())
            units = {unit['id']: unit for unit in pack['units']}
        elif ledger_name.startswith('totalist-'):
            units = ledger['evidence']
        elif ledger_name.startswith('mlx-'):
            pack = json.loads((P / ledger['source_pack']).read_text())
            units = pack['units']
        else:
            units = ledger['units']
        if type(ledger.get('files')) is dict:
            candidates = [{'path': beneath_research(name), 'sha256': value['sha256']}
                          for name, value in ledger['files'].items()]
        elif 'candidate_hashes' in ledger:
            candidates = [{'path': beneath_research(name), 'sha256': value} for name, value in ledger['candidate_hashes'].items()]
        else:
            assert ledger['file_path_policy'] == 'EXPLICIT_REPOSITORY_RELATIVE_FILES_NO_HOST_PATH_FALLBACK'
            candidates = [{'path': relative(row['path']), 'sha256': row['sha256']} for row in ledger['files']]
        for candidate in candidates:
            raw, meta = read(root_fd, candidate['path'])
            assert meta['sha256'] == candidate['sha256'], candidate['path']
            candidate.update(bytes=len(raw), kind='BILINGUAL_CHAPTER' if Path(candidate['path']).stem in ['en', 'pt-br'] else 'AUXILIARY_ILLUSTRATIVE_EXAMPLE_NOT_EXECUTED_BY_THIS_AUDIT')
        assert sorted(Path(row['path']).stem for row in candidates if row['kind'] == 'BILINGUAL_CHAPTER') == ['en', 'pt-br']
        normalized_units = {}
        for identity, unit in units.items():
            try:
                if 'source_snapshot' in unit:
                    path = beneath_research(unit['source_snapshot'])
                elif ledger_name.startswith('jmespath-'):
                    path = beneath_research('new-public-sources-v1/jmespath--jmespath.py/' + unit['revision'] + '/' + unit['source_path'])
                elif ledger_name.startswith('go-geom-'):
                    path = beneath_research('new-public-sources-v1/twpayne--go-geom/' + ledger['revision'] + '/' + unit['source_path'])
                elif ledger_name.startswith('httpx-'):
                    repository = 'encode--httpcore' if unit['path'].startswith('httpcore/') else 'encode--httpx'
                    path = beneath_research('new-public-sources-v1/' + repository + '/' + unit['revision'] + '/' + unit['path'])
                elif ledger_name.startswith('totalist-'):
                    path = beneath_research(unit['path'])
                elif ledger_name.startswith('self-'):
                    path = relative(unit['source_path'])
                else:
                    path = relative(unit.get('local_evidence_path', unit['path']))
                raw, meta = read(root_fd, path)
                assert meta['sha256'] == unit['source_sha256'], 'source hash mismatch'
                evidence = unit.get('evidence', unit)
                first, last, quote = evidence['first_line'], evidence['last_line'], evidence['quote']
                assert type(first) is int and type(last) is int and 1 <= first <= last
                full = ''.join(raw.decode().splitlines(keepends=True)[first - 1:last])
                go = b'\n'.join(raw.split(b'\n')[first - 1:last]).decode() if path.endswith('.go') else None
                style = 'FULL_PHYSICAL_LINES' if quote == full else 'GO_PARSER_LINES_NO_FINAL_LF' if quote == go else None
                assert style is not None, 'exact physical quote differs'
                assert hashlib.sha256(quote.encode()).hexdigest() == evidence['quote_sha256'], 'quote hash differs'
                normalized_units[identity] = {'path': path, 'source_sha256': meta['sha256'],
                    'first_line': first, 'last_line': last, 'quote_sha256': evidence['quote_sha256'],
                    'physical_range_style': style, 'quote_bytes': len(quote.encode())}
            except (AssertionError, KeyError, TypeError, ValueError, OSError) as error:
                failures.append({'ledger': ledger_name, 'unit': identity, 'error': str(error)[:800], 'unit_fields': list(unit)})
        for claim in ledger['claims']:
            refs = claim.get('evidence_ids', claim.get('evidence', claim.get('source_units')))
            assert type(refs) is list and refs and all(identity in units for identity in refs), (ledger_name, claim['id'])
        chapters.append({'family': family, 'ledger_path': ledger_path, 'ledger_sha256': ledger_meta['sha256'],
            'claims': len(ledger['claims']), 'faq_pairs': len(ledger['faq']), 'files': candidates, 'source_units': normalized_units,
            'owner_approved': False, 'training_gold': False, 'training_use_approved': False,
            'active_published_catalog_entry': False, 'automatic_candidate_applier_supported': False})
    for path, (_, meta) in files_read.items():
        _, after = workspace.read(root_fd, path, 1024 * 1024)
        assert after['sha256'] == meta['sha256'], 'input changed during index audit: ' + path
    assert workspace.same_root(str(ROOT), root_fd)

record = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'status': 'CURRENT_CANDIDATE_RELATIVE_INDEX_VERIFIED' if not failures else 'OWNED_INDEX_ADAPTER_REQUIRES_REVIEW',
    'chapters': chapters, 'source_card_failures': failures, 'candidate_chapters': len(chapters),
    'chapter_language_files': sum(row['kind'] == 'BILINGUAL_CHAPTER' for chapter in chapters for row in chapter['files']),
    'source_reviewed_claims': sum(chapter['claims'] for chapter in chapters),
    'chapter_derived_FAQ_pairs': sum(chapter['faq_pairs'] for chapter in chapters),
    'physical_source_units_bound': sum(len(chapter['source_units']) for chapter in chapters),
    'distinct_files_read': len(files_read), 'relative_path_policy': 'Explicit repository-relative current schemas only; no host absolute path fallback or implicit journal migration.',
    'scope': 'Isolated source-reviewed candidate index, not the active catalog. Source bytes, ranges and candidate identity only; not generic semantic entailment, independent examples, runtime behavior or owner approval.',
    'source_executed': False, 'model_calls': 0, 'optimizer_steps': 0, 'owner_gold': 0,
    'permanent_tests_modified': False, 'published_catalog_modified': False}
name = 'current-documentation-candidate-index-v1.json' if not failures else 'current-candidate-index-build-attempt-v1.json'
with (P / name).open('x') as stream:
    json.dump(record, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({key: record[key] for key in ['status', 'candidate_chapters', 'chapter_language_files', 'source_reviewed_claims', 'chapter_derived_FAQ_pairs', 'physical_source_units_bound', 'distinct_files_read']}))
if failures:
    print(json.dumps(failures))
    raise SystemExit(1)
