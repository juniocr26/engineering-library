"""New two-condition exact-copy probe; not a retry of a rejected documentation task."""
import datetime,hashlib,importlib.util,json,os,time
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];OUT=P/'quoted-code-format-probe-v1';T=ROOT/'.local-backups/documentation-intelligence-20261119/http_over_existing_ollama.py';spec=importlib.util.spec_from_file_location('quoted_code_existing_transport',T);transport=importlib.util.module_from_spec(spec);spec.loader.exec_module(transport)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def save(path,value):
 with path.open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
def unique(pairs):
 r={}
 for k,v in pairs:
  if k in r:raise ValueError('duplicate JSON key')
  r[k]=v
 return r
def main():
 OUT.mkdir(exist_ok=False);sample={'plain':'func Add(a, b int) int { return a + b }\n','quoted':'package example\n\nimport "errors"\n\nfunc Failure() error {\n    return errors.New("owned failure")\n}\n','unicode':'const label = "ação"\n'};expected={lang:sample.copy()for lang in ['en','pt-br']}
 item={'type':'object','properties':{key:{'type':'string'}for key in sample},'required':list(sample),'additionalProperties':False};schema={'type':'object','properties':{'en':item,'pt-br':item},'required':['en','pt-br'],'additionalProperties':False}
 messages=[{'role':'system','content':'Perform exact copying only. Return the exact JSON object supplied by the user, without Markdown fences or explanation. Preserve every character inside each string value, including quotes, newlines, indentation and Unicode. Code values intentionally remain identical under en and pt-br; do not translate, correct or execute any code. JSON encoding may escape characters, but decoded string values must be exact.'},{'role':'user','content':json.dumps(expected,ensure_ascii=False)}]
 options={'temperature':0,'seed':42,'num_ctx':4096,'num_predict':800,'num_thread':4};base={'model':'llama3.2:3b','stream':False,'keep_alive':0,'options':options,'messages':messages};digest='a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72'
 protocol={'at':now(),'status':'FROZEN_BEFORE_BOTH_NEW_FORMAT_CONDITIONS','hypothesis':'The constrained API format might make quoted Go code hard to reproduce. If the small constrained task copies all quoted and Unicode values exactly, a general inability of that format to represent escaped imports is falsified; this does not explain long chapter failure or improve semantic accuracy.','motivation':'Several prior chapter responses stopped normally at import lines; original outputs/rejections are immutable.','task':'OWNED_EXACT_CODE_STRING_COPY_NOT_DOCUMENTATION_GENERATION','conditions_order':['unconstrained-api-format','schema-constrained-api-format'],'maximum_calls':2,'maximum_calls_per_condition':1,'no_retries':True,'same_messages_sha256':hashlib.sha256(canonical(messages)).hexdigest(),'same_options':options,'only_request_factor_changed':'format property absent versus exact schema object; messages/options/model/keep_alive otherwise identical.','expected_decoded_object':expected,'schema':schema,'model':base['model'],'digest':digest,'resource_budget':{'maximum_output_tokens_per_call':800,'context_tokens':4096,'maximum_request_bytes':8192,'http_timeout_seconds':900,'num_thread':4,'keep_alive':0},'interpretation_limits':['Two calls in fixed order, no repeat/randomization or independent neural benchmark.','Exact copying is not source comprehension, semantic translation or factual chapter generation.','Different task from the rejected chapters; no causal chapter-quality gain claim.','All code strings are owned synthetic data and will not be executed.'],'owner_approved':False,'training_gold':False,'training_excluded':True,'training_steps':0,'publication':False};save(OUT/'protocol.json',protocol)
 tags=json.loads(transport.request('/api/tags',timeout=15));models=[m for m in tags['models']if m['name']==base['model']];assert len(models)==1 and models[0]['digest']==digest;save(OUT/'model-observation.json',{'at':now(),'model':base['model'],'digest':digest});rows=[]
 for condition in protocol['conditions_order']:
  folder=OUT/condition;folder.mkdir();request=json.loads(json.dumps(base));
  if condition=='schema-constrained-api-format':request['format']=schema
  assert canonical({k:v for k,v in request.items()if k!='format'})==canonical(base);payload=json.dumps(request,ensure_ascii=False).encode();assert len(payload)<=8192;save(folder/'request.json',request);save(folder/'dispatch.json',{'at':now(),'status':'DISPATCHING_DO_NOT_RETRY','request_sha256':hashlib.sha256(payload).hexdigest(),'bytes':len(payload)});start=time.monotonic()
  try:
   raw=transport.request('/api/chat',payload,timeout=900)
   with(folder/'response.json').open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
   response=json.loads(raw);result={'at':now(),'condition':condition,'wall_seconds':time.monotonic()-start,'model_seconds':response.get('total_duration',0)/1e9,'done_reason':response.get('done_reason'),'generated_tokens':response.get('eval_count'),'prompt_tokens':response.get('prompt_eval_count'),'response_sha256':hashlib.sha256(raw).hexdigest(),'parse_status':'PENDING'}
   try:
    packet=json.loads(response['message']['content'],object_pairs_hook=unique);checks={lang+':'+key:type(packet)is dict and type(packet.get(lang))is dict and packet[lang].get(key)==value for lang,values in expected.items()for key,value in values.items()};result.update(parse_status='VALID_JSON',field_checks=checks,exact_decoded_object=packet==expected,exact_fields=sum(checks.values()),fields=len(checks))
   except (ValueError,KeyError,TypeError)as error:result.update(parse_status='INVALID_OR_UNEXPECTED_JSON',parse_error=str(error)[:600],exact_decoded_object=False,exact_fields=0,fields=6)
   save(folder/'outcome.json',result);rows.append(result);print(json.dumps({'condition':condition,'exact_fields':result['exact_fields'],'fields':6,'done_reason':result['done_reason']}),flush=True)
  except Exception as error:
   result={'at':now(),'condition':condition,'status':'UNCERTAIN_NO_RETRY','wall_seconds':time.monotonic()-start,'error':str(error)[:1000]};save(folder/'error.json',result);rows.append(result)
 save(OUT/'comparison.json',{'at':now(),'rows':rows,'same_prompt_and_options_verified':True,'requested_condition_calls':2,'source_or_code_executed':False,'training_gold':False,'owner_approved':False,'no_chapter_rejection_reversed':True,'interpretation_requires_review':True})
if __name__=='__main__':main()
