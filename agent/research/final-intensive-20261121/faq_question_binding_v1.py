"""Literal identity diagnostics only; cannot authorize factual acceptance."""
import json


def decode(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key: '+key)
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs)


def diagnose(raw, registry, *, exact_pt=True):
    errors = []
    try:
        if len(raw.encode() if isinstance(raw, str) else raw) > 65536:
            raise ValueError('packet exceeds bounded profile')
        packet = decode(raw)
        if not isinstance(packet, dict) or set(packet) != {'faq'}:
            raise ValueError('exact faq envelope required')
        rows = packet['faq']
        if not isinstance(rows, list):
            raise ValueError('faq list required')
        seen = set()
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                raise ValueError('FAQ record must be object')
            if set(row) != {'id','question_en','question_pt','answer_en','answer_pt','fact_ids'}:
                errors.append(f'{index}:record-schema-differs')
            ident = row.get('id')
            if not isinstance(ident, str) or ident not in registry:
                errors.append(f'{index}:unknown-question-id')
                continue
            if ident in seen:
                errors.append(ident+':duplicate-id')
            seen.add(ident)
            expected = registry[ident]
            for language in ['en', 'pt'] if exact_pt else ['en']:
                if row.get('question_'+language) != expected['question_'+language]:
                    errors.append(ident+':question-'+language+'-differs')
            if row.get('fact_ids') != expected['required_fact_ids']:
                errors.append(ident+':fact-association-differs')
            for language in ['en', 'pt']:
                answer = row.get('answer_'+language)
                if not isinstance(answer, str) or not answer.strip():
                    errors.append(ident+':empty-answer-'+language)
                    continue
                for token in expected['required_answer_identifiers']:
                    if token not in answer:
                        errors.append(ident+':missing-'+language+'-identifier:'+token)
        for ident in set(registry)-seen:
            errors.append(ident+':missing-question')
    except (ValueError, TypeError, UnicodeError, RecursionError) as error:
        errors.append(str(error))
    return {'status':'LITERAL_BINDINGS_VALID' if not errors else 'BINDING_REFUSED',
            'errors':sorted(errors), 'semantic_review_required':True,
            'technical_acceptance':'NOT_EVALUATED', 'owner_approved':False,
            'publication_approved':False, 'training_eligible':False,
            'exact_PT_identity_checked':exact_pt,
            'scope':'Exact registered strings, IDs and identifier presence only; truthful answers and semantic translations are not verified.'}
