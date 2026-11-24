"""Compose isolated candidates only. No source/training/publication approval is produced."""
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def unique_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs)


def compose(method):
    protocol = unique_json((ROOT / 'answerbank-comparison-protocol-v1.json').read_text())
    base_review = unique_json((ROOT / protocol['base_chapter_review']).read_text())
    bank = {row['answer_id']: row for row in protocol['shared_bank']}
    questions = protocol['shared_questions']
    folder = ROOT / 'answerbank-comparison-v1' / method
    outcome = unique_json((folder / 'outcome.json').read_text())
    if outcome['returncode'] != 0 or not outcome.get('done'):
        raise ValueError('no terminal successful transport')
    raw_path = folder / 'raw-response.json'
    if hashlib.sha256(raw_path.read_bytes()).hexdigest() != outcome['raw_response_sha256']:
        raise ValueError('response lineage mismatch')
    response = unique_json(raw_path.read_text())
    records = unique_json(response['message']['content'])['faq']
    if len(records) != 5 or [r['qid'] for r in records] != [q['qid'] for q in questions]:
        raise ValueError('five unique ordered questions required')
    if any(r['answer_id'] not in bank for r in records):
        raise ValueError('unregistered answer ID')
    target = ROOT / ('answerbank-composed-' + method + '-v1')
    target.mkdir(exist_ok=False)
    files = []
    for lang, field in [('en', 'answer_en'), ('pt-BR', 'answer_pt')]:
        base_path = ROOT / protocol['base_chapter'] / (lang + '.md')
        registered = next(r for r in base_review['files'] if Path(r['path']).name == lang + '.md')
        raw = base_path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != registered['sha256']:
            raise ValueError('source-reviewed base changed')
        prefix, rest = raw.decode().split('## FAQ\n', 1)
        _, suffix = rest.split('## ', 1)
        faq = ['## FAQ\n']
        for question, record in zip(questions, records):
            qfield = 'question_en' if lang == 'en' else 'question_pt'
            selected = bank[record['answer_id']]
            answer = record[field] if method == 'answerbank-prose' else selected[field]
            if not isinstance(answer, str) or not answer.strip():
                raise ValueError('nonempty answer text required')
            evidence = selected['source']
            cite = f"{evidence['path']}:{evidence['lines'][0]}–{evidence['lines'][1]}"
            faq.append(f"### {question['qid']} — {question[qfield]}\n\n{answer}\n\n[{record['answer_id']}: `{cite}`]\n")
        content = prefix + '\n'.join(faq) + '\n## ' + suffix
        file = target / (lang + '.md')
        file.write_text(content)
        files.append({'path': str(file), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest(),
                      'base_prefix_sha256': hashlib.sha256(prefix.encode()).hexdigest(),
                      'base_suffix_sha256': hashlib.sha256(suffix.encode()).hexdigest()})
    result = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'method': method,
              'status': 'STRUCTURALLY_COMPOSED_PENDING_INDEPENDENT_REVIEW',
              'raw_response_sha256': outcome['raw_response_sha256'], 'files': files,
              'model_contribution': 'Five answer IDs and free answer prose' if method == 'answerbank-prose'
                                    else 'Five answer IDs only; all wording from reviewed bank',
              'not_complete_neural_authorship': True, 'owner_approved': False,
              'training_gold': False, 'source_executed': False, 'publication_authorized': False}
    receipt = ROOT / ('answerbank-composition-' + method + '-v1.json')
    if receipt.exists():
        raise FileExistsError(receipt)
    receipt.write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    for condition in ['answerbank-prose', 'answerbank-select']:
        try:
            result = compose(condition)
            print(json.dumps({'method': condition, 'status': result['status']}))
        except (ValueError, KeyError, FileNotFoundError) as error:
            receipt = ROOT / ('answerbank-composition-failure-' + condition + '-v1.json')
            if receipt.exists():
                raise FileExistsError(receipt)
            receipt.write_text(json.dumps({'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                          'method': condition, 'status': 'NOT_COMPOSED_REJECTED',
                                          'reason': str(error), 'no_retry': True,
                                          'owner_approved': False, 'training_gold': False}, indent=2) + '\n')
            print(json.dumps({'method': condition, 'status': 'NOT_COMPOSED_REJECTED', 'reason': str(error)}))
