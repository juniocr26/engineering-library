"""Read current candidate identities and physical source cards from one explicit root."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
CODE_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(CODE_ROOT / 'agent/tools'))
import documentation_workspace as workspace

def verify(root, index_relative):
    cache, chapters, cards, documents, examples = {}, 0, 0, 0, 0
    with workspace.directory(str(root)) as fd:
        def read(relative):
            workspace.relative_path(relative)
            if relative not in cache:
                cache[relative] = workspace.read(fd, relative, 1024 * 1024)
            return cache[relative]
        raw, index_meta = read(index_relative)
        index = json.loads(raw)
        assert index['status'] == 'CURRENT_CANDIDATE_RELATIVE_INDEX_VERIFIED'
        assert not index['source_card_failures']
        assert index['source_executed'] is False and index['owner_gold'] == 0
        for chapter in index['chapters']:
            chapters += 1
            assert all(chapter[flag] is False for flag in ['owner_approved', 'training_gold', 'training_use_approved', 'active_published_catalog_entry', 'automatic_candidate_applier_supported'])
            _, ledger_meta = read(chapter['ledger_path'])
            assert ledger_meta['sha256'] == chapter['ledger_sha256']
            for file in chapter['files']:
                body, metadata = read(file['path'])
                assert metadata['sha256'] == file['sha256'] and len(body) == file['bytes']
                if file['kind'] == 'BILINGUAL_CHAPTER': documents += 1
                else: examples += 1
            for identity, unit in chapter['source_units'].items():
                source, metadata = read(unit['path'])
                assert metadata['sha256'] == unit['source_sha256'], (chapter['family'], identity)
                first, last = unit['first_line'], unit['last_line']
                assert type(first) is int and type(last) is int and 1 <= first <= last
                if unit['physical_range_style'] == 'FULL_PHYSICAL_LINES':
                    lines = source.decode().splitlines(keepends=True)
                    assert last <= len(lines)
                    quote = ''.join(lines[first - 1:last]).encode()
                else:
                    assert unit['physical_range_style'] == 'GO_PARSER_LINES_NO_FINAL_LF' and unit['path'].endswith('.go')
                    lines = source.split(b'\n')
                    assert last <= len(lines)
                    quote = b'\n'.join(lines[first - 1:last])
                assert len(quote) == unit['quote_bytes'] and hashlib.sha256(quote).hexdigest() == unit['quote_sha256']
                cards += 1
        assert chapters == index['candidate_chapters'] and documents == index['chapter_language_files'] and cards == index['physical_source_units_bound']
        for relative, (_, metadata) in cache.items():
            _, current = workspace.read(fd, relative, 1024 * 1024)
            assert current['sha256'] == metadata['sha256'], 'input changed: ' + relative
        assert workspace.same_root(str(root), fd)
    return {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'status': 'CURRENT_CANDIDATE_INDEX_CONSUMED_FROM_EXPLICIT_ROOT',
            'root': str(root), 'index_relative': index_relative, 'index_sha256': index_meta['sha256'],
            'reader_source': str(Path(__file__).resolve()), 'reader_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'workspace_source': str(Path(workspace.__file__).resolve()),
            'reader_and_workspace_loaded_from_selected_root': Path(__file__).resolve().is_relative_to(root) and Path(workspace.__file__).resolve().is_relative_to(root),
            'candidate_chapters': chapters, 'language_documents': documents, 'auxiliary_examples_read_not_executed': examples,
            'physical_source_cards': cards, 'distinct_files_read': len(cache), 'all_read_inputs_unchanged': True,
            'source_executed': False, 'model_calls': 0, 'optimizer_steps': 0, 'owner_gold': 0,
            'published_catalog_modified': False, 'automatic_candidate_applier_used': False,
            'limits': 'Integrity/relative-path/physical-range consumption only. No generic prose entailment, installed package identity, arbitrary journal rebinding or training/publication approval.'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=CODE_ROOT)
    parser.add_argument('--index', default='agent/research/continuation-20261120/current-documentation-candidate-index-v1.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.root.resolve(), args.index)
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({key: result[key] for key in ['status', 'candidate_chapters', 'language_documents', 'physical_source_cards', 'distinct_files_read', 'reader_and_workspace_loaded_from_selected_root']}))
