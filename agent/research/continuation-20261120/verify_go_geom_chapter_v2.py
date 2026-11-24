"""Physical/typed-provenance and bilingual-code checks, not general prose proof."""
import datetime
import hashlib
import json
from pathlib import Path
import re
import sys

P=Path(__file__).resolve().parent
ledger=json.loads((P/'go-geom-chapter-ledger-v2.json').read_text())
base=P/'new-public-sources-v1/twpayne--go-geom'/ledger['revision']
checks={};texts={}
for key,unit in ledger['units'].items():
    raw=(base/unit['source_path']).read_bytes();lines=raw.decode().split('\n')
    quote='\n'.join(lines[unit['first_line']-1:unit['last_line']])if unit['complete_callable_or_type']else''.join(raw.decode().splitlines(keepends=True)[unit['first_line']-1:unit['last_line']])
    checks['physical:'+key]=hashlib.sha256(raw).hexdigest()==unit['source_sha256']and quote==unit['quote']and hashlib.sha256(quote.encode()).hexdigest()==unit['quote_sha256']
static=P/ledger['static_receipt_path'];static_body=json.loads(static.read_text())
checks['static_package_receipt_identity']=hashlib.sha256(static.read_bytes()).hexdigest()==ledger['static_receipt_sha256']and static_body['all_checks_pass']
checks['subject_archive_identity']=hashlib.sha256((P/'go-geom-static-failed-reader-v1/geom-package.a').read_bytes()).hexdigest()==static_body['subject_archive_sha256']
for name,expected in ledger['files'].items():
    raw=(P/name).read_bytes();lang=Path(name).stem;text=raw.decode();texts[lang]=text
    checks['candidate_identity:'+lang]=len(raw)==expected['bytes']and hashlib.sha256(raw).hexdigest()==expected['sha256']
    refs=re.findall(r'\[source:([^\]]+)\]',text);checks['source_refs:'+lang]=bool(refs)and all(r in ledger['units']for r in refs)
    for claim in ledger['claims']:checks['claimtext:'+lang+':'+claim['id']]=claim[lang]in text
    checks['faq_count:'+lang]=len(re.findall(r'^### ',text,re.M))==7
checks['bilingual_inline_code_identical']=re.findall(r'`([^`\n]+)`',texts['en'])==re.findall(r'`([^`\n]+)`',texts['pt-br'])
checks['bilingual_fenced_code_identical']=re.findall(r'```[^\n]*\n(.*?)\n```',texts['en'],re.S)==re.findall(r'```[^\n]*\n(.*?)\n```',texts['pt-br'],re.S)
sys.path.insert(0,str(P.parents[2]/'agent/tools'));import go_source_ast
example=re.search(r'```go\n(.*?)\n```',texts['en'],re.S).group(1)+'\n'
syntax=go_source_ast.run(json.dumps({'source':example,'path':'illustrative-example.go','selectors':['main']}).encode())
checks['example_static_parser_only']=syntax['source_executed']is False and syntax['units'][0]['selector']=='main'
checks['context_budget']=ledger['source_quote_bytes']<=24576
checks['no_training_or_publication_promotion']=ledger['owner_approved']is False and ledger['training_gold']is False and ledger['training_exclusion']is True
report={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_checks_pass':all(checks.values()),'check_count':len(checks),'checks':checks,
        'example_parser_result':syntax,'example_compiled':False,'example_executed':False,
        'static_package_binding_checked':True,'full_prose_entailment_certified':False,'general_translation_quality_certified':False,
        'agent_review_findings':['12source statements plus1staticbinding claim;7FAQanswersderivative.','Firstcandidateembeddinginference required package-level static evidence;now7declaringreceiversverified.','Privateexportscopeabsence is not sourceabsence.','Error-pathfieldassignment and copying routes remain explicit;no concurrency/runtimeguarantee.']}
with(P/'go-geom-chapter-verification-v2.json').open('x')as stream:json.dump(report,stream,indent=2)
print(json.dumps({'all_checks_pass':report['all_checks_pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v]}))
