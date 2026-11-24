"""Prepare immutable isolated research inputs; no source or tool execution."""
from pathlib import Path
import copy
import json
import datetime
import hashlib

P=Path(__file__).resolve().parent
OUT=P/'helper-removal-boundary-v1'
assert not OUT.exists()
OUT.mkdir()
old='def cost_comparison():\n    return 1\n'
replacement='def estimate_cost():\n    return 1\n'
identity='owned.query-cost-comparison'
reason='Explicit retirement in this owned positive-control scenario only'
retirement={'contract_id':identity,'source':'current module RETIRED_CONTRACTS','reason':reason,'aliases_checked':True,'relocations_checked':True}
base={'id':'','family':'owned-helper-refactor','language':'python','previous_source':old,'current_source':replacement,'documentation':{'en':'cost_comparison returns 1.','pt-br':'cost_comparison retorna 1.'},'complete_scope':True,'source_available':True,'logical_contract_id':identity,'metadata':{'selector':'cost_comparison','previous_path':'owned/before.py','current_path':'owned/after.py','managed_ownership':False,'human_authored':False}}
cases=[]
def add(ident,expected,change=None,basis=''):
    q=copy.deepcopy(base)
    q['id']=ident
    if change:change(q)
    cases.append({'id':ident,'expected_action':expected,'basis':basis,'packet':q})
add('unrecorded-refactor','INCONCLUSIVE',basis='Old symbol absent; continuation has no admitted identity/retirement declaration. Absence alone is insufficient.')
def alias(q):
    q['current_source']=replacement+"\nCONTRACT_ALIASES = {'cost_comparison': 'estimate_cost'}\n"
    q['metadata']['renamed_to']='estimate_cost'
add('explicit-alias','MODIFY',alias,'Positive identity-preserving alias and replacement; do not retire documentation.')
def native_absence(q):
    q['positive_retirement_evidence']=dict(retirement,source='native exact selector has zero matches')
add('absence-asserted-as-retirement','INCONCLUSIVE',native_absence,'A native absence claim is not the required positive source retirement registry.')
def conflicting(q):
    q['current_source']=replacement+"\nCONTRACT_ALIASES = {'cost_comparison': 'estimate_cost'}\nRETIRED_CONTRACTS = {"+repr(identity)+': '+repr(reason)+'}\n'
    q['positive_retirement_evidence']=copy.deepcopy(retirement)
add('alias-retirement-conflict','INCONCLUSIVE',conflicting,'Current alias prevents the retirement branch; no metadata rename target is supplied to bypass that conflict.')
def retired(q):
    q['current_source']='RETIRED_CONTRACTS = {'+repr(identity)+': '+repr(reason)+'}\n'
    q['positive_retirement_evidence']=copy.deepcopy(retirement)
add('positive-retirement-control','REMOVE',retired,'Positive owned retirement declaration with established previous definition and required checks; not real Prometheus retirement.')
def no_previous(q):
    retired(q)
    q['previous_source']='def unrelated():\n    return 1\n'
add('retirement-without-previous-definition','INCONCLUSIVE',no_previous,'No established previous selected definition.')
def unchecked_alias(q):
    retired(q)
    q['positive_retirement_evidence']['aliases_checked']=False
add('retirement-aliases-unchecked','INCONCLUSIVE',unchecked_alias,'Positive declaration does not replace required alias check.')
def unchecked_relocation(q):
    retired(q)
    q['positive_retirement_evidence']['relocations_checked']=False
add('retirement-relocations-unchecked','INCONCLUSIVE',unchecked_relocation,'Positive declaration does not replace required relocation check.')
def current_reference(q):
    q['metadata']['selector']='estimate_cost'
    q['documentation']={'en':'See owned/after.py for estimate_cost.','pt-br':'Consulte owned/after.py para estimate_cost.'}
