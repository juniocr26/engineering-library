import json
from pathlib import Path
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2]
common='''

### Final intensive progress 027 — exact historical witness reveals attribution error

The bounded witness locator found preserved exact caller/helper requests and raw responses under the prior campaign’s original-public-chapter-provenance-captures-v1. Reading both confirms the caller PT any-versus-none inversion. It also changes the historical chapter assessment: the helper’s first PT fact says strict upper-width menor que, while the original chapter incorrectly links that wording to rejection of nonpositive dimensions. The helper’s second fact actually says zero ou negativo, correctly preserving positivity. The equality defect belongs to the upper bound, not the positivity guard. This is a confirmed imprecision in the original manually corrected target, not a new model run or evidence that all historical source claims fail.

`go-image-historical-attribution-review-v1.json` binds exact request/response hashes and preserves all facts, including three identical helper output facts as repetition rather than independent observations. Model tag is not effective server digest; historical tokens stay historical. The full isolated EN/PT pair in `go-image-animation-attribution-candidate-v1/` changes only the corresponding attribution clause. Exact two-language diff and unchanged diagrams/code are recorded in `go-image-animation-attribution-candidate-change-v1.json`; original document and305dataset row bytes remain intact.

The old label is not silently reclassified or promoted. New corrected pair remains pending complete gate review and actual recovery, with no current accepted-pair count increase. No owner/publication/Gold approval, production or permanent-test edits, new local inference or optimizer update. Campaign continues toward approximately12actualhours.
'''
j=p/'root-report-bundle-progress-027';prepare(root,j,{n:common.encode() for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
with (p/'root-report-append-receipt-v27.json').open('x') as f:json.dump({'bundle':str(j.relative_to(root)),'outcome':out},f,indent=2);f.write('\n')
print(out['status'])
