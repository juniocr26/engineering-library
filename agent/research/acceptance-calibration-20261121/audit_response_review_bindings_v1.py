"""Validate byte-level links among original responses, reviews and source snapshots."""
from pathlib import Path
import json,hashlib,datetime,re
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sha=lambda b:hashlib.sha256(b).hexdigest();checks=[];seen=set();unresolved=[];reviewfiles=[]
def check(owner,field,target,expected):
 key=(str(owner),field,str(target),expected)
 if key in seen:return
 seen.add(key);actual=sha(target.read_bytes());checks.append({'review_or_record':str(owner.relative_to(ROOT)),'field':field,'target':str(target.relative_to(ROOT)),'expected_sha256':expected,'actual_sha256':actual,'matches':actual==expected})
def resolve(value,owner):
 if not isinstance(value,str):return None
 path=Path(value)
 if path.is_absolute():
  if path.is_relative_to(ROOT) and path.is_file():return path
  return None
 for target in [ROOT/path,P/path,owner.parent/path]:
  if target.is_file():return target
 return None
# Every returned response's exact content and reported model identity.
responses=[]
for f in sorted(P.rglob('outcome.json')):
 o=json.loads(f.read_text())
 if o.get('exit_code')!=0:continue
 folder=f.parent;raw=json.loads((folder/'raw-response.json').read_bytes());content=(folder/'model-content.txt').read_bytes();request=json.loads((folder/'request.json').read_bytes());matches=raw['message']['content'].encode()==content and raw['model']==request['model'];responses.append({'folder':str(folder.relative_to(ROOT)),'exact_HTTP_message_content_bytes_preserved':raw['message']['content'].encode()==content,'reported_model_matches_request':raw['model']==request['model'],'raw_sha256':sha((folder/'raw-response.json').read_bytes()),'content_sha256':sha(content),'matches':matches})
for f in sorted(P.rglob('*review*.json')):
 if not f.is_file():continue
 try:r=json.loads(f.read_bytes())
 except (ValueError,TypeError):continue
 if not isinstance(r,dict):continue
 reviewfiles.append(str(f.relative_to(ROOT)))
 if (f.parent/'model-content.txt').is_file():
  for key in ['content_sha256','model_content_sha256','original_content_sha256','raw_output_sha256']:
   if key in r:check(f,key,f.parent/'model-content.txt',r[key])
  for key,name in [('raw_response_sha256','raw-response.json'),('request_sha256','request.json')]:
   if key in r:check(f,key,f.parent/name,r[key])
  if 'extends_exact_v1_sha256' in r:check(f,'extends_exact_v1_sha256',f.parent/'semantic-review-v1.json',r['extends_exact_v1_sha256'])
 def walk(node,location='$'):
  if isinstance(node,dict):
   for pathkey,hashkey in [('semantic_review','semantic_review_sha256'),('source_semantic_review','source_semantic_review_sha256'),('rendered_artifact','rendered_artifact_sha256'),('source_snapshot','source_sha256'),('path','sha256')]:
    value=node.get(hashkey);path=node.get(pathkey)
    if isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) and isinstance(path,str):
     target=resolve(path,f)
     if target is not None:check(f,location+'.'+hashkey,target,value)
     else:unresolved.append({'review':str(f.relative_to(ROOT)),'field':location+'.'+pathkey,'path_literal':path,'classification':'Notverifiedbydirectworkspacepathprofile; may be repository-relative/sourcecitation, notautomaticallymissingorfalse.'})
   for k,v in node.items():walk(v,location+'.'+k)
  elif isinstance(node,list):
   for i,v in enumerate(node):walk(v,location+'['+str(i)+']')
 walk(r)
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'returned_response_bindings':responses,'returned_responses_checked':len(responses),'all_returned_HTTP_content_and_model_bindings_match':all(x['matches'] for x in responses),'review_files_scanned':len(reviewfiles),'review_file_paths':reviewfiles,'explicit_hash_bindings_checked':len(checks),'hash_binding_checks':checks,'all_explicit_resolved_hash_bindings_match':all(x['matches'] for x in checks),'unresolved_by_profile':unresolved,'scope':'Byteidentity and declaredmodel/pathhashlinks only. Not semantictruth, exhaustiveclaimreview, ownerapproval orfulltransitiveprovenanceclosure. Multipleversions/fields/quotes are duplicateevidenceedges, not independentaccuracyobservations. Originalpartialinvalidoutputs remain unchanged.','known_protocol_metadata_correction':'render-refusal-protocol-provenance-correction-v1.json; PoldrendererLliteralretainedandcorrectedinsupplement; no acceptance/referencechange.','production_changes':0,'gold':0,'optimizer_updates':0}
with (P/'response-review-source-binding-audit-v1.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({k:result[k] for k in ['returned_responses_checked','all_returned_HTTP_content_and_model_bindings_match','review_files_scanned','explicit_hash_bindings_checked','all_explicit_resolved_hash_bindings_match']},indent=2));print('mismatches',[(x['review_or_record'],x['field']) for x in checks if not x['matches']]);print('unresolvedpathprofile',len(unresolved))
