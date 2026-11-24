"""Closed bilingual declaration claims on unchanged inline packet schema.

Research-only: no arbitrary prose entailment, physical-catalog certification,
runtime binding, retirement or filesystem application.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re

P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('closed_decl_engine',P/'typed_module_lifecycle_v5.py')
engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
OWN_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
ENGINE_SHA=hashlib.sha256(Path(engine.__file__).read_bytes()).hexdigest()
TOP={'id','family','language','previous_source','current_source','documentation','complete_scope','source_available','positive_retirement_evidence','logical_contract_id','metadata'}
NAME=r'[A-Za-z_][A-Za-z0-9_]{0,127}'


def parse_claim(text,language,selector):
    if type(text)is not str or len(text.encode())>4096:
        raise ValueError('bounded string documentation required')
    if text=='':return {'kind':'undocumented-declaration'}
    symbol=re.escape(selector)
    absent=symbol+(r' has no ('+NAME+r') parameter\.'if language=='en'else r' não possui parâmetro ('+NAME+r')\.')
    match=re.fullmatch(absent,text)
    if match:
        if not engine.valid_name(match[1]):raise ValueError('parameter token is not an admitted identifier')
        return {'kind':'no-explicit-parameter','parameter':match[1]}
    present=symbol+(r' has (?:a|an) ('+NAME+r') parameter\.'if language=='en'else r' possui parâmetro ('+NAME+r')\.')
    match=re.fullmatch(present,text)
    if match:
        if not engine.valid_name(match[1]):raise ValueError('parameter token is not an admitted identifier')
        return {'kind':'has-explicit-parameter','parameter':match[1]}
    tuple_pattern=symbol+(r' returns the tuple (.+)\.'if language=='en'else r' retorna a tupla (.+)\.')
    match=re.fullmatch(tuple_pattern,text)
    if match:
        names=match[1].split(', ')
        if not 1<=len(names)<=8 or not all(engine.valid_name(name)for name in names):raise ValueError('tuple claim outside identifier-list grammar')
        return {'kind':'written-tuple-return','elements':names}
    raise ValueError('prose outside closed declaration grammar;runtime/helper/class semantics are not weakened')


def decision(packet):
    result={'version':'0.0.2-research','action':'INCONCLUSIVE','source_executed':False,'runtime_bindings_verified':False,
            'physical_source_paths_authenticated':False,'physical_documentation_certified':False,
            'owner_approved':False,'training_gold':False,'publication_authorized':False,'model_calls':0,'writes':0,
            'scope':'CLOSED_BILINGUAL_DECLARATION_CLAIMS_NOT_GENERAL_PROSE','automatic_candidate_applier_supported':False,
            'producer_sha256':OWN_SHA,'engine_sha256':ENGINE_SHA}
    try:
        if hashlib.sha256(Path(__file__).read_bytes()).hexdigest()!=OWN_SHA or hashlib.sha256(Path(engine.__file__).read_bytes()).hexdigest()!=ENGINE_SHA:
            raise ValueError('loaded closed-claim implementation changed;reload required')
        if type(packet)is not dict:raise ValueError('closed source packet object required')
        packet=copy.deepcopy(packet)
        if set(packet)!=TOP:raise ValueError('original closed packet fields required')
        if packet['language']!='python' or packet['complete_scope']is not True or packet['source_available']is not True:
            raise ValueError('explicit available complete Python module scope required')
        if packet['metadata']!={} or packet['positive_retirement_evidence']is not None:
            raise ValueError('metadata/retirement extensions outside this isolated research profile')
        for name in ['id','family','logical_contract_id']:
            if type(packet[name])is not str or not packet[name]or len(packet[name].encode())>256:raise ValueError('bounded packet identity required')
        for name in ['previous_source','current_source']:
            if type(packet[name])is not str or len(packet[name].encode())>65536:raise ValueError('bounded inline source bytes required')
        logical=packet['logical_contract_id']
        if not re.fullmatch(NAME+r'(?:\.'+NAME+r')*',logical):raise ValueError('logical declaration selector outside profile')
        selector=logical.rsplit('.',1)[-1]
        if not engine.valid_name(selector):raise ValueError('logical selector is not an admitted name')
        docs=packet['documentation']
        if type(docs)is not dict or set(docs)!={'en','pt-br'}:raise ValueError('paired documentation strings required')
        mapped={lang:parse_claim(text,lang,selector)for lang,text in docs.items()}
        if mapped['en']!=mapped['pt-br']:raise ValueError('bilingual closed claims disagree')
        cards={}
        for when,key in [('previous','previous_source'),('current','current_source')]:
            source=packet[key];digest=hashlib.sha256(source.encode()).hexdigest()
            # Logical observation label only. No physical file path is invented.
            cards[when]={'path':'inline-packet-module.py','revision':'source-sha256:'+digest,'source':source,'sha256':digest}
        observed=engine.recommend(cards['previous'],cards['current'],selector,mapped)
        result.update(action=observed['action'],reason=observed['reason'],selector=selector,
                      parsed_claim=mapped['en'],typed_observation=observed,
                      original_packet_sha256=hashlib.sha256(json.dumps(packet,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()).hexdigest())
        if result['action']=='REMOVE':raise ValueError('retirement never admitted by this profile')
        if result['action']=='ADD':result['add_scope']='Proposed isolated note for supplied empty logical slot only;physicalcatalog absence/ownership not proved.'
        return result
    except (ValueError,TypeError,KeyError,UnicodeError,RecursionError)as error:
        result.update(action='INCONCLUSIVE',reason=str(error)[:1024]);return result
