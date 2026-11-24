"""Freeze guard controls and explicit unverified-scope examples before a source fix."""
import copy
import datetime
import hashlib
import json
from pathlib import Path

P=Path(__file__).resolve().parent
protocol=json.loads((P/'returned-map-renderer-protocol-v2.json').read_text())
rows=copy.deepcopy(protocol['cases'])
for row in rows:
    row['kind']='ADVERSE_IDENTIFIER_TRANSLATION' if row['expected_status']=='REFUSED' else 'VALID_REFERENCE_PRESERVATION'
    row['semantic_fact_accepted']=row['expected_status']=='RENDERED'
    row['notes']='Real current HTTPX returned class-reference dictionary; no package source execution.'
owned=P/'returned-map-owned-sources-v1';owned.mkdir(exist_ok=False)


def add(identity,source,en_code,pt_code,expected,kind='ADVERSE_IDENTIFIER_TRANSLATION',semantic=False):
    root=owned/identity;root.mkdir();raw=source.encode();(root/'mapping.py').write_bytes(raw)
    rows.append({'id':identity,'source_root':'/sources/engineering-library/'+str(root),'file':'mapping.py','selector':'build_map','source_sha256':hashlib.sha256(raw).hexdigest(),'en':'The `build_map` source names '+en_code+' in its returned dictionary.','pt-br':'O código de `build_map` nomeia '+pt_code+' em seu dicionário retornado.','expected_status':expected,'kind':kind,'semantic_fact_accepted':semantic,'notes':'Owned nonexecuted source; a RENDERED scope-limit row is not an accepted factual documentation target.'})

bare='def build_map():\n    return {AlphaError: BetaError}\n'
ambiguous='def build_map():\n    return {first.Error: target.Error, second.Error: other.Error}\n'
add('bare-target-translated',bare,'`AlphaError` and `BetaError`','`AlphaError` e `ErroBeta`','REFUSED')
add('bare-source-translated',bare,'`AlphaError` and `BetaError`','`ErroAlfa` e `BetaError`','REFUSED')
add('bare-reference-pair-preserved',bare,'`AlphaError` and `BetaError`','`AlphaError` e `BetaError`','RENDERED','VALID_REFERENCE_PRESERVATION',True)
add('qualified-reference-pair-preserved',ambiguous,'`first.Error: target.Error`','`first.Error: target.Error`','RENDERED','VALID_REFERENCE_PRESERVATION',True)
add('qualified-owner-exchanged',ambiguous,'`first.Error: target.Error`','`second.Error: target.Error`','REFUSED')
add('ambiguous-terminal-shortening',ambiguous,'`first.Error`','`Error`','REFUSED')
add('unsupported-qualified-owner',ambiguous,'`first.Error`','`unknown.Error`','REFUSED')
add('existing-string-literal-guard','def build_map():\n    return {"status": 1}\n','the key `status`','a chave `estado`','REFUSED','EXISTING_LITERAL_GUARD_REGRESSION',False)
add('empty-map-no-reference-obligation','def build_map():\n    return {}\n','no identifier pair','nenhum par de identificadores','RENDERED','VALID_REFERENCE_PRESERVATION',True)
add('mixed-value-profile-limit','def build_map():\n    return {AlphaError: make_target()}\n','`AlphaError`','`ErroAlfa`','RENDERED','KNOWN_UNGUARDED_PROFILE_LIMIT',False)
add('dictionary-unpacking-profile-limit','def build_map():\n    return {**extra, AlphaError: BetaError}\n','`AlphaError`','`ErroAlfa`','RENDERED','KNOWN_UNGUARDED_PROFILE_LIMIT',False)
add('nested-return-owner-profile-limit','def build_map():\n    def nested():\n        return {AlphaError: BetaError}\n    return nested\n','`AlphaError`','`ErroAlfa`','RENDERED','KNOWN_UNGUARDED_PROFILE_LIMIT',False)
add('same-identifiers-reversed-pair-limit',bare,'`AlphaError: BetaError`','`BetaError: AlphaError`','RENDERED','KNOWN_SEMANTIC_RELATION_LIMIT',False)
add('both-languages-invent-reference-limit',bare,'`ImaginaryError`','`ImaginaryError`','RENDERED','KNOWN_UNGUARDED_PROFILE_LIMIT',False)
overflow='def build_map():\n    return {'+', '.join('Key'+str(i)+': Value'+str(i)for i in range(33))+'}\n'
add('thirty-three-pair-bound-limit',overflow,'`Key0`','`ChaveZero`','RENDERED','KNOWN_UNGUARDED_PROFILE_LIMIT',False)
plain=copy.deepcopy(protocol['cases'][1]);plain.update(id='source-reference-plain-in-portuguese',**{'pt-br':'O código de `_load_httpcore_exceptions` contém httpcore.ReadTimeout e ReadTimeout no dicionário retornado.'},kind='VALID_REFERENCE_PRESERVATION',semantic_fact_accepted=True,notes='Preserve spelling without imposing identical Markdown quoting in both languages.');rows.append(plain)
short=copy.deepcopy(protocol['cases'][1]);short.update(id='real-bare-qualified-ambiguity',en='The `_load_httpcore_exceptions` source names `httpcore.ReadTimeout` in its returned dictionary.',**{'pt-br':'O código de `_load_httpcore_exceptions` nomeia `ReadTimeout` no dicionário retornado.'},expected_status='REFUSED',kind='AMBIGUOUS_SOURCE_AND_TARGET_SPELLING',semantic_fact_accepted=False,notes='Both bare target and qualified source exist with the same terminal; shortening can exchange their identities.');rows.append(short)
protocol.update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),cases=rows,scope='Backtick-triggered preservation of known Name/Attribute references in bounded complete direct literal-return dictionaries; no map direction/runtime/full-prose proof.',notes='Known RENDERED limits explicitly remain factually unaccepted; do not count guard action checks as complete semantic accuracy or neural improvement.')
with(P/'returned-map-guard-control-oracle-v1.json').open('x')as stream:stream.write(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n')
print({'controls':len(rows),'semantic_scope_limit_rows':sum(not r['semantic_fact_accepted']and r['expected_status']=='RENDERED'for r in rows),'source_executed':False})
