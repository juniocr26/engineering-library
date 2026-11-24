"""Closed bilingual keyword-prefix routing, preserving the original packet schema."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re

P = Path(__file__).resolve().parent

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, P / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

prefix = load('keyword_router_prefix', 'keyword_prefix_observer_v1.py')
declaration = load('keyword_router_declaration', 'closed_declaration_lifecycle_v2.py')
OWN_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
PREFIX_SHA = hashlib.sha256(Path(prefix.__file__).read_bytes()).hexdigest()
DECLARATION_SHA = hashlib.sha256(Path(declaration.__file__).read_bytes()).hexdigest()
NAME = r'[A-Za-z_][A-Za-z0-9_]{0,127}'


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()


def parse(text, language, selector):
    if type(text) is not str or len(text.encode()) > 4096:
        raise ValueError('bounded paired documentation strings required')
    rejecting = re.escape(selector) + (r' rejects the (' + NAME + r') keyword as unexpected\.' if language == 'en' else r' rejeita a opção (' + NAME + r') como inesperada\.')
    direct = re.escape(selector) + (r' contains a direct (' + NAME + r') pop before the unexpected-keyword guard\.' if language == 'en' else r' contém extração direta de (' + NAME + r') antes da verificação de opções inesperadas\.')
    for pattern, kind in [(rejecting, 'rejects-as-unexpected'), (direct, 'contains-direct-pop')]:
        match = re.fullmatch(pattern, text)
        if match:
            if not declaration.engine.valid_name(match[1]):
                raise ValueError('keyword outside admitted identifier profile')
            return {'kind': kind, 'keyword': match[1]}
    return None


def decision(packet):
    result = {'version': '0.0.1-research', 'action': 'INCONCLUSIVE', 'source_executed': False,
              'runtime_bindings_verified': False, 'physical_source_paths_authenticated': False,
              'physical_documentation_certified': False, 'owner_approved': False,
              'training_gold': False, 'publication_authorized': False, 'model_calls': 0, 'writes': 0,
              'automatic_candidate_applier_supported': False, 'producer_sha256': OWN_SHA,
              'dependencies_sha256': {'keyword_prefix': PREFIX_SHA, 'closed_declaration': DECLARATION_SHA},
              'scope': 'CLOSED_BILINGUAL_WRITTEN_PREFIX_OR_DECLARATION_CLAIMS_NOT_GENERAL_PROSE'}
    try:
        if any(hashlib.sha256(path.read_bytes()).hexdigest() != expected for path, expected in [(Path(__file__), OWN_SHA), (Path(prefix.__file__), PREFIX_SHA), (Path(declaration.__file__), DECLARATION_SHA)]):
            raise ValueError('loaded keyword router producer changed; reload required')
        if type(packet) is not dict:
            raise ValueError('closed source packet required')
        packet = copy.deepcopy(packet)
        if set(packet) != declaration.TOP or packet['language'] != 'python' or packet['complete_scope'] is not True or packet['source_available'] is not True:
            raise ValueError('original complete available Python packet required')
        if packet['metadata'] != {} or packet['positive_retirement_evidence'] is not None:
            raise ValueError('metadata/retirement extensions outside research profile')
        if any(type(packet[k]) is not str or not packet[k] or len(packet[k].encode()) > 256 for k in ['id', 'family', 'logical_contract_id']):
            raise ValueError('bounded packet identities required')
        logical = packet['logical_contract_id']
        if not re.fullmatch(NAME + r'(?:\.' + NAME + r')*', logical):
            raise ValueError('logical selector outside closed profile')
        selector = logical.rsplit('.', 1)[-1]
        docs = packet['documentation']
        if type(docs) is not dict or set(docs) != {'en', 'pt-br'}:
            raise ValueError('paired documentation required')
        mapped = {language: parse(text, language, selector) for language, text in docs.items()}
        request_hash = hashlib.sha256(canonical(packet)).hexdigest()
        if all(v is None for v in mapped.values()):
            observed = declaration.decision(copy.deepcopy(packet))
            if observed.get('source_executed') is not False:
                result['source_executed'] = None
                raise ValueError('delegate execution report changed; overall execution status is uncertain')
            if observed.get('producer_sha256') != DECLARATION_SHA or observed.get('action') not in ['ADD', 'MODIFY', 'NO-OP', 'INCONCLUSIVE']:
                raise ValueError('declaration delegate provenance or action changed')
            for flag in ['owner_approved', 'training_gold', 'publication_authorized', 'automatic_candidate_applier_supported']:
                if observed.get(flag) is not False:
                    raise ValueError('declaration delegate authority changed')
            for count in ['writes', 'model_calls']:
                if type(observed.get(count)) is not int or observed[count] != 0:
                    raise ValueError('declaration delegate zero-operation contract changed')
            if observed['action'] != 'INCONCLUSIVE' and observed.get('original_packet_sha256') != request_hash:
                raise ValueError('declaration delegate addresses a different packet')
            result.update(action=observed['action'], reason=observed['reason'], declaration_observation=observed,
                          original_packet_sha256=request_hash, route='existing-closed-declaration-profile')
            return result
        if mapped['en'] is None or mapped['en'] != mapped['pt-br']:
            raise ValueError('bilingual closed keyword claims disagree or only one is recognized')
        cards = {}
        for when, key in [('previous', 'previous_source'), ('current', 'current_source')]:
            text = packet[key]
            if type(text) is not str or len(text.encode()) > 65536:
                raise ValueError('bounded full inline module required')
            digest = hashlib.sha256(text.encode()).hexdigest()
            cards[when] = {'path': 'inline-packet-module.py', 'revision': 'source-sha256:' + digest, 'source': text, 'sha256': digest}
        facts = {when: prefix.observe(card, selector, mapped['en']['keyword']) for when, card in cards.items()}
        if any(f['status'] != 'WRITTEN_KEYWORD_PREFIX_FACTS' or f.get('source_executed') is not False or f.get('producer_sha256') != PREFIX_SHA for f in facts.values()):
            result['keyword_evidence'] = facts
            raise ValueError('paired bounded keyword prefix facts not established')
        recognized = facts['current']['keyword_recognized_by_direct_pop']
        matches = not recognized if mapped['en']['kind'] == 'rejects-as-unexpected' else recognized
        result.update(action='NO-OP' if matches else 'MODIFY', selector=selector, parsed_claim=mapped['en'],
                      keyword_evidence=facts, original_packet_sha256=request_hash, route='complete-statement-keyword-prefix-profile',
                      reason='Compare written direct pop and exact remaining-kwargs guard only; accepted values, later traversal and runtime bindings remain unverified.')
        return result
    except (ValueError, TypeError, KeyError, UnicodeError, RecursionError) as error:
        result.update(action='INCONCLUSIVE', reason=str(error)[:1024])
        return result
