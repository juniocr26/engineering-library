import json
from pathlib import Path
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2]
common='''

### Final intensive progress 036 — original Python ASGI target accepted unchanged

The original dataset has no FastAPIchapter pair; actual metadata selection identified the distinct Starlette server-error chapter. Full EN/PTtext and actual preserved127-token stopped baseline were read. The baseline really claims onlyHTTPinvocation and translates response_started toresposta_started inPT, despite its supplied method showing nonHTTPdelegation. This is a source-visible contradiction/identifier defect, not blame for missing manually expanded helper bodies. No original model score or output was repaired.

Fresh Starlette source at271c277da0ff64e2048a4d46ecc812b9d61db5f6 matches6registeredranges. Full selected class/helpers,application stack context and selected testsource were inspected;7Pythonfiles AST-parsed,notimported/run. The2logical relative source-excerpts links resolve to exactboundbytes. Source supports localstartflagbeforeawaitsend,debug/default/customorder,responseconstructionbeforeconditional sending,andfinalraiseonlyafterpriornormalcompletion. Source comments/docstring always500/alwaysraise are intent,not evidence overriding actualguards/helperfailurepaths. All stated runtime/formatting-security/scheduling/deployment limits remain. No textual correction was required for this original pair; literal provenance metadata localization remains editorialreview, separate from technicalmeaning.

Checkpoint026 restored3610regularfiles with hashes/modes and27finite replay groups,including exact source/AST/span/link/historicalresponse consumer. Four postnote reports reconstructed exactly. Complete-reviewv2 records allG1–G9PASS withindeclaredscope. Populationauditv6 describes19related chapter-versionpairs:16technicalacceptances,1citationgap,2originalhistoricalattributionfailures;helpermaintenance separate. Requested16metricregistryv5 preserves null generalrates and0/0currentneuraltrials.

Ownerreviewbatchv6 retains3primary and6supplementalpublicpairs,9total,with explicit primary-only legacycount scope. Starlette/FastAPIrelatedfamilies,translations,revisions,FAQs and dependencies remain default-deny for independent evaluation/training. No owner/publication/Goldapproval or new localmodelcalls/optimizerupdates. Goalbookkeeping observationv3 is GPT/Codexaccounting,not Ollamatokens/billing; monetarycost unknown. Actual current campaign remains roughly5hours,not12; earlier8hours notadded. No production/permanenttest/external or original305record edits. Final ledger/inventory/question consolidation and duration remain outstanding.
'''
j=p/'root-report-bundle-progress-036';prepare(root,j,{n:common.encode() for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
with (p/'root-report-append-receipt-v36.json').open('x') as f:json.dump({'bundle':str(j.relative_to(root)),'outcome':out},f,indent=2);f.write('\n')
print(out['status'])
