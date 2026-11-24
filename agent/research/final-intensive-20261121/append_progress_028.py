import json
from pathlib import Path
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2]
common='''

### Final intensive progress 028 — corrected original-target pair technically accepted

Checkpoint021 actually restored2827regularfiles with exact hashes/modes, replayed22finite consumer groups including the exact Go Image Optimizer candidate/source/historical-attribution closure, and reconstructed all four postnote reports exactly. The current review/terminal receipt remain later-cut sidecars, not a self-referential archive claim. `go-image-animation-corrected-complete-review-v2.json` now records all nine gates PASS for the full isolated manually corrected EN/PT chapter. Technical scope is the original ordered-guard/two-budget/FAQ/diagram explanation and its exact historical response attribution; no decoder/runtime/memory guarantee, independent-human approval or effective historical server-model digest is inferred.

`go-image-animation-original-target-review-v2.json` separately preserves FAIL_HISTORICAL_ATTRIBUTION for original target bytes; historical dataset labels remain untouched. Source implementation remains unchanged, while the explanation warrants a manual MODIFY. This is not a before/after source-evolution classifier trial or a new neural generation.

Population audit v3 now describes15related bilingual chapter-version pairs:13TECHNICALLY_ACCEPTED,1retained SQLX citation gap and1original Go Image historical-attribution failure. The helper maintenance pair remains separate. `requested-metric-reconciliation-v2.json` binds these descriptive counts while preserving all16requested metrics and unknown general semantic/performance rates. Current local model calls/tokens/generation time and optimizer updates remain0; GPT/Codex assistance is distinct and nonzero. No original305records, external source, production or permanent tests changed; Gold/publication/owner approvals remain0. Approximately12actualhours and final consolidation remain outstanding.
'''
j=p/'root-report-bundle-progress-028';prepare(root,j,{n:common.encode() for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
with (p/'root-report-append-receipt-v28.json').open('x') as f:json.dump({'bundle':str(j.relative_to(root)),'outcome':out},f,indent=2);f.write('\n')
print(out['status'])
