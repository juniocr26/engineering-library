"""Isolated preview for explicitly registered generated class-integer statements.

No file writes, owner prose adoption, public catalog application or arbitrary
language interpretation. Physical reads and immutable registries belong to the
research consumer. This is not wired into the production candidate applier.
"""
import copy
import hashlib
import importlib.util
from pathlib import Path
import re
import sys

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
sys.path.insert(0, str(ROOT / 'agent/tools'))
from documentation_candidates import blocks
from documentation_retrieval import relative_path

spec = importlib.util.spec_from_file_location('preview_class_observer', P / 'class_member_observer_v3.py')
observer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(observer)
OWN_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
OBSERVER_SHA = hashlib.sha256(Path(observer.__file__).read_bytes()).hexdigest()
PREFIX = {'en': 'Written class assignment: ', 'pt-br': 'Atribuição escrita da classe: '}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def rendered(language, selector, value):
    if type(value) is not int or not -(10**12) < value < 10**12:
        raise ValueError('bounded integer, never Boolean, required')
    return (PREFIX[language] + '`' + selector + ' = ' + str(value) + '`.\n').encode()


def preview(specification):
    result = {'status': 'INCONCLUSIVE', 'scope': 'REGISTERED_GENERATED_INTEGER_STATEMENT_RESEARCH_PREVIEW',
              'writes': 0, 'publication_authorized': False, 'owner_approved': False,
              'training_gold': False, 'automatic_production_applier_supported': False,
              'runtime_semantics_verified': False}
    try:
        if sha(Path(__file__).read_bytes()) != OWN_SHA or sha(Path(observer.__file__).read_bytes()) != OBSERVER_SHA:
            raise ValueError('loaded preview implementation changed; reload required')
        if type(specification) is not dict:
            raise ValueError('explicit preview specification required')
        specification = copy.deepcopy(specification)
        if set(specification) != {'scope', 'registered_source_path', 'previous', 'current', 'documents', 'operations'} or specification['scope'] != 'owned-research-generated-documents':
            raise ValueError('unsupported preview authority/scope')
        registered = specification['registered_source_path']
        relative_path(registered)
        for key in ['previous', 'current']:
            if specification[key].get('path') != registered:
                raise ValueError('source path substituted outside registered operation')
        documents = specification['documents']
        if type(documents) is not dict or set(documents) != {'en', 'pt-br'}:
            raise ValueError('paired physical documentation required')
        parsed = {}
        for lang, doc in documents.items():
            if type(doc) is not dict or set(doc) != {'path', 'bytes', 'expected_sha256', 'registered_generated_claims'}:
                raise ValueError('closed physical document card required')
            relative_path(doc['path'])
            if not doc['path'].startswith(lang + '/') or not doc['path'].endswith('.md'):
                raise ValueError('wrong language or document path')
            raw = doc['bytes']
            if type(raw) is not bytes or len(raw) > 2*1024*1024 or b'\0' in raw or sha(raw) != doc['expected_sha256']:
                raise ValueError('physical document bytes/hash refused')
            raw.decode('utf-8')
            if type(doc['registered_generated_claims']) is not list or not all(type(x) is str for x in doc['registered_generated_claims']):
                raise ValueError('explicit generated ownership registry required')
            parsed[lang] = blocks(raw)
        operations = specification['operations']
        if type(operations) is not list or not 1 <= len(operations) <= 8:
            raise ValueError('bounded nonempty operation list required')
        changes = {'en': [], 'pt-br': []}
        decisions = []
        seen_ids, seen_selectors = set(), set()
        quote_bytes = 0
        for operation in operations:
            if type(operation) is not dict or set(operation) != {'claim_id', 'selector', 'expected_blocks'}:
                raise ValueError('closed operation required')
            claim = operation['claim_id'];selector = operation['selector']
            if type(claim) is not str or not re.fullmatch(r'[a-z][a-z0-9_.-]{0,95}', claim):
                raise ValueError('invalid claim identity')
            if claim in seen_ids or selector in seen_selectors:
                raise ValueError('duplicate claim or selector')
            seen_ids.add(claim);seen_selectors.add(selector)
            if type(operation['expected_blocks']) is not dict or set(operation['expected_blocks']) != {'en', 'pt-br'}:
                raise ValueError('paired block hashes required')
            observed = {key: observer.observe(specification[key], selector) for key in ['previous', 'current']}
            values = {}
            for key, facts in observed.items():
                value = facts.get('written_value', {})
                if facts['status'] != 'WRITTEN_CLASS_MEMBER' or value.get('kind') != 'literal' or value.get('type') != 'int':
                    raise ValueError('positive bounded written integer required; absence never retires documentation')
                values[key] = value['value']
                rendered('en', selector, value['value'])
                quote_bytes += len(facts['evidence']['quote'].encode())
            if quote_bytes > 24576:
                raise ValueError('combined complete member quote budget exceeded')
            mapped_values = []
            for lang, doc in documents.items():
                if claim not in doc['registered_generated_claims'] or claim not in parsed[lang]:
                    raise ValueError('unregistered generated ownership; markers alone insufficient')
                first, last = parsed[lang][claim]
                body = doc['bytes'][first.end():last.start()]
                if sha(body) != operation['expected_blocks'][lang]:
                    raise ValueError('physical generated block hash mismatch')
                pattern = re.escape(PREFIX[lang] + '`' + selector + ' = ') + r'(-?(?:0|[1-9][0-9]{0,11}))`\.\n'
                match = re.fullmatch(pattern, body.decode())
                if not match:
                    raise ValueError('physical prose outside exact generated statement grammar')
                mapped_values.append(int(match[1]))
                changes[lang].append((first.end(), last.start(), rendered(lang, selector, values['current'])))
            if mapped_values[0] != mapped_values[1]:
                raise ValueError('bilingual physical claim values disagree')
            action = 'NO-OP' if mapped_values[0] == values['current'] else 'MODIFY'
            decisions.append({'claim_id': claim, 'selector': selector, 'action': action,
                              'source_values': values, 'document_value': mapped_values[0],
                              'document_already_wrong_before_change': mapped_values[0] != values['previous'],
                              'source_written_value_changed': values['previous'] != values['current'],
                              'source_evidence': observed})
        candidates = {}
        preservation = {}
        for lang, doc in documents.items():
            cursor = 0;parts = [];kept = []
            for first, last, replacement in sorted(changes[lang]):
                if first < cursor:
                    raise ValueError('overlapping generated spans')
                outside = doc['bytes'][cursor:first];parts.extend([outside, replacement]);kept.append(sha(outside));cursor=last
            parts.append(doc['bytes'][cursor:]);kept.append(sha(parts[-1]));candidate=b''.join(parts)
            # These exact original outside segments are used unchanged, not reconstructed.
            candidates[lang] = candidate
            preservation[lang] = {'original_sha256': sha(doc['bytes']), 'candidate_sha256': sha(candidate),
                                  'outside_segment_hashes': kept, 'untouched_outside_segments': True}
        result.update(status='PREVIEW_READY', decisions=decisions, candidates=candidates,
                      preservation=preservation, complete_member_quote_bytes=quote_bytes)
        return result
    except (ValueError, TypeError, KeyError, UnicodeError) as error:
        result.update(status='INCONCLUSIVE', reason=str(error)[:1024])
        return result
