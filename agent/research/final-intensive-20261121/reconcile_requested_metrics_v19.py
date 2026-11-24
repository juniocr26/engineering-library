"""Map all requested metric names to exact populations, including unmeasured ones."""
import json,hashlib,datetime
from pathlib import Path
p=Path(__file__).resolve().parent
request=p/'user-request-original-v1.txt';audit=p/'current-metric-population-audit-results-v21.json';d=json.loads(audit.read_text());by={r['id']:r for r in d['metrics']}
specs=[
('Complete-document technical acceptance rate',['new-neural-complete-output-acceptance'],'No new local-model trial; descriptive manual candidate-pair accounting is separate.'),
('Atomic supported-claim precision',['global-atomic-supported-claim-precision'],'28 reobtained registered pairs are not an independently enumerated atomic claim denominator.'),
('Unsupported factual claim rate',[],'No new independent generated atomic claim population; cannot infer complement from hash/span matches.'),
('Critical factual error count',[],'No new generated local-model output; accepted manual pairs have scoped review verdicts, not a representative model error frequency.'),
('Frozen requirement coverage',[],'Whole candidate gate verdicts exist, but heterogeneous scope requirements have no single independently enumerated comparable denominator.'),
('Architecture relationship coverage',[],'Selected callers and static typed relations have bounded observations; full relevant relation reference graph has not been independently enumerated across tasks.'),
('Source citation semantic correctness',[],'Physical span and identity checks do not entail statement truth; no independent global semantic citation denominator.'),
('Exact technical identifier preservation',['independent-technical-identifier-preservation'],'Owned mutation screens and manually reviewed chapter pairs do not supply independent model identifier accuracy.'),
('Bilingual semantic agreement',['independent-bilingual-semantic-agreement'],'Bilingual lexical study explicitly demonstrates semantic blind spots and paraphrase false flags; no representative independent semantic sample.'),
('Correct lifecycle action rate',['independent-lifecycle-decision-accuracy'],'Real revision cases support bounded correlated decisions, not a generalized rate.'),
('Unsafe REMOVE recommendation rate',['new-autonomous-unsafe-REMOVE-rate'],'No current autonomous model recommendation population; absence of production mutation is not proof of safe recommendation accuracy.'),
('Verifier false acceptance rate',['envelope-integrity-false-admission','faq-literal_violation_admissions','faq-semantic_negative_binding_passes'],'Integrity, literal binding and manually labelled semantic-negative controls must remain separate populations.'),
('Verifier false rejection rate',['envelope-integrity-false-refusal','faq-literal_positive_refusals','faq-legitimate_paraphrase_refused'],'Exact literal policy and genuine semantic acceptability differ; selected controls are not independent general error estimates.'),
('Appropriate INCONCLUSIVE decisions',[],'Examples include incomplete source identity, missing supplied Go shellRun, invalid import identity and source citation gaps; no independent denominator of all opportunities.'),
('Reproducibility and recovery success',[],'Checkpoint044 verifies5263 retained regular files and45finite consumer groups; earliercheckpoint040 finalreports additionallyrequire preservedlatebundle055sidecar; failed031 is preserved and not counted as recovery; not a population estimate of machine/OS/crash/weights/optimizer recoverability.'),
('Neural inference cost, time, and token usage',['new-neural-inference-tokens'],'Current local-model calls, generated tokens and generation seconds are zero. GPT/Codex campaign accounting is distinct and nonzero; monetary cost unknown.')]
text=request.read_text();records=[]
for index,(name,ids,limit) in enumerate(specs,1):
 assert '- '+name+'.' in text,name
 bounded=[by[x] for x in ids]
 records.append({'request_metric_number':index,'requested_name':name,'current_general_numerator':0 if index==1 else None,'current_general_denominator':0 if index==1 else None,'current_general_ratio':None,'population':'Current campaign eligible independent local neural trials; none executed' if index in [1,2,3,4,8,9,10,11,16] else 'No sufficient independently enumerated applicable population','method':'Exact request-to-receipt reconciliation, not a fresh performance experiment','baseline':'Historical heterogeneous local model results and prior development controls remain in original receipts; not pooled','confidence_limitations':limit,'bounded_measured_subpopulations':bounded,'general_status':'INSUFFICIENT_EVIDENCE','do_not_pool':True})
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'request_sha256':hashlib.sha256(request.read_bytes()).hexdigest(),'audit_sha256':hashlib.sha256(audit.read_bytes()).hexdigest(),'records':records,'all16_requested_metrics_accounted_for':len(records)==16,'manual_chapter_version_accounting':d['chapter_version_accounting'],'helper_maintenance_separate':d['maintenance_accounting_separate'],'internal_agent_chapter_separate':d['internal_agent_chapter_accounting_separate'],'current_local_inference_accounting':{'calls':0,'tokens':0,'generation_seconds':0,'monetary_cost':None,'monetary_cost_status':'Unknown; absence of local generation does not report total GPT/Codex cost as zero'},'no_new_model_readiness_claim':True,'training_or_production_change':False}
with (p/'requested-metric-reconciliation-v19.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({'requested_metric_names':len(records),'unjustified_general_rates':0,'current_neural_denominator':0}))
