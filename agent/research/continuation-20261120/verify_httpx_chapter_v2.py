"""Verify frozen physical source, paired code and chapter/FAQ identities only."""
import datetime
import hashlib
import json
from pathlib import Path
import re

P=Path(__file__).resolve().parent
path=P/'httpx-chapter-ledger-v2.json';ledger=json.loads(path.read_text())
sha=lambda raw:hashlib.sha256(raw).hexdigest()
checks={}
for identity,unit in ledger['units'].items():
 source=P/'new-public-sources-v1/encode--httpx'/unit['revision']/unit['path'];raw=source.read_bytes();quote=''.join(raw.decode().splitlines(keepends=True)[unit['first_line']-1:unit['last_line']])
 checks['physical:'+identity]=sha(raw)==unit['source_sha256']and quote==unit['quote']and sha(quote.encode())==unit['quote_sha256']
 checks['quote_bound:'+identity]=len(quote.encode())<=6144
texts={}
for name,expected in ledger['files'].items():
 source=P/name;raw=source.read_bytes();checks['candidate:'+name]=sha(raw)==expected['sha256']and len(raw)==expected['bytes']
 if source.suffix!='.md':compile(raw,'<unexecuted-example>','exec',dont_inherit=True);checks['example_syntax']=True;continue
 language=source.stem;body=raw.decode();texts[language]=body
 for claim in ledger['claims']:checks['claim:'+language+':'+claim['id']]=claim[language]in body
 for faq in ledger['faq']:checks['faq:'+language+':'+faq['id']]=faq[language+'_q']in body and faq[language+'_a']in body
 refs=set(re.findall(r'\[source:([^\]]+)\](?!:)',body));checks['registered_refs:'+language]=bool(refs)and refs<=set(ledger['units'])
 for identity,target in re.findall(r'^\[source:([^\]]+)\]: (\S+)',body,re.M):
  checks['link:'+language+':'+identity]=(source.parent/target.split('#')[0]).resolve().is_file()
checks['paired_inline_code']=re.findall(r'`([^`\n]+)`',texts['en'])==re.findall(r'`([^`\n]+)`',texts['pt-br'])
checks['paired_code_blocks']=re.findall(r'```[^\n]*\n(.*?)\n```',texts['en'],re.S)==re.findall(r'```[^\n]*\n(.*?)\n```',texts['pt-br'],re.S)
checks['seven_questions_each']=all(len(re.findall(r'^### ',body,re.M))==7 for body in texts.values())
checks['no_promotion']=ledger['owner_approved']is False and ledger['training_gold']is False and ledger['published']is False and ledger['training_exclusion']is True
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ledger_sha256':sha(path.read_bytes()),'checks':checks,'checks_count':len(checks),'all_passed':all(checks.values()),'full_prose_entailment_or_semantic_equivalence_certified':False,'manual_review_author':'Codex; no independent human review','example_or_httpx_source_executed':False,'http_application_requests':0,'model_calls':0,'publication_authorized':False}
with(P/'httpx-chapter-verification-v2.json').open('x')as stream:stream.write(json.dumps(record,indent=2)+'\n')
print({'all_passed':record['all_passed'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v]})
