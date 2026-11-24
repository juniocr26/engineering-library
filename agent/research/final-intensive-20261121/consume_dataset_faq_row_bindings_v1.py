import argparse,json,hashlib,collections,re
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True,type=Path);root=ap.parse_args().root.resolve();p=root/'agent/research/final-intensive-20261121';sha=lambda b:hashlib.sha256(b).hexdigest()
a=json.loads((p/'dataset-faq-row-bindings-results-v1.json').read_bytes());pre=json.loads((p/'dataset-faq-row-level-preflight-v1.json').read_bytes());assert sha((p/'dataset-faq-row-level-preflight-v1.json').read_bytes())==a['preflight_sha256']
for e in json.loads((p/'remaining-chapters-recovery-dependencies-v39.json').read_bytes())['dependencies']:assert sha((root/e['path']).read_bytes())==e['sha256']
for e in json.loads((p/'dataset-faq-row-schema-observations-v1.json').read_bytes())['original_files_hash_verified_unchanged']:assert sha((root/e['path']).read_bytes())==e['sha256']
pairs=collections.defaultdict(list); boundary=[]
for e in pre['allowed_rows']:
 raw=(root/e['file']).read_bytes().splitlines()[e['line']-1];assert sha(raw)==e['row_sha256'];r=json.loads(raw)
 assert r['canonical_record_id']==e['id'];pairs[tuple(r['question_identity'])].append(r['language'])
 for key in ['document_ref','question_specific_claim_alignment_ref','source_evidence_ref','technical_review_ref']:assert sha((root/r[key]['path']).read_bytes())==r[key]['sha256']
 doc=(root/r['document_ref']['path']).read_text();marker='<!-- reading-section: faq:'+r['question_identity'][1]+' -->';assert doc.count(marker)==1
 section=re.split(r'<!-- reading-section:|\n## ',doc.split(marker,1)[1],maxsplit=1)[0];m=re.match(r'\s*### ([^\n]+)\n+(.*)',section,re.S);assert m and m[1].strip()==r['question']
 if m[2].strip()!=r['answer'].strip():boundary.append(e['id'])
 assert all(r[k] is False for k in ['owner_approved','training_gold','training_use_approved','automatic_literal_faq_engine_admitted','automatic_inference_consumer','automatic_trainer_consumer'])
for e in a['dependencies']:assert sha((root/e['path']).read_bytes())==e['sha256']
assert len(pairs)==74 and all(sorted(v)==['en','pt-br'] for v in pairs.values());assert sorted(boundary)==sorted(x['id'] for x in json.loads((p/'dataset-faq-answer-boundary-findings-v1.json').read_bytes())['findings']) and len(boundary)==2
clock=json.loads((p/'next-neural-matched-dimensions-wall-clock-supplement-v1.json').read_bytes());assert clock['execution_status']=='NOT_RUN' and clock['current_model_calls']==0 and clock['clock_policy']['max_requests']==2
print(json.dumps({'status':'PASS_ROW_BINDING_AND_TARGET_BOUNDARY_RECOVERY','rows':148,'EN_PT_pairs':74,'exact_section_answers':146,'trailing_next_section_answers':2,'original_files_hash_verified':7,'private_rows_decoded':0,'model_calls':0,'semantic_acceptance_or_Gold_inferred':False}))
