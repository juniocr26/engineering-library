"""First observations on frozen namespace controls; never execute their source."""
import ast,copy,datetime,hashlib,json,os,runpy,sys,collections
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];protocol=json.loads((P/'scope-function-namespace-protocol-v1.json').read_text())
for item in protocol['frozen_observers']:assert hashlib.sha256((P/item['path']).read_bytes()).hexdigest()==item['sha256']
original=json.loads((P/'independent-scope-acquisition-protocol-v1.json').read_text());ns={'ast':ast,'copy':copy,'datetime':datetime,'hashlib':hashlib,'json':json,'os':os,'Path':Path,'collections':collections,'ROOT':ROOT,'HERE':P,'bounds':original['gate_frozen']}
for name,names in [('run_scope_acquisition_v1.py',{'digest','metadata_inventory','acquire'}),('compare_scope_binding_owners_v2.py',{'own_scope_declarations','binding_owner','acquire_v2'}),('observe_scope_continuity_utility_v3.py',{'v3_action'}),('observe_scope_binding_census_v4.py',{'OuterBindingEvents','provider_chain'})]:
 tree=ast.parse((P/name).read_text());defs=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names];assert len(defs)==len(names)
 for n in tree.body:
  if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ALLOW_PREFIX' for t in n.targets):ns['ALLOW_PREFIX']=ast.literal_eval(n.value)
 exec(compile(ast.Module(body=defs,type_ignores=[]),name,'exec'),ns)
 if 'acquire' in ns:ns['acquire_v1']=ns['acquire']
ns['ns']=ns;ns['COMPS']=(ast.ListComp,ast.SetComp,ast.DictComp,ast.GeneratorExp)
tree=ast.parse((P/'observe_scope_registry_profile_v5.py').read_text());defs=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in ['ScopedBindingEvents','comprehension_owned_load','chain']];assert len(defs)==3;exec(compile(ast.Module(body=defs,type_ignores=[]),'frozen-v5-definitions','exec'),ns)
sys.path.insert(0,str(ROOT/'agent/tools'));planner=runpy.run_path(str(ROOT/'agent/tools/documentation_lifecycle.py'));records=[]
for case in protocol['cases']:
 pf=ROOT/case['packet'];assert hashlib.sha256(pf.read_bytes()).hexdigest()==case['packet_sha256'];packet=json.loads(pf.read_text());root=ROOT/case['source_root']
 for f in case['files']:assert hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256']
 baseline=planner['decision'](packet)['action'];v2=ns['acquire_v2'](case,packet);v2label='INCONCLUSIVE' if baseline=='REMOVE' and not v2['closed_snapshot_remove_admissible'] else baseline;v3,proof=ns['v3_action'](case,packet,v2,v2label);v5=v3;checks=[];reasons=[]
 if v3=='MODIFY':
  observations={}
  for f in v2['independently_enumerated_files']:
   if 'sha256' not in f:continue
   raw=(root/f['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==f['sha256'];tree=ast.parse(raw.decode());visitor=ns['ScopedBindingEvents'](tree);visitor.visit(tree);parents={c:n for n in ast.walk(tree) for c in ast.iter_child_nodes(n)};observations[f['path']]=(tree,visitor.events,parents)
  required=[(m['path'],'CONTRACTS') for m in proof['matched_markers']]
  for provider in proof['resolved_providers']:required.extend((part['path'],part['name']) for part in ns['chain'](provider))
  for path,name in required:
   tree,events,parents=observations[path];selected=[e for e in events if e['name']==name];checks.append({'path':path,'name':name,'events':selected,'count':len(selected)})
   if len(selected)!=1:reasons.append('NONUNIQUE_CORRECTED_BINDING:'+path+':'+name)
  for marker in proof['matched_markers']:
   tree,events,parents=observations[marker['path']]
   for node in ast.walk(tree):
    if isinstance(node,ast.Name) and node.id=='CONTRACTS' and isinstance(node.ctx,ast.Load) and not ns['comprehension_owned_load'](node,parents):reasons.append('UNADMITTED_IDENTITY_REGISTRY_ACCESS_OR_ESCAPE:'+marker['path']+':'+str(node.lineno))
  if reasons:v5='INCONCLUSIVE'
 row={'id':case['id'],'cohort':'new-function-namespace-challenge-6','reference':case['reference_action'],'reference_reason':case['reference_reason'],'baseline_action':baseline,'v2_action':v2label,'v3_action':v3,'v5_action':v5,'v2_evidence':v2,'v3_evidence':proof,'v5_profile':{'checks':checks,'refusal_reasons':reasons},'control_source_executed':False}
 with (pf.parent/'namespace-observation-v1.json').open('x') as f:json.dump(row,f,indent=2);f.write('\n')
 records.append(row)
labels=['ADD','MODIFY','REMOVE','NO-OP','INCONCLUSIVE']
def rate(n,d):return {'numerator':n,'denominator':d,'ratio':n/d if d else None}
conditions={}
for field in ['baseline_action','v2_action','v3_action','v5_action']:
 m={r:{c:0 for c in labels} for r in labels}
 for row in records:m[row['reference']][row[field]]+=1
 s={r:sum(m[r].values()) for r in labels};conditions[field]={'matrix_reference_rows_predicted_columns':m,'reference_support':s,'exact_agreement':rate(sum(m[l][l] for l in labels),len(records)),'false_remove':rate(sum(m[l]['REMOVE'] for l in labels if l!='REMOVE'),len(records)-s['REMOVE']),'false_modify':rate(sum(m[l]['MODIFY'] for l in labels if l!='MODIFY'),len(records)-s['MODIFY']),'missed_modify':rate(s['MODIFY']-m['MODIFY']['MODIFY'],s['MODIFY']),'justified_abstention':rate(m['INCONCLUSIVE']['INCONCLUSIVE'],s['INCONCLUSIVE'])}
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':'scope-function-namespace-protocol-v1.json','records':records,'conditions':conditions,'no_reference_changes':True,'old46case_observations_unchanged':True,'interpretation':'No general stability/safety follows from old V5zero falseMODIFY. Finite lexical names are not complete namespace/object ownership analysis; exact failure rates below, with readonly/unrelated positive controls retained. Source not executed and runtime not measured.','model_calls':0,'optimizer_updates':0,'gold':0,'permanent_tests_added':False}
with (P/'scope-function-namespace-results-v1.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'individual_actions':[(r['id'],r['reference'],r['v3_action'],r['v5_action']) for r in records],'v5_rates':conditions['v5_action']},indent=2))
