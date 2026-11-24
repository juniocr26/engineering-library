import datetime,hashlib,json,shutil,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
sys.path.insert(0,str(ROOT/'agent/tools'))
from documentation_retrieval import HelperRetrieval
protocol=json.loads((P/'helper-recovery-budget-protocol-v1.json').read_text())
assert hashlib.sha256((ROOT/'agent/tools/documentation_retrieval.py').read_bytes()).hexdigest()==protocol['source_helper_sha256']
old=P/'helper-journal-public-v1';copy=P/'helper-journal-budget-copy-v1';copy.mkdir()
for name,expected in protocol['original_journal_files'].items():
 raw=(old/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected;(copy/name).write_bytes(raw)
registry=json.loads((P/'helper-public-registry-v1.json').read_text())
helper=HelperRetrieval(registry,str(copy),max_steps=1,max_quote_bytes=6144)
entry=registry['jmespath'];path='jmespath/parser.py'
request={'request_id':'new-instance-fifth-request','source_id':'jmespath','revision':entry['revision'],'path':path,'qualified_symbol':'ParsedResult.search','expected_sha256':entry['files'][path]['sha256']}
result=helper.request(request)
assert result['status']=='FOUND'
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'request':request,'result':result,'instance_steps':helper.steps,'prior_completed_distinct_requests':4,'resulting_journal_distinct_requests':5,'prior_quote_bytes':1603,'new_quote_bytes':result['quote_bytes'],'original_journal_unchanged':all(hashlib.sha256((old/name).read_bytes()).hexdigest()==expected for name,expected in protocol['original_journal_files'].items()),'source_executed':False,'new_model_calls':0,'interpretation':'Expected per-instance behavior reproduced. A caller restoring a four-step total campaign budget must not make this fifth request. Earlier public consumer explicitly used a remaining budget and was not affected.'}
with(P/'helper-recovery-budget-baseline-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'status':result['status'],'instance_steps':helper.steps,'journal_distinct_requests':5,'original_journal_unchanged':record['original_journal_unchanged']})
