"""Verify the new current-source supplement and preserve historical body identity."""
import datetime
import hashlib
import json
from pathlib import Path
import re

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
ledger=json.loads((P/'self-chapter-supplement-ledger-v3.json').read_text())
pack_path=P/'self-chapter-supplement-evidence-v4.json'
pack=json.loads(pack_path.read_text())
sha=lambda raw:hashlib.sha256(raw).hexdigest()
checks={'source_pack_identity':sha(pack_path.read_bytes())==ledger['source_evidence_sha256']}
for unit in pack['units']:
 raw=(ROOT/unit['source_path']).read_bytes();quote=''.join(raw.decode().splitlines(keepends=True)[unit['first_line']-1:unit['last_line']])
 checks['physical_source:'+unit['id']]=sha(raw)==unit['source_sha256']and quote==unit['quote']and sha(quote.encode())==unit['quote_sha256']
texts={}
for filename,expected in ledger['files'].items():
 file=P/filename;raw=file.read_bytes();language=file.stem;texts[language]=raw.decode();checks['file:'+language]=sha(raw)==expected['sha256']and len(raw)==expected['bytes']
 for claim in ledger['claims']:checks['claim:'+language+':'+claim['id']]=claim[language]in texts[language]
 for faq in ledger['faq']:checks['faq:'+language+':'+faq['id']]=faq[language+'_q']in texts[language]and faq[language+'_a']in texts[language]
 for index,target in enumerate(re.findall(r'\]\(([^)]+)\)',texts[language])):
  checks['link:'+language+':'+str(index)]=(file.parent/target.split('#')[0]).resolve().is_file()
for record in ledger['historical_checks']:checks['historical:'+record['language']]=sha((ROOT/record['path']).read_bytes())==record['sha256']
checks['paired_inline_identifiers']=re.findall(r'`([^`\n]+)`',texts['en'])==re.findall(r'`([^`\n]+)`',texts['pt-br'])
checks['no_publication_or_training']=ledger['owner_approved']is False and ledger['training_gold']is False and ledger['training_exclusion']is True and ledger['published_catalog_written']is False and ledger['frozen_v10_modified']is False
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'all_passed':all(checks.values()),'checks_count':len(checks),'claims':len(ledger['claims']),'faq_pairs':len(ledger['faq']),'historical_bodies_unchanged':True,'manual_faq_relevance_review':'Codex reviewed six question-specific assigned answers; no independent human certification.','full_prose_entailment_or_semantic_equivalence_certified':False,'source_executed':False,'model_calls':0,'publication_authorized':False}
with(P/'self-chapter-supplement-verification-v3.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'all_passed':record['all_passed'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v]})
