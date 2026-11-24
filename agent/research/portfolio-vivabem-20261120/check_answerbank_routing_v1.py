"""Frozen question/answer routing checks, not arbitrary prose/source verification."""
import copy
import datetime
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def check(payload, method, protocol, oracle):
    if not isinstance(payload, dict) or set(payload) != {'faq'}:
        return {'routing_admitted': False, 'reason': 'top-level shape'}
    rows = payload['faq']
    questions = [q['qid'] for q in protocol['shared_questions']]
    if not isinstance(rows, list) or len(rows) != len(questions):
        return {'routing_admitted': False, 'reason': 'record count'}
    expected_keys = {'qid', 'answer_id'}
    if method == 'answerbank-prose':
        expected_keys |= {'answer_en', 'answer_pt'}
    if any(not isinstance(r, dict) or set(r) != expected_keys for r in rows):
        return {'routing_admitted': False, 'reason': 'record shape'}
    if [r['qid'] for r in rows] != questions:
        return {'routing_admitted': False, 'reason': 'question coverage/order'}
    bank = {r['answer_id']: r for r in protocol['shared_bank']}
    records = []
    for row in rows:
        qid = row['qid']
        expected = oracle['question_to_answer'][qid]
        identifier_valid = isinstance(row['answer_id'], str) and row['answer_id'] in bank
        mapped = identifier_valid and row['answer_id'] == expected
        prose_present = method != 'answerbank-prose' or all(isinstance(row[k], str) and row[k].strip()
                                                          for k in ['answer_en', 'answer_pt'])
        exact = None
        if method == 'answerbank-prose' and identifier_valid and prose_present:
            exact = all(row[k] == bank[row['answer_id']][k] for k in ['answer_en', 'answer_pt'])
        records.append({'qid': qid, 'expected_answer': expected, 'actual_answer': row['answer_id'],
                        'mapping_correct': mapped, 'required_prose_present': bool(prose_present),
                        'exact_registered_bilingual_wording': exact})
    return {'routing_admitted': all(r['mapping_correct'] and r['required_prose_present'] for r in records),
            'records': records, 'semantic_review_still_required': True,
            'scope': 'Pre-reviewed fixed answer mappings only. No arbitrary semantic classifier or owner approval.'}


def main():
    protocol = json.loads((ROOT / 'answerbank-comparison-protocol-v1.json').read_text())
    oracle = json.loads((ROOT / 'answerbank-comparison-oracle-v1.json').read_text())
    reference = {'faq': [{'qid': q['qid'], 'answer_id': oracle['question_to_answer'][q['qid']]}
                         for q in protocol['shared_questions']]}
    cases = [('positive-mapping', reference, True)]
    for name, qid, wrong in [('wrong-true-fact-legacy', 'Q003', 'A04'),
                             ('wrong-true-fact-duplicate', 'Q004', 'A07')]:
        candidate = copy.deepcopy(reference)
        next(r for r in candidate['faq'] if r['qid'] == qid)['answer_id'] = wrong
        cases.append((name, candidate, False))
    duplicate = copy.deepcopy(reference)
    duplicate['faq'][1]['qid'] = duplicate['faq'][0]['qid']
    cases.append(('duplicate-question', duplicate, False))
    missing = copy.deepcopy(reference)
    missing['faq'].pop()
    cases.append(('missing-question', missing, False))
    wrong = copy.deepcopy(reference)
    wrong['faq'][0]['answer_id'] = 'UNKNOWN'
    cases.append(('unknown-answer', wrong, False))
    raw = [{'id': n, 'payload': v, 'expected': e} for n, v, e in cases]
    input_file = ROOT / 'answerbank-routing-challenge-input-v1.json'
    if input_file.exists():
        raise FileExistsError(input_file)
    input_file.write_text(json.dumps({'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                     'cases': raw}, indent=2) + '\n')
    results = []
    for name, payload, expected in cases:
        result = check(payload, 'answerbank-select', protocol, oracle)
        results.append({'id': name, 'expected': expected,
                        'actual': result['routing_admitted'],
                        'matched': expected == result['routing_admitted'], 'result': result})
    output = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'results': results,
              'all_matched': all(r['matched'] for r in results),
              'scope': 'Six development schema/mapping controls, not six independent semantic cases. Wrong true facts carry valid source citations but do not answer the named method question.',
              'source_executed': False, 'model_calls': 0, 'owner_approved': False, 'training_gold': False}
    target = ROOT / 'answerbank-routing-challenge-results-v1.json'
    if target.exists():
        raise FileExistsError(target)
    target.write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({'controls': len(results), 'all_matched': output['all_matched']}))


if __name__ == '__main__':
    main()
