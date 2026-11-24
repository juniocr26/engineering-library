"""Positive continuity utility in an owned lexical oracle; no production changes."""
import ast,copy,datetime,hashlib,json,os,runpy,sys,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
original=json.loads((HERE/'independent-scope-acquisition-protocol-v1.json').read_text())
challenge=json.loads((HERE/'scope-binding-owner-challenge-protocol-v2.json').read_text())
protocol=json.loads((HERE/'scope-continuity-utility-protocol-v3.json').read_text())
prior=json.loads((HERE/'scope-binding-owner-comparison-results-v2.json').read_text());old={r['id']:r for r in prior['records']}
namespace={'ast':ast,'copy':copy,'datetime':datetime,'hashlib':hashlib,'json':json,'os':os,'Path':Path,'ROOT':ROOT,'HERE':HERE,'bounds':original['gate_frozen']}
for name,functions in [('run_scope_acquisition_v1.py',{'digest','metadata_inventory','acquire'}),('compare_scope_binding_owners_v2.py',{'own_scope_declarations','binding_owner','acquire_v2'})]:
    tree=ast.parse((HERE/name).read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in functions];assert len(defs)==len(functions)
    exec(compile(ast.Module(body=defs,type_ignores=[]),name,'exec'),namespace)
    if 'acquire' in namespace:namespace['acquire_v1']=namespace['acquire']
