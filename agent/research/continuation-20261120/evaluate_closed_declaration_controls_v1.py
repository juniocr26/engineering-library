"""Owned admission/action observations for the closed declaration adapter."""
import copy
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path

P=Path(__file__).resolve().parent
producer=P/'closed_declaration_lifecycle_v1.py'
spec=importlib.util.spec_from_file_location('closed_decl',producer);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def packet(before,after,en,pt):
    return {'id':'owned-claim','family':'owned-declaration-controls','language':'python','previous_source':before,'current_source':after,
            'documentation':{'en':en,'pt-br':pt},'complete_scope':True,'source_available':True,'positive_retirement_evidence':None,'logical_contract_id':'owned.api','metadata':{}}

old='def api():\n    return 1\n';param='def api(limit=None):\n    return 1\n'
no=('api has no limit parameter.','api não possui parâmetro limit.')
tupledocs=('api returns the tuple key, value.','api retorna a tupla key, value.')
tuplesrc='def api(key, value):\n    return key, value\n'
cases=[]
def add(i,before,after,docs,expected,mutate=None):
    p=packet(before,after,*docs)
    if mutate:mutate(p)
    cases.append({'id':i,'packet':p,'expected':expected})
add('new-note-empty-logical-slot','pass\n',old,('',''),'ADD')
add('added-explicit-parameter',old,param,no,'MODIFY')
add('unchanged-absent-parameter',old,old,no,'NO-OP')
add('vararg-name-present',old,'def api(*limit):\n    return 1\n',no,'MODIFY')
add('kwarg-name-present',old,'def api(**limit):\n    return 1\n',no,'MODIFY')
add('stable-tuple-parentheses','def api(key, value):\n    return (key, value)\n',tuplesrc,tupledocs,'NO-OP')
add('tuple-order-changed',tuplesrc,'def api(key, value):\n    return value, key\n',tupledocs,'MODIFY')
add('side-effect-before-tuple',tuplesrc,'def api(key, value):\n    helper()\n    return key, value\n',tupledocs,'INCONCLUSIVE')
add('bilingual-parameter-disagrees',old,param,(no[0],'api não possui parâmetro other.'),'INCONCLUSIVE')
add('foreign-document-selector',old,param,('other has no limit parameter.','other não possui parâmetro limit.'),'INCONCLUSIVE')
add('source-unavailable',old,param,no,'INCONCLUSIVE',lambda p:p.update(source_available=False))
add('incomplete-module-scope',old,param,no,'INCONCLUSIVE',lambda p:p.update(complete_scope=False))
add('known-dynamic-module-binding',old,'def api():\n    return 1\nglobals()["api"] = replacement\n',no,'INCONCLUSIVE')
add('missing-current-symbol-never-removes',old,'def other():\n    return 1\n',no,'INCONCLUSIVE')
add('extra-runtime-assertion',old,param,(no[0]+' It is thread safe.',no[1]+' É segura entre threads.'),'INCONCLUSIVE')
add('one-empty-language',old,param,('',no[1]),'INCONCLUSIVE')
add('invalid-current-syntax',old,'def api(:\n',no,'INCONCLUSIVE')
add('unadmitted-metadata-extension',old,param,no,'INCONCLUSIVE',lambda p:p.update(metadata={'current_path':'other.py'}))
add('tuple-global-names-unresolved',old,'def api():\n    return key, value\n',tupledocs,'INCONCLUSIVE')
one='import os\n\ndef api(value):\n    return (value,)\n'
add('unrelated-import-does-not-execute',one,one,('api returns the tuple value.','api retorna a tupla value.'),'NO-OP')
add('keyword-is-not-parameter-token',old,param,('api has no class parameter.','api não possui parâmetro class.'),'INCONCLUSIVE')
add('whitespace-is-not-certified-empty-slot','pass\n',old,(' ',' '),'INCONCLUSIVE')
marker=Path('/tmp/el-closed-declaration-owned-noexec-20261120')
if marker.exists():raise ValueError('pre-existing marker;preserve and do not claim non-execution')
malicious=old+'open("'+str(marker)+'", "w").write("must-not-execute")\n'
add('module-side-effect-is-not-executed',malicious,malicious,no,'NO-OP')
add('empty-slot-existing-source-not-new-declaration',old,old,('',''),'INCONCLUSIVE')
oracle={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_before_predictions':True,'producer_sha256':hashlib.sha256(producer.read_bytes()).hexdigest(),'cases':cases,'marker':str(marker),'scope':'Owned controlled observations;no permanent test/source application execution.'}
with(P/'closed-declaration-control-oracle-v1.json').open('x')as stream:json.dump(oracle,stream,indent=2,ensure_ascii=False)
rows=[]
for case in cases:
    result=m.decision(case['packet']);ok=result['action']==case['expected']and not marker.exists()
    rows.append({'id':case['id'],'expected':case['expected'],'observed':result['action'],'matches':ok,'marker_absent':not marker.exists(),'result':result})
report={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'correct':sum(r['matches']for r in rows),'n':len(rows),'rows':rows,'source_executed':False,'model_calls':0,'physical_paths_or_docs_certified':False}
with(P/'closed-declaration-controls-v1.json').open('x')as stream:json.dump(report,stream,indent=2)
print(json.dumps({'correct':report['correct'],'n':report['n'],'failures':[{'id':r['id'],'action':r['observed'],'reason':r['result'].get('reason')}for r in rows if not r['matches']]}))
