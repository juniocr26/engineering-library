"""Frozen positive/rename observations plus the prior 24-case regression matrix."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path

P=Path(__file__).resolve().parent
old=json.loads((P/'closed-declaration-control-oracle-v1.json').read_text())
base=old['cases'][1]['packet']
import copy
cases=[]

def add(i,before,after,en,pt,expected):
    packet=copy.deepcopy(base);packet.update(previous_source=before,current_source=after,documentation={'en':en,'pt-br':pt})
    cases.append({'id':i,'packet':packet,'expected':expected})

none='def api():\n    return 1\n';param='def api(limit=None):\n    return 1\n'
yes=('api has a limit parameter.','api possui parâmetro limit.')
add('positive-present',param,param,*yes,'NO-OP')
add('removed-named-parameter-modifies',param,none,*yes,'MODIFY')
add('renamed-parameter-not-remove','def api(old_name=0):\n    return 1\n','def api(new_name=0):\n    return 1\n','api has an old_name parameter.','api possui parâmetro old_name.','MODIFY')
add('vararg-exact-name-present',param,'def api(*limit):\n    return 1\n',*yes,'NO-OP')
add('kwarg-exact-name-present',param,'def api(**limit):\n    return 1\n',*yes,'NO-OP')
add('arbitrary-kwargs-key-not-named-parameter',param,'def api(**options):\n    return 1\n',*yes,'MODIFY')
add('article-an-admitted',param,param,'api has an limit parameter.',yes[1],'NO-OP')
add('bilingual-presence-disagrees',param,param,yes[0],'api não possui parâmetro limit.','INCONCLUSIVE')
add('positive-extra-runtime-claim',param,param,yes[0]+' It never fails.',yes[1]+' Nunca falha.','INCONCLUSIVE')
add('missing-function-still-inconclusive',param,'def other():\n    return 1\n',*yes,'INCONCLUSIVE')
add('keyword-rejection-not-inferred',param,none,'api rejects limit as an unexpected keyword.','api rejeita limit como opção inesperada.','INCONCLUSIVE')
add('case-sensitive-parameter-name',param,'def api(Limit=None):\n    return 1\n',*yes,'MODIFY')
producer=P/'closed_declaration_lifecycle_v2.py'
oracle={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_before_predictions':True,'producer_sha256':hashlib.sha256(producer.read_bytes()).hexdigest(),'prior_control_oracle_sha256':hashlib.sha256((P/'closed-declaration-control-oracle-v1.json').read_bytes()).hexdigest(),'new_cases':cases,'prior_cases_reused':len(old['cases']),'scope':'Parameter declarations,not keywordacceptance/runtime/retirement. Alternative English article is harmless closed-syntax variation.'}
with(P/'positive-parameter-control-oracle-v1.json').open('x')as stream:json.dump(oracle,stream,indent=2,ensure_ascii=False)
s=importlib.util.spec_from_file_location('positive_decl',producer);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
rows=[]
for group,group_cases in [('prior-regression',old['cases']),('positive-new',cases)]:
    for case in group_cases:
        result=m.decision(case['packet']);rows.append({'id':case['id'],'group':group,'expected':case['expected'],'observed':result['action'],'matches':result['action']==case['expected'],'result':result})
report={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'n':len(rows),'correct':sum(x['matches']for x in rows),'rows':rows,'new_owned_control_count':len(cases),'repeated_prior_control_count':len(old['cases']),'source_executed':False,'permanent_tests_modified':False}
with(P/'positive-parameter-controls-v1.json').open('x')as stream:json.dump(report,stream,indent=2)
print(json.dumps({'correct':report['correct'],'n':report['n'],'new':len(cases),'prior':len(old['cases']),'failures':[(x['id'],x['observed'],x['result']['reason'])for x in rows if not x['matches']]}))
