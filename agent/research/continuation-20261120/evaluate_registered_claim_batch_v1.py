"""Frozen multi-claim and relocation controls, only on exclusive owned data."""
import copy
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path

P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('observed_batch', P / 'registered_claim_batch_v1.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
protocol = json.loads((P / 'registered-claim-batch-protocol-v1.json').read_text())
source_protocol = json.loads((P / 'registered-slugify-real-protocol-v1.json').read_text())
base_packet = source_protocol['cases'][0]['packet']
sha = lambda raw: hashlib.sha256(raw).hexdigest()
base = Path('/private/tmp/el-claim-batch-controls-20261120-v1')
base.mkdir(mode=0o700, exist_ok=False)
rows = []
for definition in protocol['expected_controls']:
    identity = definition['id']
    case = base / identity
    case.mkdir()
    docs = case / 'docs'
    docs.mkdir()
    source_registration = copy.deepcopy(source_protocol['registration'])
    source_registration['contracts']['slugify.slugify'] = {'selector': 'slugify', 'previous_path': 'slugify/slugify.py', 'current_path': 'slugify/slugify.py'}
    relocated = identity == 'two-modifications-with-registered-synthetic-relocation'
    for when, key in [('previous', 'previous_source'), ('current', 'current_source')]:
        root = case / ('source-' + when)
        root.mkdir()
        path = 'relocated/slugify.py' if relocated and when == 'current' else 'slugify/slugify.py'
        target = root / path
        target.parent.mkdir(parents=True)
        raw = base_packet[key].encode()
        target.write_bytes(raw)
        license_origin = Path(source_registration['sources'][when]['root']) / 'LICENSE'
        (root / 'LICENSE').write_bytes(license_origin.read_bytes())
        source_registration['sources'][when].update(root=str(root), files={path: sha(raw)})
        for contract in source_registration['contracts'].values():
            contract[when + '_path'] = path
    first = copy.deepcopy(base_packet)
    first.update(id='batch-allow-unicode', logical_contract_id='slugify.slugify', documentation={'en': 'slugify has no allow_unicode parameter.', 'pt-br': 'slugify não possui parâmetro allow_unicode.'})
    second = copy.deepcopy(base_packet)
    second.update(id='batch-renamed-formal', logical_contract_id='slugify.smart_truncate', documentation={'en': 'smart_truncate has a word_boundaries parameter.', 'pt-br': 'smart_truncate possui parâmetro word_boundaries.'})
    replacements = [
        {'en': 'slugify has a allow_unicode parameter.\n', 'pt-br': 'slugify possui parâmetro allow_unicode.\n'},
        {'en': 'smart_truncate has a word_boundary parameter.\n', 'pt-br': 'smart_truncate possui parâmetro word_boundary.\n'},
    ]
    requests = [{'claim_id': packet['logical_contract_id'], 'packet': packet, 'replacements': copy.deepcopy(replacement), 'action': 'MODIFY'} for packet, replacement in zip([first, second], replacements, strict=True)]
    if identity == 'modify-plus-addressed-noop':
        second['documentation'] = {language: text[:-1] for language, text in replacements[1].items()}
        requests[1]['action'] = 'NO-OP'
        requests[1]['replacements'] = None
    entries, claims, originals = {}, {}, {}
    for language in ['en', 'pt-br']:
        chunks = [b'# Human introduction remains byte-exact.\n\n']
        for index, packet in enumerate([first, second]):
            claim = packet['logical_contract_id']
            body = (packet['documentation'][language] + '\n').encode()
            chunks.extend([('<!-- documentation-agent:claim:' + claim + ':start -->\n').encode(), body, ('<!-- documentation-agent:claim:' + claim + ':end -->\n').encode(), b'\nIndependent human context between/after claims.\n'])
            claims.setdefault(claim, {'block_sha256': {}})['block_sha256'][language] = sha(body)
        chunks.append(b'\nHuman ending; navigation and citations are separately unverified.\n')
        raw = b''.join(chunks)
        (docs / (language + '.md')).write_bytes(raw)
        originals[language] = raw
        entries[language] = {'path': language + '.md', 'file_sha256': sha(raw)}
    registration = {'schema_version': 1, 'scope': 'paired-claim-batch-review', 'source_registration': source_registration, 'documentation_root': str(docs), 'documents': entries, 'claims': claims, 'managed_ownership': True, 'human_authored': False}
    (case / 'exact-inputs.json').write_text(json.dumps({'registration': registration, 'requests': requests, 'original_documents': {k: v.decode() for k, v in originals.items()}, 'source_relocation_is_synthetic': relocated}, ensure_ascii=False, indent=2) + '\n')
    if identity == 'duplicate-claim-conflict':
        requests.append(copy.deepcopy(requests[0]))
    elif identity == 'second-claim-invalid-replacement':
        requests[1]['replacements']['pt-br'] = 'smart_truncate possui parâmetro word_boundaries.\n'
    elif identity == 'second-claim-stale-block':
        registration['claims']['slugify.smart_truncate']['block_sha256']['pt-br'] = '0' * 64
    elif identity == 'empty-operation-list':
        requests = []
    elif identity == 'operation-count-over-bound':
        requests = [copy.deepcopy(requests[0]) for _ in range(9)]
    elif identity == 'unsupported-retirement-in-batch':
        requests[1]['action'] = 'REMOVE'
    elif identity == 'unknown-claim-id':
        requests[1]['claim_id'] = 'slugify.unknown'
        requests[1]['packet']['logical_contract_id'] = 'slugify.unknown'
    child_calls = []
    try:
        batch = module.RegisteredClaimBatch(registration)
        for index, child in enumerate(batch.children.values()):
            original_prepare = child.prepare

            def wrapped(packet, replacement, action, index=index, original_prepare=original_prepare):
                observed = original_prepare(packet, replacement, action)
                child_calls.append(index)
                if observed.get('status') != 'PREPARED':
                    return observed
                if index == 1 and identity == 'second-child-missing-language':
                    observed['candidates'].pop('pt-br')
                if index == 0 and identity == 'child-output-hash-mismatch':
                    observed['candidates']['en']['markdown'] += 'Unexpected output drift.\n'
                if index == 0 and identity == 'child-modifies-other-claim-body':
                    item = observed['candidates']['en']
                    item['markdown'] = item['markdown'].replace('smart_truncate has a word_boundaries parameter.', 'smart_truncate has a word_boundary parameter.')
                    item['candidate_sha256'] = sha(item['markdown'].encode())
                if index == 0 and identity == 'child-fabricates-authority':
                    observed['owner_approved'] = True
                if index == 0 and identity == 'child-source-execution-uncertain':
                    observed['source_executed'] = None
                if index == 0 and identity == 'document-changes-between-children':
                    (docs / 'pt-br.md').write_bytes(originals['pt-br'] + b'Concurrent owned document edit.\n')
                if index == 0 and identity == 'source-path-replaced-between-children':
                    entry = source_registration['sources']['current']
                    path = Path(entry['root']) / next(iter(entry['files']))
                    raw = path.read_bytes()
                    path.rename(case / 'exact-preserved-current-source.py')
                    path.write_bytes(raw)
                if index == 0 and identity == 'batch-root-replaced-between-children':
                    docs.rename(case / 'retained-original-doc-root')
                    docs.mkdir()
                    for language, raw in originals.items():
                        (docs / (language + '.md')).write_bytes(raw)
                return observed

            child.prepare = wrapped
        observed = batch.prepare(requests)
    except (ValueError, TypeError, KeyError, OSError) as error:
        observed = {'status': 'REFUSED', 'reason': str(error), 'writes': 0, 'source_executed': False}
    status = observed['status']
    if status == 'REFUSED':
        assert 'candidates' not in observed, 'partial batch candidate escaped'
        if identity == 'child-source-execution-uncertain':
            assert observed['source_executed'] is None
    else:
        assert set(observed['candidates']) == {'en', 'pt-br'} and len(observed['operations']) == 2
        for language, item in observed['candidates'].items():
            raw = item['markdown'].encode()
            assert b'# Human introduction remains byte-exact.\n\n' in raw
            assert raw.count(b'Independent human context between/after claims.\n') == 2
            assert b'Human ending; navigation and citations are separately unverified.\n' in raw
            assert replacements[0][language].encode() in raw and replacements[1][language].encode() in raw
            assert sha(raw) == item['candidate_sha256']
    rows.append({'id': identity, 'expected': definition['expected'], 'actual': status, 'matches': status == definition['expected'], 'child_call_sequence': child_calls, 'result': observed, 'synthetic_relocation': relocated})
record = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'rows': rows, 'correct': sum(r['matches'] for r in rows), 'n': len(rows), 'owned_root': str(base), 'producer_sha256': sha((P / 'registered_claim_batch_v1.py').read_bytes()), 'source_family_count': 1, 'function_contract_count': 2, 'source_executed': False, 'neural_model_calls': 0, 'production_or_public_source_modified': False, 'original_catalog_written': False, 'permanent_tests_modified': False, 'synthetic_source_copies_and_documents_mutated_only_by_owned_control_factory': True}
with (P / 'registered-claim-batch-results-v1.json').open('x') as stream:
    stream.write(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'correct': record['correct'], 'n': len(rows), 'failures': [{'id': r['id'], 'reason': r['result'].get('reason')} for r in rows if not r['matches']]}))
