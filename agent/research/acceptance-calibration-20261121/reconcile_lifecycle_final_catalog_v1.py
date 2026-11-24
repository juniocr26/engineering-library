"""Rebuild every current matrix/rate from84 terminal records, not planner execution."""
from pathlib import Path
from collections import Counter,defaultdict
import copy,datetime,hashlib,json
P=Path(__file__).resolve().parent
source=P/'scope-retirement-initialization-profile-results-v8.json'
rows=copy.deepcopy(json.loads(source.read_text())['records'])
v1path=P/'scope-binding-owner-comparison-results-v2.json'
v1={(r['cohort'],r['id']):r['v1_action']for r in json.loads(v1path.read_text())['records']}
for row in rows:
 identity=(row['cohort'],row['id'])
 if identity in v1:row['v1_action']=v1[identity]
assert len({(r['cohort'],r['id'])for r in rows})==84
labels=['ADD','MODIFY','REMOVE','NO-OP','INCONCLUSIVE']
fields=['baseline_action','v1_action','v2_action','v3_action','v4_action','v5_action','v6_action','v7_action','v8_action']
def rate(n,d):return {'numerator':n,'denominator':d,'ratio':n/d if d else None}
def compute(subset,field):
 selected=[r for r in subset if field in r];n=len(selected)
 m={r:{c:0 for c in labels}for r in labels}
 for r in selected:m[r['reference']][r[field]]+=1
 s={r:sum(m[r].values())for r in labels}
 return {'matrix_reference_rows_predicted_columns':m,'n':n,'reference_support':s,
 'exact_agreement':rate(sum(m[l][l]for l in labels),n),
 'false_remove':rate(sum(m[l]['REMOVE']for l in labels if l!='REMOVE'),n-s['REMOVE']),
 'false_modify':rate(sum(m[l]['MODIFY']for l in labels if l!='MODIFY'),n-s['MODIFY']),
 'missed_modify':rate(s['MODIFY']-m['MODIFY']['MODIFY'],s['MODIFY']),
 'unsupported_change_on_insufficient_scope':rate(sum(m['INCONCLUSIVE'][l]for l in ['ADD','MODIFY','REMOVE']),s['INCONCLUSIVE']),
 'justified_abstention':rate(m['INCONCLUSIVE']['INCONCLUSIVE'],s['INCONCLUSIVE']),
 'abstention_on_decidable':rate(sum(m[l]['INCONCLUSIVE']for l in labels if l!='INCONCLUSIVE'),n-s['INCONCLUSIVE']),
 'remove_recall':rate(m['REMOVE']['REMOVE'],s['REMOVE']),
 'false_noop_on_changes':rate(sum(m[l]['NO-OP']for l in ['ADD','MODIFY','REMOVE']),sum(s[l]for l in ['ADD','MODIFY','REMOVE']))}
cohorts=defaultdict(list)
for row in rows:cohorts[row['cohort']].append(row)
oldpath=P/'lifecycle-matrix-and-rate-audit-v7.json';old=json.loads(oldpath.read_text())
oldmap={c['cohort']:c for c in old['new_owned_cohorts']};new=[];checks=[]
for name,subset in sorted(cohorts.items()):
 conditions={field:compute(subset,field)for field in fields if any(field in r for r in subset)}
 for field,value in conditions.items():
  previous=oldmap[name]['conditions'][field]
  for metric,expected in value.items():
   if metric not in previous:continue
   assert previous[metric]==expected,(name,field,metric)
  checks.append({'cohort':name,'condition':field,'matrix_and_all_available_rate_values_unchanged':True,
                 'matrix_sum':sum(sum(v.values())for v in value['matrix_reference_rows_predicted_columns'].values()),
                 'actual_observations':value['n'],'all_zero_denominator_ratios_are_null':all(v['ratio']is None for v in value.values()if isinstance(v,dict)and v.get('denominator')==0)})
 new.append({'cohort':name,'unique_cases':len(subset),'case_ids':[r['id']for r in subset],
             'conditions':conditions,'source_scope':'Owned development-exposed parse-only closed source controls; no real catalog/source actions.',
             'ADD_NOOP_reference_support_zero':all(r['reference']not in ['ADD','NO-OP']for r in subset)})
result=copy.deepcopy(old);result['at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
result['extends']=oldpath.name;result['prior_sha256']=hashlib.sha256(oldpath.read_bytes()).hexdigest()
result['new_owned_cohorts']=new;result['condition_observation_counts']=dict(Counter(field for r in rows for field in fields if field in r))
result['prior_scope_retained_as_history']=old['scope']
result['scope']='84uniqueownedcases/11cohorts,8historicalcohortsseparate. V6falseR6/6and4/4authoritynegatives; V7blocksthosebutnewreachabilityfalseR4/4. V8literal-moduleprofileblocksnew4/4butretains1/4freshlegitimateRandloses4additionalpriorlegitimateR. MODIFYutilitylimitsretained. No genericresolver/runtime/project/catalogauthorityorindependentholdoutproof. NewADD/NOOPreferencecounts0andundefinedratesnull.'
result['matrix_rate_invariants_verified']=len(checks)
result['matrix_rate_recomputation_checks']=checks
result['owned_observation_sources']=[{'path':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}for f in [source,v1path]]
result['curation_correction']='v7newmatrices/countswerecorrect,butcopiedscopeand68-invariantcountstilldescribedv6cut. v8rebuildsallcurrentmatrices/ratesandnormalizescurrentmetadata; oldv7andallvaluespreserved. No source/planner/inference rerun.'
with(P/'lifecycle-matrix-and-rate-audit-v8.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps({'matrices_recomputed':len(checks),'all_prior_values_match':True,'unique_owned_cases':84,
 'cohorts':len(new),'condition_counts':result['condition_observation_counts'],'planner_executions':0},indent=2))
