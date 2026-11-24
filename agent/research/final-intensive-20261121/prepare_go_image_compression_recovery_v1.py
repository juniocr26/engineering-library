import json,hashlib,datetime
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[2];d=json.loads((p/'go-image-compression-attribution-review-v1.json').read_text());dataset=root/'agent/research/documentation-intelligence-20261119/datasets/v10/chapter-deltas.jsonl';paths=set();docs=[]
for line in dataset.read_text().splitlines():
 r=json.loads(line)
 if r.get('canonical_record_id') not in ['chapter-delta:go-image-compression-flow:en','chapter-delta:go-image-compression-flow:pt-br']:continue
 for field in ['candidate_documentation_ref','technical_review_ref','source_evidence_ref']:paths.add(r[field]['path'])
 docs.append({'language':r['language'],'path':r['candidate_documentation_ref']['path'],'sha256':r['candidate_documentation_ref']['sha256']})
for w in d['witnesses']:paths.add(w['capture_path'])
paths.add(str(dataset.relative_to(root)));edges=[]
for name in sorted(paths):edges.append({'path':name,'sha256':hashlib.sha256((root/name).read_bytes()).hexdigest()})
with (p/'remaining-chapters-recovery-dependencies-v17.json').open('x') as f:json.dump({'purpose':'Exact public original compression target and trace closure; no original edits','dependencies':edges},f,indent=2);f.write('\n')
manifest={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'external_dependencies':edges,'original_documents':docs,'changes':d['changes'],'witnesses':[{k:w[k] for k in ['id','response_path','response_sha256','request_path','request_sha256']} for w in d['witnesses']],'source_files':json.loads((p/'go-image-compression-source-acquisition-v1.json').read_text())['records'],'review':'go-image-compression-corrected-complete-review-v2.json','scope':'Finite identity/exact replacement/source-attribution replay, not general semantic validation or target execution.'}
with (p/'go-image-compression-recovery-manifest-v1.json').open('x') as f:json.dump(manifest,f,indent=2);f.write('\n')
print('External recovery edges',len(edges))
