"""Direct operator-owned consumption of an audited remaining budget, not a router."""
import datetime,hashlib,importlib.util,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
sys.path.insert(0,str(ROOT/'agent/tools'))
from documentation_retrieval import HelperRetrieval
spec=importlib.util.spec_from_file_location('recovered_budget_consumer_audit',P/'helper_recovery_budget_audit_v1.py');audit_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit_module)
old=P/'helper-journal-public-v1';journal=P/'helper-journal-recovered-consumer-v1';journal.mkdir()
for path in old.iterdir():
    if path.is_file():(journal/path.name).write_bytes(path.read_bytes())
registry=json.loads((P/'helper-public-registry-v1.json').read_text());ids=sorted(path.name.removesuffix('.request.json')for path in old.glob('*.request.json'))
plan=audit_module.audit(registry,str(journal),ids,total_steps=5,total_quote_bytes=24576)
assert plan['status']=='AVAILABLE'and plan['remaining_steps']==1 and plan['remaining_quote_bytes']==24576-1603
# Operator-owned single-process journal: verify every audited byte immediately before constructing the helper.
assert all(hashlib.sha256((journal/name).read_bytes()).hexdigest()==expected for name,expected in plan['snapshot_hashes'].items())
helper=HelperRetrieval(registry,str(journal),max_steps=plan['remaining_steps'],max_quote_bytes=plan['remaining_quote_bytes'])
entry=registry['jmespath']
def request(key,path,selector):return {'request_id':key,'source_id':'jmespath','revision':entry['revision'],'path':path,'qualified_symbol':selector,'expected_sha256':entry['files'][path]['sha256']}
fifth=helper.request(request('recovered-fifth','jmespath/parser.py','ParsedResult.search'))
sixth=helper.request(request('beyond-total-sixth','jmespath/__init__.py','compile'))
assert fifth['status']=='FOUND'and sixth['status']=='BUDGET_EXHAUSTED'
after=audit_module.audit(registry,str(journal),ids+['recovered-fifth'],total_steps=5,total_quote_bytes=24576)
assert after['status']=='EXHAUSTED'and after['used_steps']==5 and after['used_quote_bytes']==1603+fifth['quote_bytes']
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'initial_audit':plan,'fifth_result':fifth,'sixth_result':sixth,'final_audit':after,'all_checks_pass':True,'source_executed':False,'new_distinct_control_cases':0,'integration_demonstration':True,'automatic_model_routing':False,'ruby_routing_changed':False,'journal_access':'operator-owned exclusive single-process demonstration, no interprocess lock','original_journal_changed':False,'owner_approved':False,'training_gold':False,'model_calls':0}
with(P/'helper-recovered-budget-consumption-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'fifth':fifth['status'],'sixth':sixth['status'],'final':after['status'],'total_steps':after['used_steps'],'total_quote_bytes':after['used_quote_bytes']})
