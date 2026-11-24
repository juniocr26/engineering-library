"""Apply preregistered finite namespace-attribute refusal to terminal V5 labels only."""
import ast,datetime,hashlib,json,collections
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];protocol=json.loads((P/'scope-namespace-filter-protocol-v6.json').read_text());records=[]
for item in protocol['prior_results']:
 raw=(P/item['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==item['sha256'];records.extend(json.loads(raw)['records'])
records.extend(json.loads((P/'scope-namespace-filter-baselines-v1.json').read_text())['records']);seen=set();output=[]
for old in records:
 key=(old['cohort'],old['id']);assert key not in seen;seen.add(key);row=dict(old);row['v6_action']=row['v5_action'];refusals=[];row['v6_namespace_filter']={'rule':'Any ast.Attribute named __globals__ at any scope is unadmitted; not a mutation proof','refusal_reasons':refusals}
 if row['v5_action']=='MODIFY':
  root=ROOT/row['v2_evidence']['root']
  for file in row['v2_evidence']['independently_enumerated_files']:
   if 'sha256' not in file:continue
   path=root/file['path'];raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==file['sha256'];tree=ast.parse(raw.decode())
   for node in ast.walk(tree):
    if isinstance(node,ast.Attribute) and node.attr=='__globals__':refusals.append({'path':file['path'],'source_sha256':file['sha256'],'line':node.lineno,'ast_expression':ast.unparse(node),'not_proven_mutation':True})
  if refusals:row['v6_action']='INCONCLUSIVE'
 output.append(row)
labels=['ADD','MODIFY','REMOVE','NO-OP','INCONCLUSIVE']
def rate(n,d):return {'numerator':n,'denominator':d,'ratio':n/d if d else None}
cohorts=[]
for cohort in sorted({r['cohort'] for r in output}):
 rows=[r for r in output if r['cohort']==cohort];conditions={}
 for field in ['v5_action','v6_action']:
  matrix={r:{c:0 for c in labels} for r in labels}
  for r in rows:matrix[r['reference']][r[field]]+=1
  support={r:sum(matrix[r].values()) for r in labels};conditions[field]={'matrix_reference_rows_predicted_columns':matrix,'reference_support':support,'exact_agreement':rate(sum(matrix[l][l] for l in labels),len(rows)),'false_remove':rate(sum(matrix[l]['REMOVE'] for l in labels if l!='REMOVE'),len(rows)-support['REMOVE']),'false_modify':rate(sum(matrix[l]['MODIFY'] for l in labels if l!='MODIFY'),len(rows)-support['MODIFY']),'missed_modify':rate(support['MODIFY']-matrix['MODIFY']['MODIFY'],support['MODIFY']),'justified_abstention':rate(matrix['INCONCLUSIVE']['INCONCLUSIVE'],support['INCONCLUSIVE'])}
 cohorts.append({'cohort':cohort,'cases':len(rows),'conditions':conditions})
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':'scope-namespace-filter-protocol-v6.json','unique_cases':len(output),'records':output,'cohorts':cohorts,'no_prior_source_or_planner_rerun':True,'controls_executed':False,'model_calls':0,'optimizer_updates':0,'gold':0,'permanent_tests_added':False,'interpretation':'Finite conservative refusal blocks observed namespaces; false refusal of unused helper/class dictionary and readonly/unrelated direct namespace controls is measured. Neither zero falseMODIFY in these cases nor attribute-name filtering proves generic namespace safety, runtime behavior or production readiness. No ADD/NOOPreference support innewownedcohorts.'}
with (P/'scope-namespace-filter-results-v6.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
for r in cohorts:
 if 'namespace' in r['cohort']:print(json.dumps({'cohort':r['cohort'],'V5':{k:v for k,v in r['conditions']['v5_action'].items() if k!='matrix_reference_rows_predicted_columns'},'V6':{k:v for k,v in r['conditions']['v6_action'].items() if k!='matrix_reference_rows_predicted_columns'}},indent=2))
