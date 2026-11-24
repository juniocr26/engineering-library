"""Frozen eight-control source-only falsification; owned control files never executed."""
import ast,copy,datetime,hashlib,json,os,runpy,sys,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
protocol=json.loads((HERE/'scope-object-mutation-protocol-v1.json').read_text())
for item in protocol['frozen_observers']:assert hashlib.sha256((HERE/item['path']).read_bytes()).hexdigest()==item['sha256']
original=json.loads((HERE/'independent-scope-acquisition-protocol-v1.json').read_text())
ns={'ast':ast,'copy':copy,'datetime':datetime,'hashlib':hashlib,'json':json,'os':os,'Path':Path,'collections':collections,'ROOT':ROOT,'HERE':HERE,'bounds':original['gate_frozen']}
for name,names in [('run_scope_acquisition_v1.py',{'digest','metadata_inventory','acquire'}),('compare_scope_binding_owners_v2.py',{'own_scope_declarations','binding_owner','acquire_v2'}),('observe_scope_continuity_utility_v3.py',{'v3_action'}),('observe_scope_binding_census_v4.py',{'OuterBindingEvents','provider_chain'})]:
 tree=ast.parse((HERE/name).read_text());defs=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names];assert len(defs)==len(names)
 for n in tree.body:
  if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ALLOW_PREFIX' for t in n.targets):ns['ALLOW_PREFIX']=ast.literal_eval(n.value)
 exec(compile(ast.Module(body=defs,type_ignores=[]),name,'exec'),ns)
 if 'acquire' in ns:ns['acquire_v1']=ns['acquire']
sys.path.insert(0,str(ROOT/'agent/tools'));planner=runpy.run_path(str(ROOT/'agent/tools/documentation_lifecycle.py'));records=[]
for case in protocol['cases']:
 pf=ROOT/case['packet'];assert hashlib.sha256(pf.read_bytes()).hexdigest()==case['packet_sha256'];packet=json.loads(pf.read_text());root=ROOT/case['source_root']
 for f in case['files']:assert hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256']
 baseline=planner['decision'](packet);v2=ns['acquire_v2'](case,packet);v2_label='INCONCLUSIVE' if baseline['action']=='REMOVE' and not v2['closed_snapshot_remove_admissible'] else baseline['action'];v3,proof=ns['v3_action'](case,packet,v2,v2_label);v4=v3;census={'checks':[],'refusal_reasons':[]}
 if v3=='MODIFY':
  observations={}
  for f in v2['independently_enumerated_files']:
   if 'sha256' not in f:continue
   raw=(root/f['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==f['sha256'];visitor=ns['OuterBindingEvents']();visitor.visit(ast.parse(raw.decode()));observations[f['path']]=visitor.events
  required=[(m['path'],'CONTRACTS') for m in proof['matched_markers']]
  for provider in proof['resolved_providers']:
   required.extend((part['path'],part['name']) for part in ns['provider_chain'](provider))
  for path,name in required:
   events=[e for e in observations[path] if e['name']==name];census['checks'].append({'path':path,'name':name,'events':events,'count':len(events)})
   if len(events)!=1:census['refusal_reasons'].append('NONUNIQUE_MODULE_BINDING_EVENTS:'+path+':'+name)
  if census['refusal_reasons']:v4='INCONCLUSIVE'
 row={'id':case['id'],'cohort':'new-object-mutation-and-comprehension-8','reference':case['reference_action'],'reference_reason':case['reference_reason'],'baseline_action':baseline['action'],'v2_action':v2_label,'v3_action':v3,'v4_action':v4,'v2_evidence':v2,'v3_evidence':proof,'v4_binding_census':census,'control_source_executed':False}
 with (pf.parent/'object-mutation-observation-v1.json').open('x') as f:json.dump(row,f,indent=2);f.write('\n')
 records.append(row)
labels=['ADD','MODIFY','REMOVE','NO-OP','INCONCLUSIVE']
def ratio(n,d):return {'numerator':n,'denominator':d,'ratio':n/d if d else None}
conditions={}
for field in ['baseline_action','v2_action','v3_action','v4_action']:
 matrix={r:{c:0 for c in labels} for r in labels}
 for row in records:matrix[row['reference']][row[field]]+=1
 support={r:sum(matrix[r].values()) for r in labels}
 conditions[field]={'matrix_reference_rows_observed_columns':matrix,'reference_support':support,'exact_agreement':ratio(sum(matrix[l][l] for l in labels),len(records)),'false_remove':ratio(sum(matrix[l]['REMOVE'] for l in labels if l!='REMOVE'),len(records)-support['REMOVE']),'false_modify':ratio(sum(matrix[l]['MODIFY'] for l in labels if l!='MODIFY'),len(records)-support['MODIFY']),'missed_modify':ratio(support['MODIFY']-matrix['MODIFY']['MODIFY'],support['MODIFY']),'justified_abstention':ratio(matrix['INCONCLUSIVE']['INCONCLUSIVE'],support['INCONCLUSIVE'])}
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':'scope-object-mutation-protocol-v1.json','cohort':'new-object-mutation-and-comprehension-8','records':records,'conditions':conditions,'no_reference_changes_or_output_repairs':True,'all_previous_observer_definitions_unchanged':True,'interpretation':'Binding-event uniqueness does not establish dictionary-object identity stability, and generic AST descent is not scope resolution. Falsification on exposed owned controls; no production changes or general safety/accuracy claim.','model_calls':0,'optimizer_updates':0,'gold':0,'permanent_tests_added':False}
with (HERE/'scope-object-mutation-results-v1.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'individual_actions':[(r['id'],r['reference'],r['v3_action'],r['v4_action']) for r in records],'rates':{k:{m:v for m,v in c.items() if m not in ['matrix_reference_rows_observed_columns','reference_support']} for k,c in conditions.items()}},indent=2))
