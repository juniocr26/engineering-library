import json
from pathlib import Path
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2]
common='''

### Final intensive progress 023 — proposal integration boundary review

Read-only audit `proposal-integration-boundary-audit-v2.json` verifies the exact current targets for four preserved proposals: semantic admission, cached Go fault delivery, independent REMOVE scope, and FAQ/question binding. All prior target hashes still match. Each proposal contains cause, expected behavior, regression cases and integration risks; no implementation, permanent tests, application run or approval was performed. Existing Ruby command output explicitly reports review:draft at line581; Python candidate metadata keeps owner_approved/training_gold false. A written/rendered draft must not be mislabeled technical acceptance or publication, and existing code must not be falsely accused of owner-approval bypass. Structural admission still does not establish whole-prose semantics.

The first audit correctly described draft behavior but bound its trace to lines583–585, omitting the actual output line581. Version2 corrects that exact trace to579–584; version1 is preserved as a citation-binding defect, not silently rewritten. Source-context reading and an integrity manifest remain separate responsibilities.

Next work reconciles all requested metric names against explicit measured/unknown populations and refreshes the22-question audit with the latest checkpoint and verification findings. The campaign remains active; no new local neural inference, optimizer update, production change, owner Gold or publication approval.
'''
j=p/'root-report-bundle-progress-023';prepare(root,j,{n:common.encode() for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
with (p/'root-report-append-receipt-v23.json').open('x') as f:json.dump({'bundle':str(j.relative_to(root)),'outcome':out},f,indent=2);f.write('\n')
print(out['status'])
