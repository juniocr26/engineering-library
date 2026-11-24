"""Compare exact target-reference identities, without mutating original rows or labels."""
import json,hashlib,datetime,collections
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[2];sha=lambda b:hashlib.sha256(b).hexdigest()
meta_path=root/'agent/research/acceptance-calibration-20261121/dataset-quality-audit-v1.json';meta=json.loads(meta_path.read_text());audit=json.loads((p/'current-metric-population-audit-results-v14.json').read_text());accepted={}
for pair in audit['chapter_version_accounting']['records']:
 if pair['technical_status']!='TECHNICALLY_ACCEPTED':continue
 for doc in pair['documents']:
  assert sha((root/doc['path']).read_bytes())==doc['sha256']
  accepted.setdefault(doc['sha256'],[]).append({'topic':pair['topic'],'path':doc['path'],'version':pair['version']})
files={};records=[];counts=collections.Counter()
for m in meta['records_metadata']:
 if m['private_excluded']:counts['PRIVATE_EXCLUDED_NOT_PARSED']+=1;continue
 name=m['file']
 if name not in files:
  raw=(root/name).read_bytes();files[name]={'raw':raw,'lines':raw.splitlines(),'sha256':sha(raw)}
 line=files[name]['lines'][m['line']-1];assert sha(line)==m['raw_record_sha256'];row=json.loads(line)
 refs=[]
 for field in ('candidate_documentation_ref','document_ref'):
  edge=row.get(field)
  if isinstance(edge,dict):
   digest=edge.get('sha256');matches=accepted.get(digest,[]);target=root/edge['path']
   assert target.is_file() and sha(target.read_bytes())==digest
   refs.append({'field':field,'path':edge['path'],'original_path':edge.get('original_path'),'sha256':digest,'exact_current_accepted_document_matches':matches})
 status='EXACT_ACCEPTED_DOCUMENT_REFERENCE' if any(r['exact_current_accepted_document_matches'] for r in refs) else ('DIFFERENT_DOCUMENT_REFERENCE' if refs else 'NO_DIRECT_DOCUMENT_REFERENCE_IN_SELECTED_FIELDS')
 counts[status]+=1;records.append({'canonical_record_id':m['id'],'file':name,'line':m['line'],'row_sha256':sha(line),'record_role':m['record_role'],'family':m['family'],'correspondence_status':status,'selected_target_refs':refs,'owner_approved':row.get('owner_approved'),'training_gold':row.get('training_gold'),'training_use_approved':row.get('training_use_approved'),'automatic_trainer_consumer':row.get('automatic_trainer_consumer'),'labels_changed':False})
for name,f in files.items():assert sha((root/name).read_bytes())==f['sha256']
assert len(records)==297 and counts['PRIVATE_EXCLUDED_NOT_PARSED']==8
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':sha((p/'dataset-current-candidate-correspondence-protocol-v1.json').read_bytes()),'original_metadata_receipt_sha256':sha(meta_path.read_bytes()),'current_accepted_chapter_document_hashes':len(accepted),'records':records,'counts':dict(counts),'original_files_verified_unchanged':[{'path':name,'sha256':f['sha256']} for name,f in files.items()],'scope':'Direct candidate_documentation_ref/document_ref identities only, not all indirect graph paths, inline answers, semantic equivalence or whole target bundles.','interpretation':'A current acceptance applies only to bound bytes and frozen scope. Neither a shared family nor even an exact document reference grants training/publication/owner approval to an original record.','source_citation_gap_propagation':'SQLX named-context candidate v2 gap must not be transferred to different sqlx-in-expansion or sqlx-map-argument-binding documents.','original_rows_modified':0,'new_gold':0,'model_calls':0}
with (p/'dataset-current-candidate-correspondence-results-v6.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({'counts':dict(counts),'accepted_document_hashes':len(accepted),'original_files_unchanged':len(files),'new_gold':0}))
