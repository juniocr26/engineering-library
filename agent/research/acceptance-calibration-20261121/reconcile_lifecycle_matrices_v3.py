"""Recompute descriptive matrices from terminal owned observations without rerunning planners."""
from pathlib import Path
import json,datetime,hashlib,collections
P=Path(__file__).resolve().parent;prior=P/'lifecycle-matrix-and-rate-audit-v2.json';old=json.loads(prior.read_text());source=P/'scope-registry-profile-results-v5.json';observed=json.loads(source.read_text());earlier=P/'scope-binding-owner-comparison-results-v2.json';v1={(r['cohort'],r['id']):r['v1_action'] for r in json.loads(earlier.read_text())['records']};labels=['ADD','MODIFY','REMOVE','NO-OP','INCONCLUSIVE']
def rate(n,d):return {'numerator':n,'denominator':d,'ratio':n/d if d else None}
def matrix(rows,key):
 m={r:{c:0 for c in labels} for r in labels};pairs=[]
 for record in rows:
  if key not in record:continue
  ref=record['reference'];pred=record[key];assert ref in labels and pred in labels;m[ref][pred]+=1;pairs.append((ref,pred))
 n=len(pairs);supports={r:sum(m[r].values()) for r in labels};assert sum(supports.values())==n
 return {'matrix_reference_rows_predicted_columns':m,'n':n,'reference_support':supports,'exact_agreement':rate(sum(r==a for r,a in pairs),n),'false_remove':rate(sum(r!='REMOVE' and a=='REMOVE' for r,a in pairs),sum(r!='REMOVE' for r,a in pairs)),'false_modify':rate(sum(r!='MODIFY' and a=='MODIFY' for r,a in pairs),sum(r!='MODIFY' for r,a in pairs)),'missed_modify':rate(sum(r=='MODIFY' and a!='MODIFY' for r,a in pairs),supports['MODIFY']),'unsupported_change_on_insufficient_scope':rate(sum(r=='INCONCLUSIVE' and a in ['ADD','MODIFY','REMOVE'] for r,a in pairs),supports['INCONCLUSIVE']),'justified_abstention':rate(m['INCONCLUSIVE']['INCONCLUSIVE'],supports['INCONCLUSIVE']),'abstention_on_decidable':rate(sum(r!='INCONCLUSIVE' and a=='INCONCLUSIVE' for r,a in pairs),n-supports['INCONCLUSIVE']),'remove_recall':rate(m['REMOVE']['REMOVE'],supports['REMOVE']),'false_noop_on_changes':rate(sum(r in ['ADD','MODIFY','REMOVE'] and a=='NO-OP' for r,a in pairs),sum(r in ['ADD','MODIFY','REMOVE'] for r,a in pairs))}
cohorts=collections.defaultdict(list);ids=set()
for original in observed['records']:
 r=dict(original);identity=(r['cohort'],r['id']);assert identity not in ids;ids.add(identity)
 if identity in v1:r['v1_action']=v1[identity]
 cohorts[r['cohort']].append(r)
results=[]
for cohort,rows in sorted(cohorts.items()):
 keys=['baseline_action','v1_action','v2_action','v3_action','v4_action','v5_action'];conditions={k:matrix(rows,k) for k in keys if any(k in r for r in rows)}
 results.append({'cohort':cohort,'unique_cases':len(rows),'case_ids':[r['id'] for r in rows],'conditions':conditions,'source_scope':'Owned exposed Python finite controls, supplied owned documentary pointers; no source execution, real catalog action or independent family transfer','ADD_NOOP_reference_support_zero':True})
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'extends':prior.name,'prior_sha256':hashlib.sha256(prior.read_bytes()).hexdigest(),'historical_cohorts_retained_without_rerun':old['historical_cohorts_retained_without_rerun'],'owned_observation_sources':[{'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in [source,earlier]],'new_owned_cohorts':results,'new_owned_unique_cases':len(ids),'V1_observations_available_only_on_original11_and_owner7':True,'other_versions_available_on_all46':True,'duplicate_observation_policy':'Each(cohort,id)countedoncepercondition; reusedterminalobservationsarenotnewcases/trials. Historical8cohorts keptseparate; no pooledgeneralaccuracy.','pooled_general_accuracy':None,'scope':'V5prevents observed objectmutation falseMODIFY but introduces conservative misses for read-only aliases, unrelated keys and function-local shadow. All versions remain research-only, not generic resolver or production-ready. Newownedcohorts do not measureADD/NOOP; historical support does not validate currentprototype ontheseclasses.','source_or_document_actions_applied':0,'new_model_calls':0,'optimizer_updates':0,'gold':0}
with (P/'lifecycle-matrix-and-rate-audit-v3.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'owned_unique_cases':len(ids),'owned_cohorts':len(results),'historical_cohorts':len(old['historical_cohorts_retained_without_rerun']),'planner_runs_now':0}))
for r in results:
 v=r['conditions']['v5_action'];print(r['cohort'],'V5',v['exact_agreement'],'falseM',v['false_modify'],'missM',v['missed_modify'])
