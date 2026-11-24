import json
from pathlib import Path
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2]
common='''

### Final intensive progress 026 — public original target reviewed without label promotion

The exact original dataset EN/PT Go Image Optimizer animation chapter was read in full with immutable source/review references, then compared to fresh read-only Git objects at48476de6e4450294b7769ab7af90805100bb21b5. Sixteen source/context/license/module files were acquired without executing upstream code/tests. Selected compression/resize callers, configurable aggregate fallback, fixed resize constant, error declarations and integration test assertions were inspected. Selected source guards, strict aggregate expression, positive divisor order, distinct budgets and threeFAQ meanings are supported within the chapter’s stated static scope. Source comments and test assertions are not runtime results.

`go-image-animation-original-target-review-v1.json` records seven composite source groups and six adverse challenges, not independent atomic model observations. One useful negative challenge is contradicted by actual callers: animation validation is not universally before decoded-frame allocation; selected GIF/AVIF compression paths call DecodeAll earlier. The chapter appropriately does not assert that global guarantee. Existing local source correspondence does not establish decoder memory safety.

No current technical acceptance is granted: historical model failure attributions still require exact request/response witnesses (G2/G4 INCONCLUSIVE), and the newly acquired closure awaits operational recovery (G9 INCONCLUSIVE). Historical VERIFIED_WITH_LIMITATIONS label and original bytes remain unchanged. No new accepted-pair count, trainingGold, publication approval, optimizer update or local model call. Next action locates the exact historical witnesses rather than treating prior summary labels as proof.
'''
j=p/'root-report-bundle-progress-026';prepare(root,j,{n:common.encode() for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
with (p/'root-report-append-receipt-v26.json').open('x') as f:json.dump({'bundle':str(j.relative_to(root)),'outcome':out},f,indent=2);f.write('\n')
print(out['status'])
