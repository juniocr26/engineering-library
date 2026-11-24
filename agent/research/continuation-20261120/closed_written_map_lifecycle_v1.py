"""Isolated role/polarity admission for written literal return pairs; no runtime claims."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re

P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('written_map_prior', P / 'closed_helper_lifecycle_v3.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
retrieval = prior.observer.retrieval
OWN_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
DEPENDENCIES = {**prior.DEPENDENCIES, str(Path(prior.__file__)): prior.OWN_SHA}
TOKEN = r'[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*'


def lexical_name(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        if len(parts) > 32:
            raise ValueError('attribute depth outside bounded profile')
        node = node.value
    if not isinstance(node, ast.Name):
        raise ValueError('literal pair contains an expression outside Name/Attribute profile')
    parts.append(node.id)
    text = '.'.join(reversed(parts))
    if len(text) > 256 or not re.fullmatch(TOKEN, text):
        raise ValueError('pair identifier outside bounded ASCII spelling profile')
    return text


def parse(text, language, selector):
    if type(text) is not str or len(text.encode()) > 4096:
        raise ValueError('bounded paired prose required')
    verb = r'(writes|does not write) the literal return pair' if language == 'en' else r'(escreve|não escreve) o par literal de retorno'
    match = re.fullmatch(re.escape(selector) + ' ' + verb + r' `(' + TOKEN + r'): (' + TOKEN + r')`\.', text)
    if match is None:
        return None
    pair = [match[2], match[3]]
    if any(len(name) > 256 or name.count('.') > 32 for name in pair):
        raise ValueError('claim spelling exceeds source profile')
    return {'kind': 'written-literal-return-pair', 'pair': pair, 'present': match[1] in ['writes', 'escreve']}


def observe(source, selector):
    if type(source) is not str or len(source.encode()) > 65536:
        raise ValueError('bounded complete inline source required')
    # Reuse actual current complete-callable extraction; never execute source.
    unit = retrieval.python_unit(source, selector)
    tree = ast.parse(source, type_comments=True)
    functions = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == selector]
    if len(functions) != 1 or type(functions[0]) is not ast.FunctionDef or functions[0].decorator_list:
        raise ValueError('one undecorated synchronous top-level function required')
    function = functions[0]
    body = list(function.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and type(body[0].value.value) is str:
        body = body[1:]
    imports = 0
    while body and type(body[0]) in [ast.Import, ast.ImportFrom]:
        imports += 1
        body = body[1:]
    if imports > 4 or len(body) != 1 or not isinstance(body[0], ast.Return) or not isinstance(body[0].value, ast.Dict):
        raise ValueError('only bounded imports followed by a single complete literal return admitted')
    mapping = body[0].value
    if len(mapping.keys) > 32 or any(key is None for key in mapping.keys):
        raise ValueError('oversized or unpacked dictionary outside profile')
    pairs = [[lexical_name(key), lexical_name(value)] for key, value in zip(mapping.keys, mapping.values)]
    if len({pair[0] for pair in pairs}) != len(pairs):
        raise ValueError('duplicate lexical keys outside written-pair profile')
    return {'pairs': pairs, 'complete_callable': unit, 'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
            'syntax_only': True, 'runtime_identity_or_reachability_verified': False}


def decision(packet):
    result = {'version': '0.0.1-research', 'action': 'INCONCLUSIVE', 'scope': 'CLOSED_WRITTEN_LITERAL_PAIR_WITH_EXPLICIT_ROLE_AND_POLARITY',
              'source_executed': False, 'runtime_bindings_verified': False, 'physical_source_paths_authenticated': False,
              'physical_documentation_certified': False, 'owner_approved': False, 'training_gold': False,
              'publication_authorized': False, 'automatic_candidate_applier_supported': False,
              'writes': 0, 'model_calls': 0, 'producer_sha256': OWN_SHA, 'dependencies_sha256': DEPENDENCIES}
    try:
        if hashlib.sha256(Path(__file__).read_bytes()).hexdigest() != OWN_SHA or any(hashlib.sha256(Path(name).read_bytes()).hexdigest() != digest for name, digest in DEPENDENCIES.items()):
            raise ValueError('loaded source dependency changed; reload required')
        if type(packet) is not dict or set(packet) != prior.declaration.TOP:
            raise ValueError('original eleven-field packet required')
        packet = copy.deepcopy(packet)
        if packet['language'] != 'python' or packet['complete_scope'] is not True or packet['source_available'] is not True:
            raise ValueError('available complete Python source required')
        if packet['metadata'] != {} or packet['positive_retirement_evidence'] is not None:
            raise ValueError('metadata or retirement extension not admitted')
        for key in ['id', 'family', 'logical_contract_id']:
            if type(packet[key]) is not str or not 1 <= len(packet[key].encode()) <= 256:
                raise ValueError('bounded packet identity required')
        if not re.fullmatch(prior.NAME + r'(?:\.' + prior.NAME + r')*', packet['logical_contract_id']):
            raise ValueError('bounded selector identity required')
        selector = packet['logical_contract_id'].rsplit('.', 1)[-1]
        docs = packet['documentation']
        if type(docs) is not dict or set(docs) != {'en', 'pt-br'}:
            raise ValueError('exact bilingual documentation fields required')
        claims = {language: parse(text, language, selector) for language, text in docs.items()}
        if all(claim is None for claim in claims.values()):
            return {**prior.decision(packet), 'written_map_fallback': True, 'written_map_producer_sha256': OWN_SHA}
        if claims['en'] is None or claims['en'] != claims['pt-br']:
            raise ValueError('bilingual pair role, spelling or polarity mismatch')
        claim = claims['en']
        observations = {when: observe(packet[key], selector) for when, key in [('previous', 'previous_source'), ('current', 'current_source')]}
        truth = {when: (claim['pair'] in value['pairs']) == claim['present'] for when, value in observations.items()}
        result.update(action='NO-OP' if truth['current'] else 'MODIFY', selector=selector, parsed_claim=claim,
                      evidence=observations, claim_truth=truth,
                      change_basis='CURRENT_WRITTEN_CLAIM_TRUE' if truth['current'] else ('SOURCE_EVOLUTION' if truth['previous'] else 'PREEXISTING_DOCUMENTATION_ERROR'),
                      original_packet_sha256=prior.digest(packet),
                      reason='Exact lexical pair and explicit polarity checked in the sole admitted literal return; no runtime object or invocation guarantee.')
    except (ValueError, TypeError, KeyError, AttributeError, SyntaxError, UnicodeError, RecursionError, retrieval.Refused) as error:
        result.update(action='INCONCLUSIVE', reason=str(error)[:1024])
    return result
