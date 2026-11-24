import json,hashlib,datetime
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[2];review=json.loads((p/'go-image-historical-attribution-review-v1.json').read_text());change=json.loads((p/'go-image-animation-attribution-candidate-change-v1.json').read_text());old=json.loads((p/'go-image-animation-original-target-review-v1.json').read_text());paths=set()
for edge in old['bound_original_references']:paths.add(edge['path'])
for item in review['records']:
 for kind in ('request','response'):paths.add(item[kind]['path'])
paths.add('agent/research/acceptance-calibration-20261121/original-public-chapter-provenance-capture-results-v3.json')
paths.add('.local-backups/continuation-20261119/go-image-results.jsonl')
deps=[]
for name in sorted(paths):
 f=root/name;deps.append({'path':name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
with (p/'remaining-chapters-recovery-dependencies-v16.json').open('x') as f:json.dump({'purpose':'Exact original dataset target, prior model request/response and trace attribution recovery; public Go Image Optimizer only','dependencies':deps},f,indent=2);f.write('\n')
manifest={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'external_dependencies':deps,'candidate_documents':change['records'],'current_review_status':'PENDING_G9_OPERATIONAL_CHECKPOINT','scope':'Hash-bound finite recovery and exact attribution comparisons; not semantic verifier, external app execution, effective server model digest or original HTTP wire encoding.'}
with (p/'go-image-animation-candidate-recovery-manifest-v1.json').open('x') as f:json.dump(manifest,f,indent=2);f.write('\n')
print('Bound external dependency count',len(deps))
