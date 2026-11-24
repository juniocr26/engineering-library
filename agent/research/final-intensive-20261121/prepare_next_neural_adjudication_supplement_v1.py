"""Non-executable adjudication safeguards for the frozen future DEV pair."""
from pathlib import Path
import json,hashlib,datetime
P=Path(__file__).resolve().parent;root=P.parents[2]
ref=lambda n:{'path':str((P/n).relative_to(root)),'sha256':hashlib.sha256((P/n).read_bytes()).hexdigest()}
d={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'role':'PROSPECTIVE_SCORING_AND_CAUSAL_LIMITS_SUPPLEMENT_NOT_EXECUTED_NOT_AUTHORIZATION','protocol':ref('next-neural-matched-dimensions-protocol-v1.json'),'request_audit':ref('next-neural-matched-dimensions-request-audit-v1.json'),'time_budget':ref('next-neural-matched-dimensions-wall-clock-supplement-v1.json'),'failure_diagnostic':ref('historical-neural-failure-taxonomy-v2.json'),'changes_to_frozen_inputs_or_budgets':False,'current_model_calls':0,'inference_authorized_by_this_supplement':False,'production_changes':0,
'acceptance_unit':'A complete EN/PT bounded chapter plus all three requested FAQs and full frozen G1–G9 requirements. A correct action, a few true facts, JSON validity or literal IDs alone cannot pass.',
'scoring_procedure_if_future_run_is_authorized':[
'Preserve immutable raw request/response, terminal reason, runtime/model identity, exact context admission evidence, timing and tokens before preparing any review view.',
'Assign neutral output IDs using a recorded mapping stored outside the reviewer view. Hide arm labels and preparation-field identities from the first scoring view; never remove content from the raw artifact or substantive claims from the reviewer view.',
'Freeze the reviewer view and its exact hash before first scoring; score each output against source and the pre-existing full rubric before revealing arm identity.',
'Unitize every factual proposition in output order, including qualifications in tables, examples, FAQs and translations. Record compound claims as separate linked propositions where feasible. Retain a stable claim ID, exact output span, source support span, status and reviewer provenance.',
'For each proposition classify supported, contradicted, unsupported or genuinely unknown. Distinguish omitted required coverage from a false assertion and from an appropriately bounded unknown.',
'Evaluate EN/PT conditions, negation, method ownership, signatures, units, return ordering, defaults and FAQ question association; a citation-ID match is insufficient.',
'Apply each gate independently. Any critical unknown is INCONCLUSIVE; any critical false claim or unmet mandatory requirement prevents technical acceptance. Do not repair the output before grading its original bytes.',
'Unblind only after immutable per-output verdicts; preserve any later corrections as separate candidates with separate authorship and gates. Never relabel an original failed response as accepted.'
],
'causal_and_cost_limits':[
'The frozen B-then-A order has no counterbalancing. Load, cache, context initialization, thermal/resource drift and timing order can confound cost differences. Record first-load and generation times separately where the runtime actually supplies them; do not claim a causal speed benefit.',
'Temperature zero and fixed seed do not by themselves certify deterministic kernels or identical runtime state. One response per arm is descriptive; no statistical significance, general method ranking or weights improvement.',
'Removing three metadata fields changes prompt token count. Equal maximum context/output settings are not equal actual admission, prompt length, completed output length or inference cost.',
'The same agent may remember protocol/reference/arm identity despite a neutral view. This procedure reduces label exposure but is not an independent human reviewer, certified blinding or independent benchmark.',
'The source family and complete task are already DEV-exposed. Related repos, imports, translations and FAQs retain the family exclusion. The pair must not enter a future holdout or training merely because output bytes are new.',
'If only one response is available, timeout leaves outcome unknown, output is truncated, context is silently shortened or any identity/admission gate fails, the comparison is INCONCLUSIVE_UNPAIRED. No automatic retry or budget expansion.',
'Passing both outputs would show bounded task acceptance under exact conditions, not isolate every mechanism; failing both does not falsify metadata-role confusion as a general mechanism. Record observed claim differences without inventing cause.'
],
'current_acceptance_barriers':['Unchanged host/runtime denial: no dispatch is attempted.','No current complete local-model output to score.','No certified independent holdout population or independent human claim denominator.','Publication, owner approval, Gold and training remain separate and false.'],
'first_complete_neural_output_success_condition':'At least one original, complete local-model contribution output passes all applicable frozen gates at exact source/response identity, with factual coverage and bilingual review. This is a future condition, not a result of static preparation.',
'budget_change':None,'retry_change':None,'training_or_optimizer_updates':0}
with (P/'next-neural-adjudication-supplement-v1.json').open('x') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
print('prospective supplement preserved; no inference or scoring result')
