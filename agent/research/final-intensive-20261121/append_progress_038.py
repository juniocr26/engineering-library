import json
from pathlib import Path
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2]
common='''

### Final intensive progress 038 — exact local vendor source and unresolved Go intake

A predeclared prospective Go-source inquiry preserved the installed SDK vendor variant of golang.org/x/net/http/httpguts as six exact raw source/license/carrier files, content snapshot sha256:928bae0207dd9f0c0b5dd2baebc4551e43be3bbc6fd7b71599be5d9b0316b4e9. The carrier declares an upstream pseudoversion but full upstream commit and byte equivalence remain unverified. This is not a new checkout, certified independent family, accepted chapter or neural evaluation. Existing compiler/source-graph tools and family exclusions were frozen before source review and remain unchanged.

Bounded existing-research scans found no family/path identifiers in9814UTF8files and no selected API identifiers in9816files. Archives, external sources and model pretraining are outside those scans; zero hits do not certify independence. Complete reading of the two captured Go files produced14manual bilingual composite references with explicit negative challenges. The functions distinguish token/field-name/field-value/host byte predicates; the host check is lenient, the field-value predicate permits edge spaces/tabs, and the non-ASCII conversion branch depends on unreviewed IDNA behavior. A negative rune/byte-conversion observation is supported by the preserved installed Go language specification and static reasoning, without executing the target. References are prospective only, not training/Gold/owner approved.

The unchanged v5 observer received both complete files and the unchanged standard-export graph. It returned INCONCLUSIVE_TYPE_OR_IMPORT_ERRORS for net/textproto, net and golang.org/x/net/idna, with zero admitted declarations/relations or partial type facts. No stubs, source deletion, closure enlargement or rule tuning was used to turn this result into a pass. Exact raw bytes, reference ranges, language evidence and expected inconclusive binary replay pass the local recovery consumer; a new full checkpoint is pending. Model calls/optimizer updates remain zero.

Repository ledgerv10 adds25actual read-only commands across configuration, Starlette and frontend acquisitions, including one failed named config_test query. Its initial v9 adapter failed on a preexisting dict/list shape assumption; the failed script and failure receipt are retained, and a separate corrected adapter produced42repository blocks. Ledger state/inventory fields retain explicit prior observation cuts rather than claiming a current final inventory. No source/application/UI/permanent-test/external-repository mutations or Git actions. Campaign remains active; final duration and consolidation are not yet complete.
'''
j=p/'root-report-bundle-progress-038';prepare(root,j,{n:common.encode() for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
with (p/'root-report-append-receipt-v38.json').open('x') as f:json.dump({'bundle':str(j.relative_to(root)),'outcome':out},f,indent=2);f.write('\n')
print(out['status'])
