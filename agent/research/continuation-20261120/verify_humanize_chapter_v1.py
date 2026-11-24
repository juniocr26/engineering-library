"""Physical/bilingual structural verification; not autonomous semantic proof."""
import datetime,hashlib,json,re
from pathlib import Path
P=Path(__file__).resolve().parent;path=P/'humanize-chapter-ledger-v1.json';raw=path.read_bytes();ledger=json.loads(raw);pack=json.loads((P/'humanize-source-pack-v1.json').read_text());runtime=json.loads((P/'humanize-confined-runtime-results-v1.json').read_text());checks=[]
def check(id,value):checks.append({'id':id,'pass':value is True})
check('source-pack-hash',hashlib.sha256((P/'humanize-source-pack-v1.json').read_bytes()).hexdigest()==ledger['source_pack_sha256']);check('runtime-receipt-hash',hashlib.sha256((P/'humanize-confined-runtime-results-v1.json').read_bytes()).hexdigest()==ledger['runtime_results_sha256'])
for id,u in ledger['units'].items():
 source=(P/u['source_snapshot']).read_bytes();quote='\n'.join(source.decode().splitlines()[u['first_line']-1:u['last_line']]);check('physical-unit:'+id,hashlib.sha256(source).hexdigest()==u['source_sha256']and quote==u['quote']and hashlib.sha256(quote.encode()).hexdigest()==u['quote_sha256'])
case_ids={r['id']for cut in runtime['results']for r in cut['rows']};claimmap={c['id']:c for c in ledger['claims']}
for c in ledger['claims']:
 check('code-identifiers:'+c['id'],re.findall(r'`([^`]+)`',c['en'])==re.findall(r'`([^`]+)`',c['pt-br']))
 check('numeric-tokens:'+c['id'],re.findall(r'\d+(?:\.\d+)*',c['en'])==re.findall(r'\d+(?:\.\d+)*',c['pt-br']))
 check('evidence-ids:'+c['id'],bool(c['evidence_ids'])and all(id in ledger['units']for id in c['evidence_ids'])and all(id in case_ids for id in c['runtime_case_ids']))
for f in ledger['faq']:
 c=claimmap[f['claim_id']];check('faq-answer-claim:'+f['id'],all(f[lang+'_a']==c[lang]for lang in ['en','pt-br'])and f['evidence_ids']==c['evidence_ids']and f['runtime_case_ids']==c['runtime_case_ids'])
for name,entry in ledger['files'].items():
 file=P/name;body=file.read_bytes();text=body.decode();refs=re.findall(r'\[source:([^\]]+)\]',text);local=[]
 for target in re.findall(r'\]\(([^)]+)\)',text):
  if not target.startswith(('https://','http://')):local.append((file.parent/target).is_file())
 check('chapter-file:'+name,hashlib.sha256(body).hexdigest()==entry['sha256']and len(body)==entry['bytes']);check('chapter-source-refs:'+name,all(ref in ledger['units']for ref in refs));check('chapter-local-links:'+name,all(local));check('chapter-code-fences:'+name,text.count('```')%2==0)
check('unapproved-flags',all(ledger[k]is False for k in ['owner_approved','training_gold','publication_authorized','example_executed','command_executed'])and ledger['training_excluded']is True)
check('actual-static-reader-15-each',all(cut['passes']==cut['cases']==15 and cut['source_copies_unchanged']for cut in json.loads((P/'humanize-static-initializers-results-v1.json').read_text())['results']))
check('original-36-predictions-preserved',all(cut['passes']==35 and cut['cases']==36 for cut in runtime['results']))
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ledger_sha256':hashlib.sha256(raw).hexdigest(),'checks':checks,'passes':sum(c['pass']for c in checks),'count':len(checks),'all_pass':all(c['pass']for c in checks),'claims':len(ledger['claims']),'faq_pairs':len(ledger['faq']),'manual_semantic_review_notes':['Dependencies statement is grounded in complete selected package/source list plus module metadata, not only callable citations. Module go1.16 is not testedminimumversion.','R/Q alias support distinguished by API. ParseBytes source file is byte-identical; ParseBigBytes initializer aliases are confirmed by the static typed reader.','BigComma mutates caller input; humanateBigBytes copies its own input. Diagrams/table carry only those selected written relationships.','ComputeSI exact-float prediction mismatch remains visible and is not rewritten into36/36.','Example and go doc command are illustrative, not executed. No invented installation success or example output.','Six FAQ answers derive from chapter claims and are not additional independent training examples.'],'limits':'Code-span/number equality and physical citations do not by themselves prove natural-language entailment or semantic translation. Semantic notes are Codex source review, not independent owner approval.','training_excluded':True,'owner_approved':False,'training_gold':False,'model_calls':0,'source_executed_by_verifier':False}
with(P/'humanize-chapter-verification-v1.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'checks':len(checks),'passes':r['passes'],'all_pass':r['all_pass'],'failures':[c['id']for c in checks if not c['pass']]})
