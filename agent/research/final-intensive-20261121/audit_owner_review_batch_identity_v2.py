from pathlib import Path
import json,hashlib,datetime,collections,itertools,re,unicodedata
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sha=lambda b:hashlib.sha256(b).hexdigest();proto=P/'owner-review-batch-identity-diversity-protocol-v1.json';pr=json.loads(proto.read_bytes());batch=ROOT/pr['batch']['path'];assert sha(batch.read_bytes())==pr['batch']['sha256'];d=json.loads(batch.read_bytes());groups=[('PUBLIC',d['public_manual_pairs']+d['supplemental_technically_accepted_pairs']),('INTERNAL',d['internal_owner_review_only'])];assert len(groups[0][1])==28 and len(groups[1][1])==2
rows=[];doc_hashes=collections.defaultdict(list);pair_hashes=collections.defaultdict(list);normalized=collections.defaultdict(list);families=collections.defaultdict(list);english={};notices=collections.Counter();selected=set();deps={}
def bind(e):
 f=ROOT/e['path'];raw=f.read_bytes();assert sha(raw)==e['sha256'];deps[e['path']]=e['sha256'];return raw
for visibility,records in groups:
 for r in records:
  hashes=[];documents=[]
  for doc in r['documents']:
   raw=bind(doc);selected.add(doc['sha256']);hashes.append(doc['sha256']);doc_hashes[doc['sha256']].append(r['id']);text=raw.decode();norm=sha(' '.join(unicodedata.normalize('NFC',text).split()).encode());normalized[norm].append({'pair':r['id'],'path':doc['path']});language=doc.get('language',Path(doc['path']).stem).lower();assert language in ['en','pt-br'];documents.append({'language':language,'path':doc['path'],'sha256':doc['sha256'],'normalized_sha256':norm,'bytes':len(raw)})
   if visibility=='PUBLIC' and language=='en':english[r['id']]=text
  assert len(hashes)==2;pair_hashes[tuple(sorted(hashes))].append(r['id']);family=r.get('source_family','INTERNAL_ENGINEERING_LIBRARY');families[family].append(r['id']);receipt=r.get('gate_receipt',r.get('receipt'));bind(receipt);notice=r.get('license_notice',r.get('rights_notice'));bind(notice);notices[notice.get('identified_notice','UNSPECIFIED')]+=1
  flags={k:r.get(k,'MISSING_UNKNOWN') for k in ['owner_approved','publication_approved','training_gold_approved','training_eligible']};assert all(v is False for v in flags.values())
  rows.append({'id':r['id'],'visibility':visibility,'declared_source_family':family,'documents':documents,'gate_receipt':receipt,'rights_notice':notice,'flags':flags,'technical_status':r['technical_status'],'independent_evaluation_approval_inferred':False})
failed=[]
for e in d['preserved_failed_original_targets']:
 old=json.loads(bind(e));docs=old['documents'];overlap=[x['sha256'] for x in docs if x['sha256'] in selected];assert not overlap
 for doc in docs:bind(doc)
 failed.append({'review':e,'original_documents':docs,'selected_hash_overlap':overlap})
def shingles(text):
 tokens=re.findall(r'\w+|[^\w\s]',text.casefold());return {tuple(tokens[i:i+5]) for i in range(len(tokens)-4)}
sets={k:shingles(t) for k,t in english.items()};similarities=[]
for a,b in itertools.combinations(sorted(sets),2):
 union=sets[a]|sets[b];score=len(sets[a]&sets[b])/len(union) if union else 0;similarities.append({'a':a,'b':b,'five_token_shingle_Jaccard':score,'review_signal':score>=0.6})
assert len(english)==28 and len(similarities)==378
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':sha(proto.read_bytes()),'rows':rows,'public_pairs':28,'internal_pairs':2,'selected_documents':sum(len(r['documents']) for r in rows),'unique_document_hashes':len(doc_hashes),'unique_pair_hash_sets':len(pair_hashes),'exact_document_duplicate_groups':[{'sha256':k,'pairs':v} for k,v in doc_hashes.items() if len(v)>1],'exact_pair_duplicate_groups':[v for v in pair_hashes.values() if len(v)>1],'normalized_text_duplicate_groups':[v for v in normalized.values() if len(v)>1],'declared_family_label_groups':dict(families),'public_declared_family_labels':len({r['declared_source_family'] for r in rows if r['visibility']=='PUBLIC'}),'certified_independent_families':0,'rights_notice_label_counts':dict(notices),'failed_original_exclusion':failed,'near_duplicate_triage':{'comparisons':378,'threshold':0.6,'flags':[r for r in similarities if r['review_signal']],'top10':sorted(similarities,key=lambda x:x['five_token_shingle_Jaccard'],reverse=True)[:10],'no_semantic_or_independence_certification':True},'dependencies':[{'path':k,'sha256':v} for k,v in sorted(deps.items())],'all_owner_publication_Gold_training_flags_false':True,'originals_modified':False,'new_model_calls':0,'new_semantic_gate_verdicts':0,'training_approval':False}
with (P/'owner-review-batch-identity-diversity-results-v2.json').open('x') as f:json.dump(out,f,indent=2,ensure_ascii=False);f.write('\n')
print(json.dumps({k:out[k] for k in ['public_pairs','internal_pairs','selected_documents','unique_document_hashes','unique_pair_hash_sets','public_declared_family_labels','certified_independent_families','exact_document_duplicate_groups','normalized_text_duplicate_groups','rights_notice_label_counts']}));print('near_flags',len(out['near_duplicate_triage']['flags']),'top_similarity',out['near_duplicate_triage']['top10'][0]['five_token_shingle_Jaccard'])
