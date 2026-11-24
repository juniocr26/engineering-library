import json,hashlib,re,collections,datetime
from pathlib import Path
P=Path(__file__).parent
sha=lambda b:hashlib.sha256(b).hexdigest()
pre=P/'dataset-faq-row-level-preflight-v1.json'
a=json.loads(pre.read_text()); results=[]; dependencies={}; pairs=collections.defaultdict(list)
for allowed in a['allowed_rows']:
 raw=Path(allowed['file']).read_bytes().splitlines()[allowed['line']-1]
 assert sha(raw)==allowed['row_sha256']
 r=json.loads(raw); checks={}; blobs={}
 for key in ['document_ref','question_specific_claim_alignment_ref','source_evidence_ref','technical_review_ref']:
  ref=r[key]; data=Path(ref['path']).read_bytes(); actual=sha(data)
  checks[key+'_hash']=actual==ref['sha256']; dependencies[ref['path']]=actual; blobs[key]=data
 doc=blobs['document_ref'].decode(); alignment=json.loads(blobs['question_specific_claim_alignment_ref'])
 qid=r['question_identity'][1]; lang=r['language']; marker='<!-- reading-section: faq:'+qid+' -->'
 checks['single_stable_section']=doc.count(marker)==1
 section=doc.split(marker,1)[1] if checks['single_stable_section'] else ''
 section=re.split(r'<!-- reading-section:|\n## ',section,maxsplit=1)[0]
 match=re.match(r'\s*### ([^\n]+)\n+(.*)',section,re.S)
 checks['section_question_exact']=bool(match and match[1].strip()==r['question'])
 checks['section_answer_exact']=bool(match and match[2].strip()==r['answer'].strip())
 checks['canonical_identity']=r['canonical_reader_key']=='section:faq:'+qid and r['canonical_record_id']==allowed['id'] and r['claim_alignment_record_id']==':'.join(r['question_identity'])
 checks['alignment_identity']=alignment.get('id')==r['claim_alignment_record_id']
 ap=alignment.get('faq_pair',{}).get(lang,{})
 checks['alignment_question_exact']=ap.get('question')==r['question']
 checks['alignment_answer_exact']=ap.get('answer_and_trailing_context')==r['answer']
 checks['alignment_document_hash']=alignment.get('document_hashes',{}).get(lang)==r['document_ref']['sha256']
 checks['assertion_matches_alignment']=alignment.get('source_backed_assertion')==r['source_backed_assertion']
 checks['scope_limit_matches_alignment']=alignment.get('explicit_scope_limit')==r['explicit_scope_limit']
 witnesses=[]
 for evidence in alignment.get('evidence',[]):
  source=evidence.get('frozen_source'); w={'path':source}
  if source and Path(source).is_file():
   data=Path(source).read_bytes(); dependencies[source]=sha(data)
   w['full_hash_match']=sha(data)==evidence.get('full_file_sha256')
   quote=''.join(data.decode().splitlines(keepends=True)[evidence['first_line']-1:evidence['last_line']])
   w['physical_quote_exact']=quote==evidence.get('quote')
   w['quote_hash_match']=sha(evidence.get('quote','').encode())==evidence.get('quote_sha256')
  else:w['unresolved']=True
  witnesses.append(w)
 checks['physical_witnesses_present']=bool(witnesses)
 checks['physical_witnesses_exact']=bool(witnesses) and all(w.get('full_hash_match') and w.get('physical_quote_exact') and w.get('quote_hash_match') for w in witnesses)
 checks['all_approval_and_consumption_flags_false']=all(r[k] is False for k in ['owner_approved','training_gold','training_use_approved','automatic_literal_faq_engine_admitted','automatic_inference_consumer','automatic_trainer_consumer'])
 pairs[tuple(r['question_identity'])].append(lang)
 results.append({**allowed,'language':lang,'checks':checks,'witnesses':witnesses,'status':'BOUND_ROW_TEXT_AND_SOURCE_WITNESSES' if all(checks.values()) else 'REQUIRES_BINDING_REVIEW','semantic_support_verdict':'NOT_INFERRED_FROM_TEXT_HASH_OR_PARENT_ACCEPTANCE'})
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'role':'ROW_TEXT_IDENTITY_AND_PHYSICAL_WITNESS_AUDIT_NOT_SEMANTIC_OR_GOLD_CERTIFICATION','preflight_sha256':sha(pre.read_bytes()),'rows':results,'counts':dict(collections.Counter(r['status'] for r in results)),'check_failures':dict(collections.Counter(k for r in results for k,v in r['checks'].items() if not v)),'identity_pairs':len(pairs),'complete_en_pt_identity_pairs':sum(sorted(v)==['en','pt-br'] for v in pairs.values()),'dependencies':[{'path':k,'sha256':v} for k,v in sorted(dependencies.items())],'private_rows_decoded':0,'original_rows_modified':0,'model_calls':0,'training_approval_granted':False}
(P/'dataset-faq-row-bindings-results-v1.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['rows','dependencies']},ensure_ascii=False))
