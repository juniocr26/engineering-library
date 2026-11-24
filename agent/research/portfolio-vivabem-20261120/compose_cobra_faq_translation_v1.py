"""Research-only immutable-body composition, never a source-truth approval."""
import datetime
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent
protocol_path = P / 'cobra-faq-translation-protocol-v1.json'
freeze_path = P / 'cobra-faq-translation-request-freeze-v1.json'
protocol = json.loads(protocol_path.read_text())
freeze = json.loads(freeze_path.read_text())
assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == freeze['composer_sha256']
assert hashlib.sha256(protocol_path.read_bytes()).hexdigest() == freeze['protocol_sha256']
folder = P / 'cobra-faq-translation-v1'
outcome = json.loads((folder / 'outcome.json').read_text())
content_path = folder / 'model-content.txt'
result_path = P / 'cobra-faq-translation-composition-v1.json'
assert not result_path.exists(), 'Do not overwrite earlier composition evidence'


def strict_pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('Duplicate JSON key')
        result[key] = value
    return result


record = {
    'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'protocol': protocol_path.name,
    'status': 'BLOCKED_BEFORE_FULL_CHAPTER_COMPOSITION',
    'full_chapter_composed': False,
    'model_contribution': 'Only Portuguese FAQ question/answer translation of fixed reviewed English text.',
    'model_wording_repaired': False,
    'owner_approved': False,
    'training_gold': False,
    'publication_authorized': False,
    'production_or_external_writes': 0,
}
try:
    if outcome.get('returncode') != 0 or outcome.get('done') is not True or outcome.get('done_reason') != 'stop':
        raise ValueError('Completed normal-stop transport required before composition')
    raw_path = folder / 'raw-response.json'
    if hashlib.sha256(raw_path.read_bytes()).hexdigest() != outcome['raw_response_sha256']:
        raise ValueError('Raw response receipt mismatch')
    content = content_path.read_text()
    if json.loads(raw_path.read_text())['message']['content'] != content:
        raise ValueError('Model content differs from preserved raw response')
    body = json.loads(content, object_pairs_hook=strict_pairs)
    if not isinstance(body, dict) or set(body) != {'faq'} or not isinstance(body['faq'], list) or len(body['faq']) != 5:
        raise ValueError('Five-item closed FAQ schema required')
    expected_ids = [item['qid'] for item in protocol['source_inputs']]
    translated = {}
    for item in body['faq']:
        if not isinstance(item, dict) or set(item) != {'qid', 'question_pt', 'answer_pt'}:
            raise ValueError('Unexpected translation record schema')
        qid = item['qid']
        if not isinstance(qid, str) or qid not in expected_ids or qid in translated:
            raise ValueError('Unknown or duplicate question ID')
        for key, limit in [('question_pt', 400), ('answer_pt', 1600)]:
            value = item[key]
            if not isinstance(value, str) or not value.strip() or len(value) > limit or any(ord(c) < 32 for c in value):
                raise ValueError('Nonempty bounded single-paragraph strings required')
        translated[qid] = item
    if set(translated) != set(expected_ids):
        raise ValueError('Missing translation record')
    parent = {}
    for item in protocol['parent_files']:
        path = Path(item['path'])
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != item['sha256']:
            raise ValueError('Parent chapter bytes changed since freeze')
        parent[path.name] = raw
    english = parent['en.md']
    portuguese = parent['pt-BR.md']
    marker = '## FAQ\n\n'.encode()
    footer_marker = '\n## Manutenção e limites\n'.encode()
    if portuguese.count(marker) != 1 or portuguese.count(footer_marker) != 1:
        raise ValueError('Unique parent FAQ boundaries required')
    prefix, rest = portuguese.split(marker)
    previous_faq, suffix = rest.split(footer_marker)
    # Exact model strings; only deterministic Markdown wrapping and frozen qid order.
    replacement = '\n\n'.join('**' + translated[q]['question_pt'] + '** ' + translated[q]['answer_pt'] for q in expected_ids).encode() + b'\n'
    composed_pt = prefix + marker + replacement + footer_marker + suffix
    candidate = P / 'cobra-faq-translation-hybrid-v1'
    candidate.mkdir(exist_ok=False)
    (candidate / 'en.md').write_bytes(english)
    (candidate / 'pt-BR.md').write_bytes(composed_pt)
    files = [{'path': str(candidate / name), 'sha256': hashlib.sha256((candidate / name).read_bytes()).hexdigest(),
              'bytes': (candidate / name).stat().st_size} for name in ['en.md', 'pt-BR.md']]
    record.update(status='STRUCTURALLY_COMPOSED_PENDING_COMPLETE_SOURCE_REVIEW', full_chapter_composed=True,
                  files=files, translation_record_ids=expected_ids,
                  english_parent_sha256=hashlib.sha256(english).hexdigest(),
                  portuguese_prefix_with_heading_sha256=hashlib.sha256(prefix + marker).hexdigest(),
                  portuguese_footer_with_heading_sha256=hashlib.sha256(footer_marker + suffix).hexdigest(),
                  source_faq_removed_sha256=hashlib.sha256(previous_faq).hexdigest(),
                  replacement_faq_sha256=hashlib.sha256(replacement).hexdigest(),
                  model_content_sha256=hashlib.sha256(content.encode()).hexdigest(),
                  complete_semantic_approval=False)
except (ValueError, KeyError, TypeError) as error:
    record['reason'] = str(error)

result_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({'status': record['status'], 'full_chapter_composed': record['full_chapter_composed'],
                  'owner_approved': False, 'training_gold': False}))
