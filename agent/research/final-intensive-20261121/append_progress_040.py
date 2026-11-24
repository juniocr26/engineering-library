import json
from pathlib import Path
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2]
common='''

### Final intensive progress 040 — original task/iteration recovery acceptance and honest current metrics

Checkpoint029 actually restored3808regularfiles withhashes/modes,30finiteconsumer groups and3expectedCsyntax outcomes. The exact Starlette task/iteration consumer replay verified complete originalENPT bytebindings,6PythonASTparses,4sourcepacket ranges,2logical links and4historicalrawresponses, without importing/executing target code. The archivedv11postnoteprocedure checked all29nonCstages and reconstructed fourcanonicalreportbytes withcheckpoint sidecars. Complete-reviewv2 therefore closes G9 and records all nine gatesPASS for the original unchanged manualpair. Owner/publication/Gold stillfalse.

Currentmetric auditv8 recomputes21relatedchapter-versionpairs:18TECHNICALLY_ACCEPTED,1INCONCLUSIVE_CITATION_GAP,2FAIL_HISTORICAL_ATTRIBUTION; helpermaintenance1pairseparate. These are exact manually authored/reviewed document versions, not21independent realtasks or18successful neural outputs. Requestedmetric registryv7 retains16explicit metrics with unknown general rates and zero currentlocal-neuraltrials. It also corrects a stale historicalcheckpoint019description toactual029 and removes an outdated three-pair wording; old registries preserved.

Ownerreviewbatchv8 contains3primary+8supplementalpublicpairs,11total, plus1restrictedhelperpair. The updater initially guessed an absent schema field and failed before output; separate correctedproducer inspectsactualfield, verifies everydocument/gatereceipthash andtotal before writing. Failedadapter/dependentmissing-script receipts retained. Such adapter failures reinforce that metadata shape assumptions are not source or prose correctness. No approvals propagated tooriginal305rows.

Campaign remainsACTIVE, with actualinstrumentedtime nowabout6hours, not12. Modelgenerationcalls/tokens/time andoptimizerupdatesremain0; GPT/Codexusageisnonzeroandmonetarycostunknown. Externalrepos/privatebodyrestrictions/UI/production/permanenttests/Gitstate remainunchanged. Continue substantive original-target diagnosis and final evidence consolidation; final duration/inventory/scope/22question refresh stillpending.
'''
j=p/'root-report-bundle-progress-040';prepare(root,j,{n:common.encode() for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
with (p/'root-report-append-receipt-v40.json').open('x') as f:json.dump({'bundle':str(j.relative_to(root)),'outcome':out},f,indent=2);f.write('\n')
print(out['status'])
