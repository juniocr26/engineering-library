"""Persist same-agent manual judgments over original, losslessly read E outputs."""
import collections
import datetime
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
references = {row['claim_id']: row for row in json.loads((HERE / 'atomic-reference-ledger-v2.json').read_text())['claims']}


class ObjectPairs(list):
    pass


def collect(node, path='$', output=None, duplicates=None):
    output = [] if output is None else output
    duplicates = [] if duplicates is None else duplicates
    if isinstance(node, ObjectPairs):
        keys = collections.Counter(key for key, value in node)
        for key, count in keys.items():
            if count > 1:
                duplicates.append({'object_path': path, 'key': key, 'occurrences': count})
        ids = [value for key, value in node if key == 'id']
        answers = [value for key, value in node if key == 'answer_en']
        if len(ids) == 1 and len(answers) == 1:
            output.append({'path': path, 'fields': dict(node)})
        for index, (key, value) in enumerate(node):
            collect(value, path + '/' + key + '@' + str(index), output, duplicates)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            collect(value, path + '/' + str(index), output, duplicates)
    return output, duplicates


# These judgments were made by reading the actual source, questions, answers,
# and both languages. They are not an automatic semantic classifier.
judgments = {
    'fastapi': [
        ('F01', 'SUPPORTED', 'EN True matches the declaration. PT Verdade does not preserve the written code literal unambiguously.'),
        ('F02', 'SUPPORTED', 'EN None is correct. PT Nenhum is ambiguous between a None default and no default.'),
        ('F03', 'SUPPORTED', 'Empty-dictionary initialization is correct under the question condition; cited models.py is the wrong source file.'),
        ('F04', 'SUPPORTED_WEAKER', 'Named cache argument is correct in question context; the citation names models.py instead of solver utils.py.'),
        ('F05', 'SUPPORTED', 'Conjunction is correct. PT e/em are prose connectives, not a proposed executable Python expression. Source file is wrong.'),
        ('F06', 'CONTRADICTED', 'Generates solved=cache[key] for the absent-key write; actual write is cache[key]=solved. Both languages reverse assignment direction.'),
        ('F07', 'SUPPORTED_OTHER_QUESTION', 'Generated question asks whether the branch assigns use_cache, rather than whether its guard tests use_cache. No answers a different predicate; required reference remains uncovered.'),
        ('F08', 'SUPPORTED', 'Exact written request_astack assertion and correct utils.py file; no enabled-at-runtime guarantee inferred.'),
        ('F09', 'SUPPORTED', 'Exact written function_astack assertion and correct utils.py file; no complete-error-handling guarantee inferred.'),
    ],
    'cobra': [
        ('C01', 'CONTRADICTED', 'Invents a function PositionalArgs taking a callback. Source declares a defined function type, not that API function.'),
        ('C02', 'CONTRADICTED', 'Subcommand/argument condition is not len(cmd.ValidArgs)>0; source line35 belongs to legacyArgs.'),
        ('C03', 'SUPPORTED_WEAKER', 'Tab separator is correct, but before-first-tab projection is omitted.'),
        ('C04', 'SUPPORTED', 'Factory returns a function, and that callback checks argument count. Split these propositions for atomic counting.'),
        ('C05', 'SUPPORTED', 'EN len<n or len>n is integer-equivalent to len!=n. PT retorno do callback is ambiguous about returned callback versus callback return value.'),
        ('C06', 'SUPPORTED', 'Supplied-validator order is correct in both languages.'),
        ('C07', 'SUPPORTED', 'Return at first non-nil error is correct. Ordinary PT não nulo is not treated as a renamed source identifier.'),
        ('C08', 'SUPPORTED', 'Exact delegation expression is preserved.'),
        ('C09', 'MIXED_SPLIT_INTO_ATOMS', 'Deprecation status is correct, but the added replacement recommendation is reversed.'),
    ],
    'zod': [
        ('Z01', 'SUPPORTED', 'EN false flag is correct; PT question is malformed/mixed-language and is not certified as a complete equivalent question.'),
        ('Z02', 'INSUFFICIENT', 'Value/issues parameters does not preserve payload-object plus ctx argument roles. Ambiguous API shape, not an invented concrete positional call.'),
        ('Z03', 'SUPPORTED', 'Correct error class under selected synchronous Promise-guard question; no all-realms Promise guarantee inferred.'),
        ('Z04', 'SUPPORTED', 'Normal failure condition result.issues.length is correct.'),
        ('Z05', 'SUPPORTED', 'success:true literal is correct.'),
        ('Z06', 'CONTRADICTED', 'Actual guard is !closure-local error, not an undefined-only property check.'),
        ('Z07', 'INSUFFICIENT', 'Incoming setter e->local error becomes property error->local error; source dataflow role is wrong or ambiguous.'),
        ('Z08', 'SUPPORTED', 'Await under Promise guard is preserved, without unconditional fulfillment; PT wording needs review.'),
        ('Z09', 'SUPPORTED', 'Correct ZodRealError factory class.'),
        ('Z10', 'SUPPORTED', 'Correct data:result.value property.'),
    ],
}
metrics = {
    'fastapi': {'supported': 8, 'contradicted': 1, 'insufficient': 0, 'denominator': 9,
                'scope': 'Identifiable EN code propositions; F07 is true for a changed question, not required-reference coverage; PT literal/question issues separate.'},
    'cobra': {'supported': 8, 'contradicted': 3, 'insufficient': 0, 'denominator': 11,
              'scope': 'C04 factory/callback split and C09 status/recommendation split; PT C05 ambiguity is separate from EN precision.'},
    'zod': {'supported': 7, 'contradicted': 1, 'insufficient': 2, 'denominator': 10,
            'scope': 'Identifiable EN source propositions; malformed PT questions and missing source locations assessed separately.'},
}
reasons = {
    'fastapi': ['Critical reverse cache assignment F06', 'F07 question changed', 'Repeated questions keys and misnamed PT question key',
                'PT True/None literal ambiguity', 'Wrong models.py citations for solver behavior', 'Uncertainty answer EN-only outside required FAQ list'],
    'cobra': ['Invented API function signature C01', 'Wrong function guard C02', 'Reversed deprecation recommendation C09',
              'Uncertainty question lacks answer', 'PT callback-level ambiguity C05'],
    'zod': ['Wrong getter predicate Z06', 'Ambiguous setter/runner dataflow roles', 'Repeated faq key11times discards all but last entry under ordinary decoding',
            'Only revision, without source path/lines', 'Several PT questions malformed or mixed-language'],
}
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
for task, decisions in judgments.items():
    folder = HERE / 'generation-v1' / task / 'E'
    content_path = folder / 'model-content.txt'
    rows, duplicates = collect(json.loads(content_path.read_text(), object_pairs_hook=ObjectPairs))
    decision_map = {cid: (verdict, reason) for cid, verdict, reason in decisions}
    records = []
    for row in rows:
        item = row['fields']
        if item['id'].startswith('U-'):
            continue  # uncertainty control is reviewed separately below
        reference = references[item['id']]
        verdict, reason = decision_map[item['id']]
        records.append({'claim_id': 'NEW-E-' + task + '-' + item['id'], 'reference_id': item['id'],
                        'original_generated_record': item, 'original_json_object_path': row['path'],
                        'source_revision': reference['source_revision'], 'source_path': reference['source_path'],
                        'source_file_sha256': reference['source_file_sha256'], 'source_lines': reference['source_lines'],
                        'exact_source_evidence': reference['exact_source_evidence'],
                        'expected_interpretation': reference['expected_interpretation'],
                        'factual_verdict_en': verdict, 'bilingual_or_relevance_reason': reason,
                        'reviewer': 'Same Codex campaign agent, source and raw EN/PT read without repair',
                        'critical_if_unsupported': True})
    if task == 'cobra':
        records.append({'claim_id': 'NEW-E-cobra-C09-RECOMMENDATION', 'parent_id': 'C09',
                        'generated_interpretation': 'ExactValidArgs is deprecated and should be used instead of MatchAll(ExactArgs(n), OnlyValidArgs).',
                        'source_revision': references['C09']['source_revision'], 'source_path': 'args.go',
                        'source_lines': [141, 143],
                        'exact_source_evidence': '// Deprecated: use MatchAll(ExactArgs(n), OnlyValidArgs) instead\nfunc ExactValidArgs(n int) PositionalArgs {\n\treturn MatchAll(ExactArgs(n), OnlyValidArgs)',
                        'verdict': 'CONTRADICTED', 'critical': True,
                        'note': 'The correct deprecation-status clause does not certify its reversed recommendation.'})
    review = {'at': now, 'task': task, 'method': 'E',
              'content_sha256': hashlib.sha256(content_path.read_bytes()).hexdigest(),
              'raw_response_sha256': hashlib.sha256((folder / 'raw-response.json').read_bytes()).hexdigest(),
              'lossless_factual_records': records, 'duplicate_keys': duplicates,
              'selected_english_atomic_metrics': metrics[task], 'full_bilingual_atomic_precision': None,
              'strict_individual_faq_pair_acceptance': None, 'whole_requested_faq_output': 'REJECTED',
              'reasons': reasons[task],
              'uncertainty_control': {'fastapi': 'EN No only, no PT packet', 'cobra': 'Question only, no answer; not abstention',
                                      'zod': 'Explicit No/Não declines universal fulfillment; coarse justified abstention only'}[task],
              'preflight_note': 'An earlier unexecuted heredoc had a brace SyntaxError; no annotation files or predictions changed before this script.',
              'annotation_preflight_v2': 'v1 stopped on U-Z lookup after writing FastAPI and Cobra; v2 excludes the separately assessed uncertainty control and preserves those files.', 'original_outputs_and_reference_answers_unchanged': True, 'not_general_model_accuracy': True,
              'owner_approved': False, 'training_gold': False, 'optimizer_updates': 0}
    if (folder / 'semantic-review-v1.json').exists():
        prior = json.loads((folder / 'semantic-review-v1.json').read_text())
        assert prior['content_sha256'] == review['content_sha256']
        assert prior['lossless_factual_records'] == review['lossless_factual_records']
        continue  # retain successful partial v1 annotations byte-for-byte
    with (folder / 'semantic-review-v1.json').open('x') as stream:
        json.dump(review, stream, indent=2, ensure_ascii=False)
        stream.write('\n')

