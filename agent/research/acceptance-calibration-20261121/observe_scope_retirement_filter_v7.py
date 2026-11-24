"""Conservative finite retirement-registry authority filter; no source execution."""
from pathlib import Path
import ast,json,hashlib,datetime,collections
P=Path(__file__).resolve().parent;ROOT=P.parents[2];r=json.loads((P/'scope-retirement-filter-protocol-v7.json').read_text());rows=[]
for f in r['prior_results']:
 raw=(P/f['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==f['sha256'];rows.extend(json.loads(raw)['records'])
rows.extend(json.loads((P/'scope-retirement-filter-baselines-v1.json').read_text())['records']);seen=set();records=[]
for previous in rows:
 row=dict(previous);identity=(row['cohort'],row['id']);assert identity not in seen;seen.add(identity);row['v7_action']=row['v6_action'];proof={'applied_to_V6_REMOVE_only':True,'name_occurrences':[],'module_literal_candidates':[],'other_named_bindings':[],'namespace_attributes':[],'refusal_reasons':[]};row['v7_retirement_authority_filter']=proof
 if row['v6_action']=='REMOVE':
  root=ROOT/row['v2_evidence']['root'];expected_records=row['v2_evidence']['retirement_records'];positive_reasons={x['reason'] for x in expected_records};logical_ids=set()
  # Identity comes from frozen case packet, never inferred from a registry's arbitrary key.
  packets=list(root.parent.glob('selected-planner-input.json'));assert len(packets)==1;packet=json.loads(packets[0].read_text());cid=packet['logical_contract_id'];reason=packet['positive_retirement_evidence']['reason']
  for f in row['v2_evidence']['independently_enumerated_files']:
   if 'sha256' not in f:proof['refusal_reasons'].append('UNACQUIRED_ENTRY');continue
   data=(root/f['path']).read_bytes();assert hashlib.sha256(data).hexdigest()==f['sha256'];tree=ast.parse(data.decode());parents={c:n for n in ast.walk(tree) for c in ast.iter_child_nodes(n)}
   for node in ast.walk(tree):
    if isinstance(node,ast.Name) and node.id=='RETIRED_CONTRACTS':
     proof['name_occurrences'].append({'path':f['path'],'line':node.lineno,'context':type(node.ctx).__name__})
     parent=parents.get(node)
     if isinstance(node.ctx,ast.Store) and isinstance(parent,ast.Assign) and len(parent.targets)==1 and parent.targets[0] is node and isinstance(parents.get(parent),ast.Module):
      try:value=ast.literal_eval(parent.value)
      except (ValueError,TypeError,SyntaxError,RecursionError):value=None
      if f['path']=='api.py' and isinstance(value,dict) and value.get(cid)==reason:proof['module_literal_candidates'].append({'path':f['path'],'line':node.lineno,'identity':cid,'reason':reason,'source_sha256':f['sha256']})
    named=(isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and node.name=='RETIRED_CONTRACTS' or isinstance(node,ast.arg) and node.arg=='RETIRED_CONTRACTS' or isinstance(node,ast.ExceptHandler) and node.name=='RETIRED_CONTRACTS' or isinstance(node,(ast.MatchAs,ast.MatchStar)) and node.name=='RETIRED_CONTRACTS' or isinstance(node,ast.MatchMapping) and node.rest=='RETIRED_CONTRACTS' or isinstance(node,(ast.Global,ast.Nonlocal)) and 'RETIRED_CONTRACTS' in node.names or isinstance(node,ast.alias) and (node.asname or node.name.split('.')[0])=='RETIRED_CONTRACTS')
    if named:proof['other_named_bindings'].append({'path':f['path'],'line':getattr(node,'lineno',None),'kind':type(node).__name__})
    if isinstance(node,ast.Attribute) and node.attr=='__globals__':proof['namespace_attributes'].append({'path':f['path'],'line':node.lineno,'expression':ast.unparse(node)})
  if len(proof['name_occurrences'])!=1:proof['refusal_reasons'].append('NONUNIQUE_OR_READ_DELETED_REGISTRY_NAME')
  if len(proof['module_literal_candidates'])!=1:proof['refusal_reasons'].append('NO_UNIQUE_UNCONDITIONAL_MODULE_LITERAL_IDENTITY_REASON')
  if proof['other_named_bindings']:proof['refusal_reasons'].append('OTHER_DECLARATION_OR_CAPTURE_BINDING')
  if proof['namespace_attributes']:proof['refusal_reasons'].append('UNADMITTED_NAMESPACE_ATTRIBUTE_NOT_PROVEN_MUTATION')
  if proof['refusal_reasons']:row['v7_action']='INCONCLUSIVE'
 records.append(row)
labels=['ADD','MODIFY','REMOVE','NO-OP','INCONCLUSIVE'];cohorts=[]
def rate(n,d):return {'numerator':n,'denominator':d,'ratio':n/d if d else None}
for cohort in sorted({x['cohort'] for x in records}):
 subset=[x for x in records if x['cohort']==cohort];conditions={}
 for field in ['v6_action','v7_action']:
  m={x:{y:0 for y in labels} for x in labels}
  for row in subset:m[row['reference']][row[field]]+=1
  support={x:sum(m[x].values()) for x in labels};conditions[field]={'matrix_reference_rows_predicted_columns':m,'reference_support':support,'exact_agreement':rate(sum(m[x][x] for x in labels),len(subset)),'false_remove':rate(sum(m[x]['REMOVE'] for x in labels if x!='REMOVE'),len(subset)-support['REMOVE']),'remove_recall':rate(m['REMOVE']['REMOVE'],support['REMOVE']),'unnecessary_abstention_on_remove':rate(m['REMOVE']['INCONCLUSIVE'],support['REMOVE']),'missed_modify':rate(support['MODIFY']-m['MODIFY']['MODIFY'],support['MODIFY']),'justified_abstention':rate(m['INCONCLUSIVE']['INCONCLUSIVE'],support['INCONCLUSIVE'])}
 cohorts.append({'cohort':cohort,'cases':len(subset),'conditions':conditions})
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':'scope-retirement-filter-protocol-v7.json','records':records,'unique_cases':len(records),'cohorts':cohorts,'old_planner_observations_reused_no_rerun':True,'source_controls_executed':False,'no_promotions_from_INCONCLUSIVE':True,'scope':'V7 strengthens finite retirement evidence, with deliberate conservative false abstentions measured. No real catalog ownership/authority, generic source completeness, namespace safety or runtime removal proof. MODIFY remains same as V6; previous utility losses retained.','gold':0,'optimizer_updates':0,'model_calls':0}
with (P/'scope-retirement-filter-results-v7.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
for c in cohorts:
 if 'retirement' in c['cohort']:print(json.dumps(c,indent=2))
