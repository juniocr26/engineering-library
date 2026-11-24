"""Separate guard-contract checks from semantic acceptance and scope limits."""
import collections
import datetime
import json
from pathlib import Path

P=Path(__file__).resolve().parent
protocol=json.loads((P/'returned-map-guard-control-oracle-v2.json').read_text())
before=json.loads((P/'returned-map-renderer-controls-baseline-v2.json').read_text())
after=json.loads((P/'returned-map-renderer-candidate-v1.json').read_text())
rows=[]
for reference,old,new in zip(protocol['cases'],before['rows'],after['rows'],strict=True):
 assert reference['id']==old['id']==new['id']
 rows.append({'id':reference['id'],'kind':reference['kind'],'expected_guard_status':reference['expected_status'],'before':old['status'],'after':new['status'],'guard_contract_matches':new['status']==reference['expected_status'],'semantic_fact_accepted':reference['semantic_fact_accepted'],'published':False,'owner_approved':False,'training_gold':False})
groups={}
for kind in sorted({r['kind']for r in rows}):
 selected=[r for r in rows if r['kind']==kind]
 groups[kind]={'n':len(selected),'after_statuses':dict(collections.Counter(r['after']for r in selected)),'semantic_fact_acceptance':[r['semantic_fact_accepted']for r in selected]}
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'caller_before':'1.9.42','caller_after':'1.9.43','before_guard_contract_matches':before['matches'],'after_guard_contract_matches':after['matches'],'n':len(rows),'groups':groups,'rows':rows,'valid_reference_rows_preserved':sum(r['semantic_fact_accepted']and r['after']=='RENDERED'for r in rows),'known_unaccepted_facts_still_rendered':sum(not r['semantic_fact_accepted']and r['after']=='RENDERED'for r in rows),'new_identifier_error_rows_changed_to_refusal':sum(r['before']=='RENDERED'and r['after']=='REFUSED'for r in rows),'scope':'AST-derived known Name/Attribute reference presence under backtick trigger; no map relation, full prose, arbitrary code keys or runtime binding certification.','guards_tested_through_actual_source_reader_and_renderer':True,'permanent_tests_modified':False,'model_calls':0,'source_executed':False,'training_exclusion':True,'does_19_of_19_mean_semantic_accuracy':False}
with(P/'returned-map-guard-diagnostic-review-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({k:record[k]for k in ['before_guard_contract_matches','after_guard_contract_matches','n','valid_reference_rows_preserved','known_unaccepted_facts_still_rendered','new_identifier_error_rows_changed_to_refusal','does_19_of_19_mean_semantic_accuracy']})
