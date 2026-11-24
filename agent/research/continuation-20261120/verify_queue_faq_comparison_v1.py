import datetime,hashlib,json,re
from pathlib import Path
P=Path(__file__).resolve().parent;out=P/'queue-model-faq-v1';protocol=json.loads((out/'protocol.json').read_text());request=json.loads((out/'request.json').read_text());prompt=json.loads(request['messages'][1]['content']);path=P/'queue-deterministic-faq-v1.json';candidate=json.loads(path.read_text());ledger=json.loads((P/'queue-faq-ledger-v1.json').read_text());checks={}

def schema_check(value,schema,at='$'):
 errors=[];kind=schema['type']
 if kind=='object':
  if type(value)is not dict:return [at+':not object']
  for field in schema['required']:
   if field not in value:errors.append(at+':missing '+field)
  if schema.get('additionalProperties')is False and not set(value)<=set(schema['properties']):errors.append(at+':extra field')
  for key,item in value.items():
   if key in schema['properties']:errors+=schema_check(item,schema['properties'][key],at+'.'+key)
 elif kind=='array':
  if type(value)is not list:return [at+':not array']
  if not schema.get('minItems',0)<=len(value)<=schema.get('maxItems',10**9):errors.append(at+':array length')
  for index,item in enumerate(value):errors+=schema_check(item,schema['items'],at+'['+str(index)+']')
 elif kind=='string':
  if type(value)is not str:return [at+':not string']
  if'enum'in schema and value not in schema['enum']:errors.append(at+':enum differs')
 else:raise ValueError('unsupported trusted schema type')
 return errors

errors=schema_check(candidate,protocol['schema']);checks['exact_model_schema']=not errors;ids=[row['id']for row in candidate['faq']];checks['six_unique_requested_ids']=len(ids)==6 and len(set(ids))==6 and set(ids)==set(protocol['requested_ids'])
for identity,unit in prompt['source_evidence'].items():
 file=P/'new-public-sources-v1'/unit['repository'].replace('/','--')/unit['revision']/unit['path'];raw=file.read_bytes();quote=''.join(raw.decode().splitlines(keepends=True)[unit['first_line']-1:unit['last_line']]);checks['physical:'+identity]=hashlib.sha256(raw).hexdigest()==unit['source_sha256']and quote==unit['quote']and hashlib.sha256(quote.encode()).hexdigest()==unit['quote_sha256']
for row in candidate['faq']:
 key=row['id'];en=row['en']['question']+'\n'+row['en']['answer'];pt=row['pt-br']['question']+'\n'+row['pt-br']['answer'];checks['paired_inline_code:'+key]=re.findall(r'`([^`]+)`',en)==re.findall(r'`([^`]+)`',pt);checks['paired_numbers:'+key]=re.findall(r'\d+',en)==re.findall(r'\d+',pt);checks['question_specific_ids:'+key]=bool(row['evidence_ids'])and set(row['evidence_ids'])<=set(prompt['source_evidence']);checks['answer_word_bounds:'+key]=all(35<=len(row[lang]['answer'].split())<=55 for lang in ['en','pt-br'])
checks['no_promotion']=ledger['owner_approved']is False and ledger['training_gold']is False and ledger['training_exclusion']is True and ledger['published']is False
cut=json.loads((P/'recovery-delta-receipt-v3.json').read_text());manifest=json.loads((P.parents[2]/cut['input_manifest']['path']).read_text());name='agent/research/continuation-20261120/javascript-queue-review-targets-v1.jsonl';checks['pre_call_fact_targets_unchanged_from_sealed_v3']=hashlib.sha256((P.parents[2]/name).read_bytes()).hexdigest()==manifest['effective_expected_files'][name]['sha256']
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'checks_count':len(checks),'all_pass':all(checks.values()),'candidate_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'model_review_sha256':hashlib.sha256((out/'review.json').read_bytes()).hexdigest(),'model_complete_requested_sets_accepted':0,'model_requested_sets':1,'deterministic_paired_questions_prepared_for_owner_review':6,'deterministic_owner_gold':0,'schema_errors':errors,'full_prose_entailment_or_semantic_equivalence_certified':False,'manual_source_review_author':'Codex; no independent human grader','comparison_limits':ledger['comparison_limits'],'exact_deterministic_wording_authored_after_rejected_output':True,'pre_call_fact_targets_preserved':True,'new_model_calls':0,'source_executed':False}
with(P/'queue-faq-comparison-verification-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'all_pass':record['all_pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'paired_owner_review_candidates':6,'owner_gold':0})
