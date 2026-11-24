"""Bounded lexical V5 filter; conservatively refuse registry escapes, no source execution."""
import ast,collections,datetime,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
protocol=json.loads((HERE/'scope-registry-profile-protocol-v5.json').read_text())
prior=[]
for item in protocol['frozen_prior_results']:
 raw=(HERE/item['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==item['sha256'];prior.extend(json.loads(raw)['records'])
prior.extend(json.loads((HERE/'scope-registry-profile-baselines-v1.json').read_text())['records'])
cases={}
for n,k in [('independent-scope-acquisition-protocol-v1.json','cases'),('scope-binding-owner-challenge-protocol-v2.json','new_cases'),('scope-continuity-utility-protocol-v3.json','new_cases'),('scope-binding-deletion-challenge-protocol-v1.json','cases'),('scope-object-mutation-protocol-v1.json','cases'),('scope-registry-profile-protocol-v5.json','new_cases')]:
 for c in json.loads((HERE/n).read_text())[k]:cases[c['id']]=c
ns={'ast':ast}
tree=ast.parse((HERE/'observe_scope_binding_census_v4.py').read_text());defs=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='OuterBindingEvents'];exec(compile(ast.Module(body=defs,type_ignores=[]),'frozen-v4-census','exec'),ns)
COMPS=(ast.ListComp,ast.SetComp,ast.DictComp,ast.GeneratorExp)
class ScopedBindingEvents(ns['OuterBindingEvents']):
 def __init__(self,tree):
  super().__init__();self.induction_nodes=set()
  for node in ast.walk(tree):
   if isinstance(node,COMPS):
    for generator in node.generators:self.induction_nodes.update(id(t) for t in ast.walk(generator.target) if isinstance(t,ast.Name) and isinstance(t.ctx,ast.Store))
 def visit_Name(self,node):
  if id(node) not in self.induction_nodes:super().visit_Name(node)
def comprehension_owned_load(node,parents):
 child=node;ancestor=parents.get(child)
 while ancestor is not None:
  if isinstance(ancestor,(ast.FunctionDef,ast.AsyncFunctionDef,ast.Lambda,ast.ClassDef)):return False
  if isinstance(ancestor,COMPS):
   names={t.id for g in ancestor.generators for t in ast.walk(g.target) if isinstance(t,ast.Name)}
   first_iter=ancestor.generators[0].iter
   inside_first=any(n is node for n in ast.walk(first_iter))
   if node.id in names and not inside_first:return True
  child=ancestor;ancestor=parents.get(child)
 return False
def chain(provider):
 yield provider
 if 'target' in provider:yield from chain(provider['target'])
records=[]
for old in prior:
 row=dict(old);row['v5_action']=row['v3_action'];checks=[];reasons=[];row['v5_profile']={'checks':checks,'refusal_reasons':reasons,'registry_escape_refusal_is_not_proof_of_mutation':True}
 if row['v3_action']=='MODIFY':
  case=cases[row['id']];root=ROOT/case['source_root'];observations={}
  for f in row['v2_evidence']['independently_enumerated_files']:
   if 'sha256' not in f:continue
   raw=(root/f['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==f['sha256'];tree=ast.parse(raw.decode());visitor=ScopedBindingEvents(tree);visitor.visit(tree);parents={c:n for n in ast.walk(tree) for c in ast.iter_child_nodes(n)};observations[f['path']]=(tree,visitor.events,parents)
  required=[(m['path'],'CONTRACTS') for m in row['v3_evidence']['matched_markers']]
  for provider in row['v3_evidence']['resolved_providers']:required.extend((part['path'],part['name']) for part in chain(provider))
  for path,name in required:
   tree,events,parents=observations[path];selected=[e for e in events if e['name']==name];checks.append({'path':path,'name':name,'corrected_event_count':len(selected),'events':selected})
   if len(selected)!=1:reasons.append('NONUNIQUE_CORRECTED_BINDING:'+path+':'+name)
  for marker in row['v3_evidence']['matched_markers']:
   tree,events,parents=observations[marker['path']]
   for node in ast.walk(tree):
    if isinstance(node,ast.Name) and node.id=='CONTRACTS' and isinstance(node.ctx,ast.Load) and not comprehension_owned_load(node,parents):reasons.append('UNADMITTED_IDENTITY_REGISTRY_ACCESS_OR_ESCAPE:'+marker['path']+':'+str(node.lineno))
  if reasons:row['v5_action']='INCONCLUSIVE'
 with (ROOT/cases[row['id']]['packet']).parent.joinpath('registry-profile-observation-v5.json').open('x') as f:json.dump(row,f,indent=2);f.write('\n')
 records.append(row)
labels=['ADD','MODIFY','REMOVE','NO-OP','INCONCLUSIVE']
def ratio(n,d):return {'numerator':n,'denominator':d,'ratio':n/d if d else None}
cohorts=[]
for cohort in sorted({r['cohort'] for r in records}):
 rows=[r for r in records if r['cohort']==cohort];conditions={}
 for field in ['v3_action','v4_action','v5_action']:
  matrix={r:{c:0 for c in labels} for r in labels}
  for row in rows:matrix[row['reference']][row[field]]+=1
  support={r:sum(matrix[r].values()) for r in labels}
  conditions[field]={'matrix_reference_rows_observed_columns':matrix,'reference_support':support,'exact_agreement':ratio(sum(matrix[l][l] for l in labels),len(rows)),'false_remove':ratio(sum(matrix[l]['REMOVE'] for l in labels if l!='REMOVE'),len(rows)-support['REMOVE']),'false_modify':ratio(sum(matrix[l]['MODIFY'] for l in labels if l!='MODIFY'),len(rows)-support['MODIFY']),'missed_modify':ratio(support['MODIFY']-matrix['MODIFY']['MODIFY'],support['MODIFY']),'justified_abstention':ratio(matrix['INCONCLUSIVE']['INCONCLUSIVE'],support['INCONCLUSIVE'])}
 cohorts.append({'cohort':cohort,'cases':len(rows),'conditions':conditions})
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':'scope-registry-profile-protocol-v5.json','records':records,'cohorts':cohorts,'limits':['Finite exposed source-only profile; registry access refusal is conservative and intentionally measured against valid readonly/distinct-key controls.','No production integration, generic alias analysis, runtime behavior, real catalog authority or independent evaluation.','No old observation rerun, no new ADD/NOOP reference support, no pooled general lifecycle accuracy.'],'model_calls':0,'optimizer_updates':0,'gold':0,'source_controls_executed':False,'permanent_tests_added':False}
with (HERE/'scope-registry-profile-results-v5.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
for c in cohorts:print(json.dumps({'cohort':c['cohort'],'v5':{k:v for k,v in c['conditions']['v5_action'].items() if k not in ['matrix_reference_rows_observed_columns','reference_support']}},indent=2))
