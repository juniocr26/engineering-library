"""Owner-qualified binding-event filter over unchanged V3 results."""
import ast,collections,datetime,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
protocol=json.loads((HERE/'scope-binding-census-protocol-v4.json').read_text())
input_rows=[]
for entry in protocol['frozen_input_results']:
    raw=(HERE/entry['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['sha256'];data=json.loads(raw)
    for row in data['records']:
        value=dict(row)
        if 'cohort' not in value:value['cohort']=data['cohort']
        input_rows.append(value)
cases={}
for name,key in [('independent-scope-acquisition-protocol-v1.json','cases'),('scope-binding-owner-challenge-protocol-v2.json','new_cases'),('scope-continuity-utility-protocol-v3.json','new_cases'),('scope-binding-deletion-challenge-protocol-v1.json','cases')]:
    for c in json.loads((HERE/name).read_text())[key]:cases[c['id']]=c
class OuterBindingEvents(ast.NodeVisitor):
    def __init__(self):self.events=[]
    def add(self,name,node,kind):self.events.append({'name':name,'line':getattr(node,'lineno',None),'kind':kind,'owner':'MODULE_EVALUATED_SCOPE'})
    def argument_expressions(self,node):
        args=node.args
        for expression in [*args.defaults,*[x for x in args.kw_defaults if x is not None]]:self.visit(expression)
        for arg in [*args.posonlyargs,*args.args,*args.kwonlyargs]+([args.vararg] if args.vararg else [])+([args.kwarg] if args.kwarg else []):
            if arg.annotation is not None:self.visit(arg.annotation)
    def visit_FunctionDef(self,node):
        self.add(node.name,node,type(node).__name__)
        for expression in node.decorator_list:self.visit(expression)
        self.argument_expressions(node)
        if node.returns is not None:self.visit(node.returns)
    visit_AsyncFunctionDef=visit_FunctionDef
    def visit_ClassDef(self,node):
        self.add(node.name,node,'ClassDef')
        for expression in [*node.decorator_list,*node.bases,*[x.value for x in node.keywords]]:self.visit(expression)
    def visit_Lambda(self,node):self.argument_expressions(node)
    def visit_Import(self,node):
        for alias in node.names:self.add(alias.asname or alias.name.split('.')[0],node,'Import')
    def visit_ImportFrom(self,node):
        for alias in node.names:self.add(alias.asname or alias.name,node,'ImportFrom')
    def visit_Name(self,node):
        if isinstance(node.ctx,(ast.Store,ast.Del)):self.add(node.id,node,type(node.ctx).__name__)
    def visit_ExceptHandler(self,node):
        if node.name:self.add(node.name,node,'ExceptCapture')
        self.generic_visit(node)
    def visit_MatchAs(self,node):
        if node.name:self.add(node.name,node,'MatchAs')
        self.generic_visit(node)
    def visit_MatchStar(self,node):
        if node.name:self.add(node.name,node,'MatchStar')
    def visit_MatchMapping(self,node):
        if node.rest:self.add(node.rest,node,'MatchMappingRest')
        self.generic_visit(node)
def provider_chain(p):
    yield p
    if 'target' in p:yield from provider_chain(p['target'])
records=[]
for previous in input_rows:
    row=dict(previous);row['v4_action']=row['v3_action'];row['v4_binding_census']={'applied_to_v3_modify_only':True,'checks':[],'refusal_reasons':[]}
    if row['v3_action']=='MODIFY':
        case=cases[row['id']];root=ROOT/case['source_root'];observations={}
        for f in row['v2_evidence']['independently_enumerated_files']:
            if 'sha256' not in f:continue
            raw=(root/f['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==f['sha256'];tree=ast.parse(raw.decode());visitor=OuterBindingEvents();visitor.visit(tree);observations[f['path']]={'source_sha256':f['sha256'],'events':visitor.events,'counts':dict(collections.Counter(e['name'] for e in visitor.events))}
        required=[]
        for marker in row['v3_evidence']['matched_markers']:required.append((marker['path'],'CONTRACTS','identity-registry'))
        for provider in row['v3_evidence']['resolved_providers']:
            for part in provider_chain(provider):required.append((part['path'],part['name'],'provider-or-reexport'))
        for path,name,role in required:
            observed=observations[path];events=[e for e in observed['events'] if e['name']==name];count=len(events);row['v4_binding_census']['checks'].append({'path':path,'source_sha256':observed['source_sha256'],'name':name,'role':role,'binding_event_count':count,'events':events})
            if count!=1:row['v4_binding_census']['refusal_reasons'].append('NONUNIQUE_MODULE_BINDING_EVENTS:'+path+':'+name)
        if row['v4_binding_census']['refusal_reasons']:row['v4_action']='INCONCLUSIVE'
    with (ROOT/cases[row['id']]['packet']).parent.joinpath('binding-census-observation-v4.json').open('x') as f:json.dump(row,f,indent=2);f.write('\n')
    records.append(row)
labels=['ADD','MODIFY','REMOVE','NO-OP','INCONCLUSIVE']
def ratio(n,d):return {'numerator':n,'denominator':d,'ratio':n/d if d else None}
cohorts=[]
for cohort in sorted({r['cohort'] for r in records}):
    rows=[r for r in records if r['cohort']==cohort];conditions={}
    for field in ['v2_action','v3_action','v4_action']:
        matrix={r:{c:0 for c in labels} for r in labels}
        for row in rows:matrix[row['reference']][row[field]]+=1
        support={r:sum(matrix[r].values()) for r in labels}
        conditions[field]={'matrix_reference_rows_observed_columns':matrix,'reference_support':support,'exact_agreement':ratio(sum(matrix[l][l] for l in labels),len(rows)),'false_remove':ratio(sum(matrix[l]['REMOVE'] for l in labels if l!='REMOVE'),len(rows)-support['REMOVE']),'false_modify':ratio(sum(matrix[l]['MODIFY'] for l in labels if l!='MODIFY'),len(rows)-support['MODIFY']),'missed_modify':ratio(support['MODIFY']-matrix['MODIFY']['MODIFY'],support['MODIFY']),'justified_abstention':ratio(matrix['INCONCLUSIVE']['INCONCLUSIVE'],support['INCONCLUSIVE'])}
    cohorts.append({'cohort':cohort,'cases':len(rows),'conditions':conditions})
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':'scope-binding-census-protocol-v4.json','records':records,'cohorts':cohorts,'interpretation':'Owner-qualified Store/Del event counts and identity-registry ownership filter unsupported positive source maintenance. This is development-exposed finite lexical evidence, not production admission or arbitrary runtime binding/feature semantics.','no_reference_changes_or_repairs':True,'old_baseline_V2_V3_observations_reused_without_rerun':True,'all_control_source_unexecuted':True,'model_calls':0,'optimizer_updates':0,'gold':0,'production_changes':False,'permanent_tests_added':False}
with (HERE/'scope-binding-census-results-v4.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
for c in cohorts:print(json.dumps({'cohort':c['cohort'],'v4':{k:v for k,v in c['conditions']['v4_action'].items() if k not in ['matrix_reference_rows_observed_columns','reference_support']}},indent=2))
