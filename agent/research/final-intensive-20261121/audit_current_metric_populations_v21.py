import json,hashlib,datetime
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[2];sha=lambda b:hashlib.sha256(b).hexdigest();old=p/'current-metric-population-audit-results-v20.json';d=json.loads(old.read_text())
for e in d['source_evidence']:assert sha((root/e['path']).read_bytes())==e['sha256']
rp=p/'agent-contracts-dated-complete-review-v2.json';r=json.loads(rp.read_text());assert r['status']=='TECHNICALLY_ACCEPTED_INTERNAL_DATED_FULL_CHAPTER' and r['G9']['status']=='PASS'
for doc in r['documents']:assert sha((root/doc['path']).read_bytes())==doc['sha256']
d.update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),extends={'path':str(old.relative_to(root)),'sha256':sha(old.read_bytes())},internal_agent_chapter_accounting_separate={'candidate_pair_count':1,'selected_version':'dated-fullchapter-v2','technical_status':'TECHNICALLY_ACCEPTED','receipt':{'path':str(rp.relative_to(root)),'sha256':sha(rp.read_bytes())},'preserved_original_and_v1':'INCONCLUSIVE_TEMPORAL_OR_POPULATION_WORDING','authorship':'Codex-authored provenance/population clarification, historical source/review inspection','neural_contribution':False,'manual_composite_groups':37,'independent_atomic_claim_denominator':None,'independent_human_review':False,'owner_approved':False,'publication_authorized':False,'training_gold':False,'training_eligible':False,'not_added_to_public_chapter_or_neural_rate':True},population_refresh_kind='Public41/35/1/5andpriorcontrols retained from hashedv20, newinternalchapter1separate; no unchangedexperimentrerun ornewgeneralrates.')
d['source_evidence'].append({'path':str(rp.relative_to(root)),'sha256':sha(rp.read_bytes())})
with (p/'current-metric-population-audit-results-v21.json').open('x') as f:json.dump(d,f,indent=2);f.write('\n')
print(json.dumps({'public_versions':d['chapter_version_accounting']['versioned_pair_count'],'internal_helper':1,'additional_internal_fullchapter':1,'new_model_calls':0}))