acquire_v2=namespace['acquire_v2'];binding_owner=namespace['binding_owner']
sys.path.insert(0,str(ROOT/'agent/tools'));planner=runpy.run_path(str(ROOT/'agent/tools/documentation_lifecycle.py'))
ALLOW_PREFIX=('POTENTIAL_CONTINUING_DECLARATION:','POTENTIAL_CONTINUING_BINDING:','MODULE_CLASS_BINDING_CONTINUITY_UNRESOLVED:','IMPORT_SCOPE_UNRESOLVED:')
def v3_action(case,packet,v2,filtered):
    evidence={'runtime_semantics_admitted':False,'source_only_citation_maintenance':True,'independent_scope_flags_not_generator_booleans':True,'matched_markers':[],'resolved_providers':[],'refusal_reasons':[]}
    fatal=[r for r in v2['refusal_reasons'] if not r.startswith(ALLOW_PREFIX)]
    if fatal:evidence['refusal_reasons']=fatal;return 'INCONCLUSIVE',evidence
    trees={};files={};bindings={};imports=[];global_rebinding=False
    root=ROOT/case['source_root']
    for f in v2['independently_enumerated_files']:
        if 'sha256' not in f:continue
        raw=(root/f['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==f['sha256']
        tree=ast.parse(raw.decode());module=str(Path(f['path']).with_suffix('')).replace('/','.');trees[module]=tree;files[module]=f
        parents={c:n for n in ast.walk(tree) for c in ast.iter_child_nodes(n)};table=collections.defaultdict(list)
        for n in ast.walk(tree):
            if isinstance(n,(ast.Global,ast.Nonlocal)):global_rebinding=True
            if isinstance(n,ast.Call):evidence['refusal_reasons'].append('SOURCE_CALL_OUTSIDE_CONTINUITY_PROFILE:'+f['path'])
            if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and binding_owner(n,parents,n.name)=='MODULE':
                table[n.name].append({'kind':type(n).__name__,'node':n,'line':n.lineno,'conditional':not isinstance(parents.get(n),ast.Module)})
            if isinstance(n,(ast.Assign,ast.AnnAssign)):
                targets=n.targets if isinstance(n,ast.Assign) else [n.target]
                for target in targets:
                    if isinstance(target,ast.Name) and binding_owner(target,parents,target.id)=='MODULE':
                        if target.id=='CONTRACTS':
                            if not isinstance(parents.get(n),ast.Module):evidence['refusal_reasons'].append('CONDITIONAL_IDENTITY_REGISTRY:'+f['path']);continue
                            try:registry=ast.literal_eval(n.value)
                            except (ValueError,TypeError,SyntaxError):registry=None
                            if not isinstance(registry,dict) or any(not isinstance(k,str) or not isinstance(v,str) for k,v in registry.items()):evidence['refusal_reasons'].append('NONLITERAL_IDENTITY_REGISTRY:'+f['path']);continue
                            if packet['logical_contract_id'] in registry:evidence['matched_markers'].append({'module':module,'path':f['path'],'line':n.lineno,'name':registry[packet['logical_contract_id']]})
                        else:table[target.id].append({'kind':'Lambda' if isinstance(n.value,ast.Lambda) else 'UnsupportedAssignment','node':n,'line':n.lineno,'conditional':not isinstance(parents.get(n),ast.Module)})
            if isinstance(n,ast.ImportFrom) and binding_owner(n,parents,'__import_binding__')=='MODULE':
                for alias in n.names:
                    row={'kind':'ImportFrom','node':n,'line':n.lineno,'module':n.module,'imported':alias.name,'level':n.level,'conditional':not isinstance(parents.get(n),ast.Module)}
                    table[alias.asname or alias.name].append(row);imports.append((module,alias.asname or alias.name))
            if isinstance(n,ast.Import):evidence['refusal_reasons'].append('UNADMITTED_IMPORT:'+f['path'])
        bindings[module]=table
    if global_rebinding:evidence['refusal_reasons'].append('GLOBAL_OR_NONLOCAL_REBINDING')
    if not evidence['matched_markers']:
        return ('INCONCLUSIVE' if evidence['refusal_reasons'] else filtered),evidence
    if len(evidence['matched_markers'])!=1:evidence['refusal_reasons'].append('AMBIGUOUS_MULTIPLE_CONTINUITY_PROVIDERS')
    def resolve(module,name,trail=()):
        if (module,name) in trail:raise ValueError('REEXPORT_CYCLE')
        if module not in bindings:raise ValueError('MISSING_LOCAL_SOURCE_MODULE')
        choices=bindings[module].get(name,[])
        if len(choices)!=1:raise ValueError('MISSING_OR_AMBIGUOUS_MODULE_BINDING')
        b=choices[0];n=b['node'];kind=b['kind']
        if kind=='ImportFrom':
            if b['level'] or not b['module'] or b['imported']=='*':raise ValueError('UNADMITTED_IMPORT_FORM')
            target=resolve(b['module'],b['imported'],trail+((module,name),))
            return {'module':module,'path':files[module]['path'],'name':name,'kind':'REEXPORT','line':b['line'],'conditional_source_declaration':b['conditional'],'target':target}
        if kind not in ['FunctionDef','AsyncFunctionDef','ClassDef','Lambda']:raise ValueError('UNADMITTED_BINDING_KIND')
        if kind!='Lambda' and getattr(n,'decorator_list',[]):raise ValueError('DECORATED_PROVIDER_UNRESOLVED')
        if kind=='ClassDef' and (n.bases or n.keywords):raise ValueError('CLASS_BASES_UNRESOLVED')
        return {'module':module,'path':files[module]['path'],'name':name,'kind':kind,'line':b['line'],'conditional_source_declaration':b['conditional']}
    if not evidence['refusal_reasons']:
        try:
            for module,name in imports:resolve(module,name)
            marker=evidence['matched_markers'][0];evidence['resolved_providers'].append(resolve(marker['module'],marker['name']))
        except ValueError as e:evidence['refusal_reasons'].append(str(e))
    if evidence['refusal_reasons']:return 'INCONCLUSIVE',evidence
    provider=evidence['resolved_providers'][0];previous_path=packet['metadata']['previous_path'];old_leaf=Path(previous_path).name
    docs=packet['documentation']
    if not all(previous_path in docs[lang] and packet['metadata']['selector'] in docs[lang] for lang in ['en','pt-br']):evidence['refusal_reasons'].append('EXISTING_SOURCE_POINTER_NOT_ESTABLISHED');return 'INCONCLUSIVE',evidence
    if provider['path']==old_leaf:evidence['refusal_reasons'].append('NO_PROVEN_CITATION_LOCATION_CHANGE');return 'INCONCLUSIVE',evidence
    evidence['maintenance_reason']='Unique source-registered continuing module provider is outside the frozen old source citation; propose citation maintenance, not runtime feature validity.'
    evidence['document_provenance_limit']='Existing EN/PT pointer text is supplied by frozen owned packet, not independently acquired from a real active catalog.'
    return 'MODIFY',evidence
records=[]
for case in original['cases']+challenge['new_cases']+protocol['new_cases']:
    pf=ROOT/case['packet'];assert hashlib.sha256(pf.read_bytes()).hexdigest()==case['packet_sha256'];packet=json.loads(pf.read_text());root=ROOT/case['source_root']
    for f in case['files']:
        path=root/f['path']
        if f['kind']=='symlink':assert path.is_symlink() and os.readlink(path)==f['target']
        else:assert hashlib.sha256(path.read_bytes()).hexdigest()==f['sha256']
    if case['id'] in old:
        previous=old[case['id']];baseline=previous['baseline_action'];v2_label=previous['v2_action'];v2=copy.deepcopy(previous['v2_evidence']);origin='Reuse exact terminal baseline/V2 labels and evidence; V3 bounded rechecks of source hashes/markers only.';cohort=previous['cohort']
    else:
        baseline=planner['decision'](packet)['action'];v2=acquire_v2(case,packet);v2_label='INCONCLUSIVE' if baseline=='REMOVE' and not v2['closed_snapshot_remove_admissible'] else baseline;origin='New frozen challenge; first actual baseline/V2 observation.';cohort='new-continuity-challenge-8'
    action,evidence=v3_action(case,packet,v2,v2_label)
    row={'id':case['id'],'cohort':cohort,'reference':case['reference_action'],'reference_reason':case['reference_reason'],'baseline_action':baseline,'v2_action':v2_label,'v3_action':action,'v3_evidence':evidence,'v2_evidence':v2,'origin':origin,'documents_modified':False}
    with (pf.parent/'continuity-utility-observation-v3.json').open('x') as f:json.dump(row,f,indent=2);f.write('\n')
    records.append(row)
labels=['ADD','MODIFY','REMOVE','NO-OP','INCONCLUSIVE']
def ratio(n,d):return {'numerator':n,'denominator':d,'ratio':n/d if d else None}
cohorts=[]
for cohort in ['original-exposed-11','new-owner-challenge-7','new-continuity-challenge-8']:
    rows=[r for r in records if r['cohort']==cohort];conditions={}
    for field in ['baseline_action','v2_action','v3_action']:
        matrix={r:{c:0 for c in labels} for r in labels}
        for row in rows:matrix[row['reference']][row[field]]+=1
        support={r:sum(matrix[r].values()) for r in labels}
        conditions[field]={'matrix_reference_rows_observed_columns':matrix,'reference_support':support,'exact_agreement':ratio(sum(matrix[l][l] for l in labels),len(rows)),'false_remove':ratio(sum(matrix[l]['REMOVE'] for l in labels if l!='REMOVE'),len(rows)-support['REMOVE']),'false_modify':ratio(sum(matrix[l]['MODIFY'] for l in labels if l!='MODIFY'),len(rows)-support['MODIFY']),'missed_modify':ratio(support['MODIFY']-matrix['MODIFY']['MODIFY'],support['MODIFY']),'justified_abstention':ratio(matrix['INCONCLUSIVE']['INCONCLUSIVE'],support['INCONCLUSIVE']),'unnecessary_abstention_on_remove':ratio(matrix['REMOVE']['INCONCLUSIVE'],support['REMOVE'])}
    cohorts.append({'cohort':cohort,'cases':len(rows),'conditions':conditions})
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':'scope-continuity-utility-protocol-v3.json','records':records,'cohorts':cohorts,'production_planner_version':planner['VERSION'],'limits':['Owned development lexical oracle only; source registry text is not production or runtime authority.','Conditional source declarations may support source-citation maintenance while runtime semantics remain unadmitted.','Source-pointer documentation is frozen owned packet text, not an independently acquired real catalog.','No ADD/NOOP references here; no global lifecycle accuracy or independent holdout claim.','No budgets increased; large/incomplete/ambiguous source remains inconclusive.'],'model_calls':0,'optimizer_updates':0,'gold':0,'production_changes':False,'permanent_tests_added':False}
with (HERE/'scope-continuity-utility-results-v3.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
for c in cohorts:print(json.dumps({'cohort':c['cohort'],'rates':{k:{m:v for m,v in d.items() if m not in ['matrix_reference_rows_observed_columns','reference_support']} for k,d in c['conditions'].items()}},indent=2))
