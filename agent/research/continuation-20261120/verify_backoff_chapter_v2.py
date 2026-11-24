"""Physical/bilingual structural verification; not autonomous semantic proof."""
import datetime,hashlib,json,re
from pathlib import Path
P=Path(__file__).resolve().parent;path=P/'backoff-chapter-ledger-v2.json';raw=path.read_bytes();ledger=json.loads(raw);pack=json.loads((P/'backoff-source-pack-v1.json').read_text());runtime=json.loads((P/'backoff-confined-runtime-results-v1.json').read_text());checks=[]
def check(id,value):checks.append({'id':id,'pass':value is True})
check('source-pack-hash',hashlib.sha256((P/'backoff-source-pack-v1.json').read_bytes()).hexdigest()==ledger['source_pack_sha256']);check('runtime-receipt-hash',hashlib.sha256((P/'backoff-confined-runtime-results-v1.json').read_bytes()).hexdigest()==ledger['runtime_results_sha256'])
for id,u in ledger['units'].items():
 source=(P/u['source_snapshot']).read_bytes();quote='\n'.join(source.decode().splitlines()[u['first_line']-1:u['last_line']]);check('physical-unit:'+id,hashlib.sha256(source).hexdigest()==u['source_sha256']and quote==u['quote']and hashlib.sha256(quote.encode()).hexdigest()==u['quote_sha256'])
compiler_ids={r['id']for cut in json.loads((P/'backoff-source-compatibility-results-v1.json').read_text())['results']for r in cut['rows']}
case_ids={r['id']for cut in runtime['results']for r in cut['rows']};claimmap={c['id']:c for c in ledger['claims']}
for c in ledger['claims']:
 check('code-identifiers:'+c['id'],re.findall(r'`([^`]+)`',c['en'])==re.findall(r'`([^`]+)`',c['pt-br']))
 check('numeric-tokens:'+c['id'],re.findall(r'\d+(?:\.\d+)*',c['en'])==re.findall(r'\d+(?:\.\d+)*',c['pt-br']))
 check('compiler-consumer-ids:'+c['id'],all(id in compiler_ids for id in c['compiler_consumer_ids']))
 check('evidence-ids:'+c['id'],bool(c['evidence_ids'])and all(id in ledger['units']for id in c['evidence_ids'])and all(id in case_ids for id in c['runtime_case_ids']))
for f in ledger['faq']:
 c=claimmap[f['claim_id']];check('faq-answer-claim:'+f['id'],all(f[lang+'_a']==c[lang]for lang in ['en','pt-br'])and f['evidence_ids']==c['evidence_ids'])
for name,entry in ledger['files'].items():
 file=P/name;body=file.read_bytes();text=body.decode();refs=re.findall(r'\[source:([^\]]+)\]',text);local=[]
 for target in re.findall(r'\]\(([^)]+)\)',text):
  if not target.startswith(('https://','http://')):local.append((file.parent/target).is_file())
 check('chapter-file:'+name,hashlib.sha256(body).hexdigest()==entry['sha256']and len(body)==entry['bytes']);check('chapter-source-refs:'+name,all(ref in ledger['units']for ref in refs));check('chapter-local-links:'+name,all(local));check('chapter-code-fences:'+name,text.count('```')%2==0)
check('unapproved-flags',all(ledger[k]is False for k in ['owner_approved','training_gold','publication_authorized','example_executed','command_executed'])and ledger['training_excluded']is True)
check('runtime-counts',[(cut['passes'],cut['cases'])for cut in runtime['results']]==[(30,30),(38,38)])
check('compatibility-counts',all(cut['passes']==cut['cases']==6 for cut in json.loads((P/'backoff-source-compatibility-results-v1.json').read_text())['results']))
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ledger_sha256':hashlib.sha256(raw).hexdigest(),'checks':checks,'passes':sum(c['pass']for c in checks),'count':len(checks),'all_pass':all(c['pass']for c in checks),'claims':len(ledger['claims']),'faq_pairs':len(ledger['faq']),'manual_semantic_review_notes':['Complete current loop evidence requires private doRetryNotify, not only the public RetryNotifyWithTimer wrapper.','Prior cancellation does not prevent the observed valid initial operation; success and permanent error precedence remain explicit.','Configured Stop field and package -1 sentinel are distinguished. The bounded positive-value example completed on the second operation; no infinite-run or new-effect claim.','Max-retry count differs from total attempts; generic errors may carry nonzero last data.','Zero-argument invocation remains source-compatible in the owned compiler cases while zero-argument function-value assignment does not.','V2 corrects channel terminology: owned timer Start immediately supplies a buffered value, not an unbuffered synchronous Go channel. V1 remains preserved.','The exact illustrative example and go doc command are not claimed executed.','Seven FAQ answers derive from current chapter claims; no independent owner gold or usage rights approval.'],'limits':'Code-span/number equality and physical citations do not by themselves prove natural-language entailment or semantic translation. Semantic notes are Codex source review, not independent owner approval.','training_excluded':True,'owner_approved':False,'training_gold':False,'model_calls':0,'source_executed_by_verifier':False}
with(P/'backoff-chapter-verification-v2.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'checks':len(checks),'passes':r['passes'],'all_pass':r['all_pass'],'failures':[c['id']for c in checks if not c['pass']]})
