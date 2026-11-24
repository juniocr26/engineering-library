"""Read-only proposal readiness audit; no implementation or permanent test changes."""
import json,hashlib,datetime
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[2];prior=root/'agent/research/acceptance-calibration-20261121/proposed-fixes-for-owner-review-v6.json'
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
old=json.loads(prior.read_text());records=[]
for proposal in old['proposals']:
 identities=[]
 for edge in proposal['production_evidence_unchanged']:
  target=root/edge['path'];identities.append({**edge,'current_sha256':sha(target),'matches_prior_proposal':sha(target)==edge['sha256']})
 tests=[{'path':name,'exists':(root/name).is_file(),'current_sha256':sha(root/name) if (root/name).is_file() else None,'executed_now':False} for name in proposal['permanent_validation_files_requires_approval']]
 records.append({'id':proposal['id'],'status':'PROPOSED_NOT_APPLIED','targets':identities,'validation_targets':tests,'cause_present':bool(proposal['problem']),'expected_behavior_present':bool(proposal['proposed_behavior']),'regression_cases_present':bool(proposal['expected_regressions']),'risks_present':bool(proposal['risks']),'new_implementation_authorized':False})
faq=json.loads((p/'faq-binding-integration-proposal-v1.json').read_text());records.append({'id':'P-FAQ-QUESTION-BINDING','status':'PROPOSED_NOT_APPLIED','targets':[{**x,'current_sha256':sha(root/x['path']),'matches_prior_proposal':sha(root/x['path'])==x['sha256']} for x in faq['target_files_for_owner_design_review_only']],'cause_present':bool(faq['cause']),'expected_behavior_present':bool(faq['proposed_future_boundary']),'regression_cases_present':bool(faq['expected_regressions']),'risks_present':bool(faq['risks']),'new_implementation_authorized':False})
assert all(t['matches_prior_proposal'] for r in records for t in r['targets'])
traces=[]
for name,start,end,meaning in [
 ('backend/lib/documentation/command.rb',510,529,'Both source and optional web facts go through validate_and_render; this is a guarded draft path, not whole-prose semantic certification.'),
 ('backend/lib/documentation/command.rb',537,575,'Ownership and concurrent-edit checks precede staged candidates, application journal and output writes; existing recovery semantics must be preserved.'),
 ('backend/lib/documentation/command.rb',583,585,'The actual completion output explicitly says review:draft; status:written is not publication or technical acceptance.'),
 ('backend/lib/documentation/command.rb',1208,1264,'Bounded structural and special-case guards, source identity and symbols; exact comment states conservative citation guard, not semantic validation.'),
 ('agent/tools/documentation_candidates.py',215,229,'In-memory construction returns owner_approved:false/training_gold:false and requires caller source/registry binding.')]:
  f=root/name;lines=f.read_text().splitlines();assert end<=len(lines)
  traces.append({'path':name,'whole_file_sha256':sha(f),'lines':[start,end],'quote':'\n'.join(lines[start-1:end]),'interpretation':meaning,'method':'Actual source read by same campaign agent; not runtime execution.'})
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'prior_proposal':{'path':str(prior.relative_to(root)),'sha256':sha(prior)},'records':records,'source_traces':traces,'current_evidence_addenda':{'P-SEMANTIC-ADMISSION':['bilingual-guard-semantic-boundary-review-v1.json','renderer-recovery-results-v1.json'],'P-CACHED-GO-FAULT':['helper-subprocess-dynamic-review-v1.json','helper-job-state-semantics-review-v1.json'],'P-INDEPENDENT-REMOVE-SCOPE':['chi-revision-context-complete-review-v2.json','go-shellwords-version-scope-reference-review-v1.json'],'P-FAQ-QUESTION-BINDING':['faq-question-binding-results-v1.json']},'interpretation_limits':['Preserving draft output is a deliberate existing boundary, not evidence of an owner-approval bypass.','Production integration requires an explicit design of trusted review authority and compatible states; this audit does not choose or implement it.','Old recorded runtime experiments and current source inspection are separate evidence populations.','Do not add a boolean model-authored approved field as trusted review.','Permanent regression paths were only stat/hash inspected, never executed or changed.'],'source_targets_unchanged':True,'permanent_tests_executed':False,'production_changes':False,'owner_questions':0}
with (p/'proposal-integration-boundary-audit-v1.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({'proposals':len(records),'target_hashes_all_match':True,'source_traces':len(traces),'production_changes':False}))
