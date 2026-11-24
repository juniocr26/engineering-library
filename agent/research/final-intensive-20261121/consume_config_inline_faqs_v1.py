import argparse,json,hashlib
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);a=ap.parse_args();root=a.root.resolve();p=root/'agent/research/final-intensive-20261121';result=json.loads((p/'go-image-config-inline-faq-review-results-v1.json').read_text());sha=lambda raw:hashlib.sha256(raw).hexdigest()
assert sha((p/'go-image-config-inline-faq-review-protocol-v1.json').read_bytes())==result['protocol_sha256']
for edge in result['external_dependency_edges']:assert sha((root/edge['path']).read_bytes())==edge['sha256']
for edge in result['source_edges'].values():assert sha((root/edge['saved_path']).read_bytes())==edge['sha256']
for row in result['records']:
 line=(root/row['file']).read_bytes().splitlines()[row['line']-1];assert sha(line)==row['raw_record_sha256'];original=json.loads(line);assert original['question']==row['question'] and original['answer']==row['answer'];text=(root/row['parent_document_ref']['path']).read_text();tail=text.split('<!-- reading-section: faq:'+row['question_identity'][1]+' -->',1)[1].split('<!-- reading-section: faq:',1)[0].strip();heading,*body=tail.splitlines();assert heading=='### '+row['question'] and '\n'.join(body).strip()==row['answer'];assert original['owner_approved'] is False and original['training_gold'] is False and original['training_use_approved'] is False
for check in result['physical_quote_checks']:
 edge=result['source_edges'][check['source_path']];data=(root/edge['saved_path']).read_bytes();quote=b''.join(data.splitlines(keepends=True)[check['lines'][0]-1:check['lines'][1]]);assert sha(quote)==check['exact_quote_sha256']
parent=result['parent_technical_review'];assert sha((root/parent['path']).read_bytes())==parent['sha256'];assert len(result['records'])==6
print(json.dumps({'status':'PASS_EXACT_INLINE_FAQ_BINDING_AND_SOURCE_REPLAY','entries':6,'correlated_bilingual_pairs':3,'physical_quotes_including_translation_reuse':len(result['physical_quote_checks']),'unique_quote_spans':result['unique_quote_spans'],'general_semantic_verification':False,'training_gold':0,'model_calls':0}))
