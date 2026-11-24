import json,hashlib,datetime
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[2];old=p/'campaign-requirement-evidence-audit-v3.json';d=json.loads(old.read_text());now=datetime.datetime.now(datetime.timezone.utc)
def ev(name):
 x=p/name;return {'path':str(x.relative_to(root)),'sha256':hashlib.sha256(x.read_bytes()).hexdigest()}
updates={
8:('Integrity false admissions0/60 and FAQ literal-violation admissions0/9 remain finite controls. Two semantic-negative FAQ controls and two new bilingual wrong action/subject controls pass their respective literal screens. These separate correlated populations cannot establish general semantic FAR.',['binding-study-results-v1.json','faq-question-binding-results-v1.json','bilingual-guard-study-results-v1.json']),
9:('Envelope intact refusals0/3 and FAQ exact-positive refusals0/2 are literal/integrity results. FAQ legitimate paraphrase refusal1/1 and bilingual screen valid paraphrase flags1/2 demonstrate separate bounded false-flag mechanisms, not pooled semantic FRR.',['binding-study-results-v1.json','faq-question-binding-results-v1.json','bilingual-guard-study-results-v1.json']),
19:('Owned syntax, static relation, journal-delivery, recovery and bilingual-screen controls executed. Checkpoint019 consumer closure is verified; no current target application or upstream permanent suites executed. Historical312Python/242Ruby1699assertions/frontend100of102 unchanged historical.',['checkpoint-019.json','bilingual-guard-study-results-v1.json','proposal-integration-boundary-audit-v2.json']),
20:('Four proposals retain exact matching current target hashes and documented causes/behavior/regressions/risks. Ruby written output explicitly remains draft; Python owner/Gold fields remainfalse. Cached helper fault/job UNKNOWN findings persist. New bilingual screen cannot certify semantics. All production/permanent-test fixes unapplied.',['proposal-integration-boundary-audit-v2.json','helper-job-state-semantics-review-v1.json','bilingual-guard-semantic-boundary-review-v1.json']),
21:('Checkpoint019 restored2671regularfiles with exact hashes/modes and20 finite consumer groups; its postnote reconstructed all four final reports exactly from archived prefixes and receipt-sidecar procedure. Artifacts created afterward await next checkpoint. No remote/cleanclone/Windows/crash/weights/optimizer restore claim.',['checkpoint-019.json','root-report-checkpoint-019-postnote-v1.json'])}
for row in d['final_question_audit']:
 if row['number'] in updates:
  row['current_answer'],names=updates[row['number']];row['evidence']=[ev(n) for n in names]
 for edge in row['evidence']:
  assert hashlib.sha256((root/edge['path']).read_bytes()).hexdigest()==edge['sha256'],edge['path']
d.update(at=now.isoformat(),elapsed_since_instrumented_baseline_seconds=(now-datetime.datetime.fromisoformat('2026-11-21T22:42:45.313891+00:00')).total_seconds(),approximately12hours_met=False,previous_turn_classification='PROGRESS_FULL_METRIC_RECONCILIATION_AND_LATEST_RECOVERY_AUDIT',extends=ev(old.name),correction='Refresh questions8,9,19,20,21 and verify every cited evidence digest; latest requested16 metric registry remains separate from historical counts.',requested_metric_registry=ev('requested-metric-reconciliation-v1.json'))
assert len(d['final_question_audit'])==22
with (p/'campaign-requirement-evidence-audit-v4.json').open('x') as f:json.dump(d,f,indent=2);f.write('\n')
print('22 answers; all cited evidence digests verified; campaign incomplete')