add('replacement-reference-already-current','NO-OP',current_reference,'Exact existing paired reference already targets the present replacement definition; preserve it.')
def new_helper_doc(q):
    q['logical_contract_id']='owned.estimate_cost'
    q['metadata']['selector']='estimate_cost'
    q['documentation']={'en':'','pt-br':''}
add('replacement-helper-new-document','ADD',new_helper_doc,'Owned helper-scoped empty documentation, no previous replacement definition and positive current definition; not a whole-feature ADD.')
source=P/'prometheus-query-revision-source-v1'
real=copy.deepcopy(base)
real.update(id='real-go-full-files',family='prometheus-exposed-real-source',language='go',previous_source=(source/'before/web/api/v1/api.go').read_text(),current_source=(source/'after/web/api/v1/api.go').read_text(),logical_contract_id='prometheus.query-cost-comparison',documentation={'en':'The selected query handler performs cost comparison after successful execution.','pt-br':'O manipulador selecionado compara o custo após a execução bem-sucedida.'},metadata={'selector':'API.costComparison','previous_path':'web/api/v1/api.go','current_path':'web/api/v1/api.go','managed_ownership':False,'human_authored':False})
before_packet=json.loads((P/'prometheus-query-revision-native-v1/before-2-response.json').read_text())
native_old=next(u['quote'] for u in before_packet['units'] if u['selector']=='API.costComparison')
after_packet=json.loads((P/'prometheus-query-revision-native-v1/after-2-response.json').read_text())
native_new=next(u['quote'] for u in after_packet['units'] if u['selector']=='API.estimateForComparison')
partial=copy.deepcopy(real)
partial.update(id='real-go-declared-partial',previous_source='package v1\n'+native_old+'\n',current_source='package v1\n'+native_new+'\n',complete_scope=False)
real_cases=[{'id':real['id'],'expected_safety_action':'INCONCLUSIVE','full_context_document_action':'MODIFY','automation_target':True,'basis':'Actual complete selected files, not repository-wide completeness. Existing Go observer only admits tiny written integer-return modules and max64KiB source; do not simulate generic support.','packet':real},{'id':partial['id'],'expected_safety_action':'INCONCLUSIVE','full_context_document_action':'MODIFY','automation_target':False,'basis':'Intentionally incomplete selected excerpts; no retirement proof. The full-context oracle is distinct from packet-level safe abstention.','packet':partial}]
records=[]
for case in cases+real_cases:
    q=OUT/(case['id']+'-input.json')
    q.write_text(json.dumps(case['packet'],ensure_ascii=False,indent=2)+'\n')
    records.append({k:v for k,v in case.items() if k!='packet'}|{'input':q.name,'sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'bytes':q.stat().st_size})
native={'path':'web/api/v1/api.go','source':real['current_source'],'selectors':['API.costComparison']}
q=OUT/'native-missing-old-helper-request.json'
q.write_text(json.dumps(native,ensure_ascii=False)+'\n')
protocol={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'before_controlled_outcomes':True,'planner':'agent/tools/documentation_lifecycle.py','planner_version':'0.3.6','planner_sha256':hashlib.sha256((P.parents[1]/'tools/documentation_lifecycle.py').read_bytes()).hexdigest(),'owned_cases':records[:10],'real_source_admission_probes':records[10:],'native_negative_request':{'path':q.name,'sha256':hashlib.sha256(q.read_bytes()).hexdigest()},'scope':'Ten owned closed-grammar observations with scoped helper/document ownership; two real source admission probes; one native negative lookup. Separate populations, not13independent tasks or neural/wholechapter tests.','new_hypothesis':'Missing helper name after a continuing-feature refactor is not whole-chapter retirement. Positive/contradictory declaration controls prevent interpreting uniform refusal as a semantic safeguard.','source_or_tests_executed':False,'training_eligible':False,'owner_approved':False}
(OUT/'frozen-input-manifest.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'owned':len(cases),'real_source_probes':len(real_cases),'native_negative_probes':1,'source_bytes_each':{'before':len(real['previous_source'].encode()),'after':len(real['current_source'].encode())}},indent=2))