outcomes = [json.loads((HERE / 'generation-v1' / task / 'E/outcome.json').read_text()) for task in judgments]
summary = {'at': now, 'method': 'E', 'requested_granularity': 'Complete bilingual FAQ, not whole chapter',
           'attempts': 3, 'transport_success': 3, 'normal_stops': 3, 'json_syntax_valid': 3,
           'complete_requested_faq_acceptance': {'numerator': 0, 'denominator': 3},
           'reported_generated_tokens': sum(row['eval_count'] for row in outcomes),
           'reported_server_seconds': sum(row['total_duration'] / 1e9 for row in outcomes),
           'wall_seconds_sum': sum(row['wall_seconds'] for row in outcomes),
           'key_confirmed_mechanisms': ['Defined function type changed into API function signature',
                                      'Guard assigned to wrong function', 'Deprecation recommendation reversed',
                                      'Read/write assignment direction reversed', 'Question changed while answer remains No',
                                      'Truthiness rewritten as undefined-only', 'Duplicate JSON keys lose interchange data'],
           'no_manual_repair_or_rerun': True, 'no_historical_pooling': True,
           'owner_gold': 0, 'optimizer_updates': 0}
with (HERE / 'generation-E-results-v1.json').open('x') as stream:
    json.dump(summary, stream, indent=2)
    stream.write('\n')
print(json.dumps(summary, indent=2), flush=True)
