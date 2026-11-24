import argparse,json,hashlib,collections
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True,type=Path);ROOT=ap.parse_args().root.resolve();P=ROOT/'agent/research/final-intensive-20261121';sha=lambda b:hashlib.sha256(b).hexdigest();proto=json.loads((P/'owner-review-batch-identity-diversity-protocol-v1.json').read_bytes());batch=ROOT/proto['batch']['path'];assert sha(batch.read_bytes())==proto['batch']['sha256'];b=json.loads(batch.read_bytes());audit=json.loads((P/'owner-review-batch-identity-diversity-results-v3.json').read_bytes());assert sha((P/'owner-review-batch-identity-diversity-protocol-v1.json').read_bytes())==audit['protocol_sha256']
for e in audit['dependencies']:assert sha((ROOT/e['path']).read_bytes())==e['sha256']
for e in json.loads((P/'remaining-chapters-recovery-dependencies-v42.json').read_bytes())['dependencies']:assert sha((ROOT/e['path']).read_bytes())==e['sha256']
public=b['public_manual_pairs']+b['supplemental_technically_accepted_pairs'];internal=b['internal_owner_review_only'];assert len(public)==28 and len(internal)==2
allhashes=[];pairkeys=[];families=set()
for row in public+internal:
 assert all(row[k] is False for k in ['owner_approved','publication_approved','training_gold_approved','training_eligible']);hashes=[];langs=[]
 for e in row['documents']:
  assert sha((ROOT/e['path']).read_bytes())==e['sha256'];hashes.append(e['sha256']);allhashes.append(e['sha256']);lang=e.get('language',Path(e['path']).stem).lower().removesuffix('.md');langs.append(lang)
 assert sorted(langs)==['en','pt-br'];pairkeys.append(tuple(sorted(hashes)))
 if row in public:families.add(row['source_family'])
assert len(allhashes)==len(set(allhashes))==60 and len(pairkeys)==len(set(pairkeys))==30 and len(families)==15
for ref in b['preserved_failed_original_targets']:
 raw=(ROOT/ref['path']).read_bytes();assert sha(raw)==ref['sha256'];old=json.loads(raw);assert all(e['sha256'] not in allhashes for e in old['documents'])
assert audit['public_declared_family_labels']==15 and audit['certified_independent_families']==0 and audit['new_semantic_gate_verdicts']==0 and not audit['training_approval']
assert audit['near_duplicate_triage']['comparisons']==378 and audit['near_duplicate_triage']['threshold']==0.6 and not audit['near_duplicate_triage']['flags']
print(json.dumps({'status':'PASS_EXACT_OWNER_REVIEW_TARGET_AND_FAMILY_LABEL_RECOVERY','public_pairs':28,'internal_pairs':2,'unique_documents':60,'unique_pairs':30,'public_declared_family_labels':15,'certified_independent_families':0,'five_failed_original_pairs_excluded':True,'new_semantic_or_training_approval':False,'current_model_calls':0}))
