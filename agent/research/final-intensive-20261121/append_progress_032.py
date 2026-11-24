import json
from pathlib import Path
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2]
common='''

### Final intensive progress 032 — source-graph prototype boundaries found before real intake

A separate owned Go source-graph observer was compiled offline with existing Go1.27.1, no installation/download, in isolated research v3/v4directories. Nine frozen development controls matched: local type alias/interface relations, interface method versus runtime target, missing source import, dependency type error, cycle, stdlib shadow, unreferenced bad package, source hash mismatch and duplicateJSON. No partial declarations/relations were admitted on failure. These9owned mechanisms are not independent model/document acceptance observations. Previous v1/v2observers remain unchanged.

Additional explicit namespace controls found v3accepted source package dot/parent forms and dotdot display filename despite its intended clean-name boundary. No arbitrary source file was read: sources came from packets. V3source/binary/failures remain preserved. Separate v4tightens clean relative ASCII names and nonstandard package prefixes; all12original-plus-namespace controls then matched.

Before any actual Go Image source intake, a distinct frozen eight-run determinism probe used valid one-line owned declarations. V4produced4canonical packet variants, but exactly1variant after normalizing relation/declaration order. This demonstrates nondeterministic tie ordering, not changing type meanings. Do not claim exact generic recovery yet. Next separate version fixes full tie ordering, repeats the same frozen mechanism controls and only then checks the exact two real application packages. No actual target/source execution, external imports, model calls, training, production/permanent-test edits or new document acceptance. All original failed versions/artifacts retained.
'''
j=p/'root-report-bundle-progress-032';prepare(root,j,{n:common.encode() for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
with (p/'root-report-append-receipt-v32.json').open('x') as f:json.dump({'bundle':str(j.relative_to(root)),'outcome':out},f,indent=2);f.write('\n')
print(out['status'])
