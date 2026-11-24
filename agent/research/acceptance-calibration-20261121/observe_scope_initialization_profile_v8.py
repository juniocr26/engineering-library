"""Frozen V7 on fresh source controls, then finite V8 filter; source never runs."""
from pathlib import Path
import ast,copy,datetime,hashlib,json
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
protocol_path=P/'scope-retirement-initialization-profile-protocol-v8.json'
protocol=json.loads(protocol_path.read_text())
for item in protocol['evidence']:assert hashlib.sha256((P/item['path']).read_bytes()).hexdigest()==item['sha256']
fresh=json.loads((P/protocol['fresh_baselines']).read_text())['records']
v7_tree=ast.parse((P/'observe_scope_retirement_filter_v7.py').read_text())
loops=[n for n in v7_tree.body if isinstance(n,ast.For)and isinstance(n.target,ast.Name)and n.target.id=='previous']
assert len(loops)==1
ns={'Path':Path,'ROOT':ROOT,'P':P,'ast':ast,'json':json,'hashlib':hashlib,'rows':copy.deepcopy(fresh),'records':[],'seen':set()}
exec(compile(ast.Module(body=loops,type_ignores=[]),'frozen-owned-v7-filter-loop','exec'),ns)
new=ns['records'];assert len(new)==8
old=json.loads((P/protocol['prior_terminal_V7']).read_text())['records']
records=[]
for previous in old+new:
 row=copy.deepcopy(previous);row['v8_action']=row['v7_action'];refusals=[]
 if row['v7_action']=='REMOVE':
  root=ROOT/row['v2_evidence']['root']
  for entry in row['v2_evidence']['independently_enumerated_files']:
   if 'sha256'not in entry:refusals.append({'path':entry['path'],'reason':'UNACQUIRED_ENTRY'});continue
   raw=(root/entry['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['sha256']
   tree=ast.parse(raw.decode())
   for node in tree.body:
    admitted=isinstance(node,ast.Pass)or(isinstance(node,ast.Expr)and isinstance(node.value,ast.Constant)and isinstance(node.value.value,str))
    if isinstance(node,ast.Assign)and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
     try:ast.literal_eval(node.value);admitted=True
     except(ValueError,TypeError,SyntaxError,RecursionError):admitted=False
    if not admitted:refusals.append({'path':entry['path'],'line':node.lineno,'node_kind':type(node).__name__,'reason':'MODULE_INITIALIZATION_OUTSIDE_LITERAL_PROFILE'})
  if refusals:row['v8_action']='INCONCLUSIVE'
 row['v8_initialization_profile']={'only_filters_V7_REMOVE':True,'refusal_reasons':refusals,
  'not_proof_of_actual_runtime_module_initialization':True}
 records.append(row)
labels=['ADD','MODIFY','REMOVE','NO-OP','INCONCLUSIVE']
def rate(n,d):return {'numerator':n,'denominator':d,'ratio':n/d if d else None}
def metrics(rows,field):
 m={r:{c:0 for c in labels}for r in labels}
 for row in rows:m[row['reference']][row[field]]+=1
 s={r:sum(m[r].values())for r in labels};n=len(rows)
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
cohorts=[]
for name in sorted({r['cohort']for r in records}):
 rows=[r for r in records if r['cohort']==name]
 fields=['baseline_action','v2_action','v3_action','v5_action','v6_action','v7_action','v8_action']if name=='new-retirement-reachability-challenge-8'else['v7_action','v8_action']
 cohorts.append({'cohort':name,'unique_cases':len(rows),'case_ids':[r['id']for r in rows],
                 'conditions':{field:metrics(rows,field)for field in fields},'source_scope':'Ownedfrozenparse-onlysource; no actualruntime/catalogactions',
                 'ADD_NOOP_reference_support_zero':True})
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':protocol_path.name,
 'protocol_sha256':hashlib.sha256(protocol_path.read_bytes()).hexdigest(),'records':records,'cohorts':cohorts,
 'unique_owned_cases':len(records),'old76labels_reused_without_rerun':True,
 'new_reachability_cases':8,'new_V7_false_remove':metrics(new,'v7_action')['false_remove'],
 'new_V8_false_remove':metrics([r for r in records if r['cohort']=='new-retirement-reachability-challenge-8'],'v8_action')['false_remove'],
 'interpretation':'Freshsourceinitializationcontrols falsifyV7zero-falseREMOVEgeneralization:4/4insufficientreachabilitycasesstillREMOVE. V8finiteall-literalmoduleprofileblocks4/4butretains1/4legitimatecontrols; oldcohortutilitymeasuredseparately. No genericPython/moduleexecutionproof, projectcompleteness, productionfix or currentcatalogauthority. Allsourcecontrols remaininert.',
 'source_controls_executed':False,'model_calls':0,'production_changes':0,'gold':0,'optimizer_updates':0}
with(P/'scope-retirement-initialization-profile-results-v8.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
prior_path=P/'lifecycle-matrix-and-rate-audit-v6.json';catalog=json.loads(prior_path.read_text());catalog['at']=result['at'];catalog['extends']=prior_path.name;catalog['prior_sha256']=hashlib.sha256(prior_path.read_bytes()).hexdigest()
old_by_name={c['cohort']:c for c in catalog['new_owned_cohorts']}
for cohort in cohorts:
 if cohort['cohort']in old_by_name:old_by_name[cohort['cohort']]['conditions']['v8_action']=cohort['conditions']['v8_action']
 else:catalog['new_owned_cohorts'].append(cohort)
catalog['new_owned_unique_cases']=84
catalog['condition_observation_counts']={field:sum(c['unique_cases']for c in catalog['new_owned_cohorts']if field in c['conditions'])for field in sorted({f for c in catalog['new_owned_cohorts']for f in c['conditions']})}
catalog['new_evidence']={'path':'scope-retirement-initialization-profile-results-v8.json','sha256':hashlib.sha256((P/'scope-retirement-initialization-profile-results-v8.json').read_bytes()).hexdigest()}
catalog['interpretation_v7']='Prior76cases/10cohortsretainedexactly; add8newreachabilitycasesas11thcohort. V7new4/4falseR, V8new0/4falseRbut1/4Rrecall. No pooledgeneralaccuracy; allhistorical8cohortsunchanged. NewV8finiteprofileaddsconditiononall84actualownedcases.'
for c in catalog['new_owned_cohorts']:
 for values in c['conditions'].values():
  matrix=values.get('matrix_reference_rows_predicted_columns',values.get('matrix_reference_rows_observed_columns'))
  assert sum(sum(v.values())for v in matrix.values())==c['unique_cases']
with(P/'lifecycle-matrix-and-rate-audit-v7.json').open('x')as stream:json.dump(catalog,stream,indent=2);stream.write('\n')
fresh_cohort=next(c for c in cohorts if c['cohort']=='new-retirement-reachability-challenge-8')
print(json.dumps({'new_cases':8,'total_owned':84,'cohorts':len(cohorts),'condition_counts':catalog['condition_observation_counts'],
 'fresh_V7':{k:v for k,v in fresh_cohort['conditions']['v7_action'].items()if k!='matrix_reference_rows_predicted_columns'},
 'fresh_V8':{k:v for k,v in fresh_cohort['conditions']['v8_action'].items()if k!='matrix_reference_rows_predicted_columns'}},indent=2))
