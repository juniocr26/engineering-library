import json
from pathlib import Path
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2]
common='''

### Final intensive progress 029 — a second original-target attribution corrected

The original complete Go compression-flow EN/PT target, source evidence and actual historical caller/helper trace records were read. Fresh same-revision Git objects bind the application interface/usecase,dispatcher,router,handler,module/license and test sources (tests acquired, not executed). Source context supports empty-input-before-context ordering, discard of result on compressor/context errors, bytes-only interface,8-format dispatch,HEIF content-type argument and explicit router-to-handler composition; written composition does not prove actual runtime injection.

Both historical arms were indeed refused for prose omitting the selected declaration/method name. However, the original chapter incorrectly says both omitted the second context check: actual caller-only EN explicitly says checks again for an error in the context, while helper-arm facts omit context. `go-image-compression-attribution-review-v1.json` preserves exact trace-derived raw response hashes and prepares a separate full EN/PT correction changing that sentence only. Structural rejection must not be misreported as factual falsity of every returned statement. Historical scores/model tags remain historical; no new inference occurred.

`go-image-compression-corrected-complete-review-v2.json` records the bounded full review with G9 stillINCONCLUSIVE. Its v1P7 citation range84–99 omitted the Execute call at82; v2corrects82–99 before any recovery/promotion, retaining v1. New corrected pair is not yet technically accepted or added to accepted counts. Original rows/documents/labels and all external/production/permanent-test files remain unchanged; no owner/publication/Gold approval or training update. Next action operationally restores the complete new source/witness/candidate closure. Campaign active and actual12-hour duration still outstanding.
'''
j=p/'root-report-bundle-progress-029';prepare(root,j,{n:common.encode() for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
with (p/'root-report-append-receipt-v29.json').open('x') as f:json.dump({'bundle':str(j.relative_to(root)),'outcome':out},f,indent=2);f.write('\n')
print(out['status'])
