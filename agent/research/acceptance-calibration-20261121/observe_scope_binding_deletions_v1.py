"""Falsification challenge for unchanged V3; never execute owned control source."""
import ast,copy,datetime,hashlib,json,os,runpy,sys,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
protocol=json.loads((HERE/'scope-binding-deletion-challenge-protocol-v1.json').read_text())
assert hashlib.sha256((HERE/protocol['frozen_prototype']).read_bytes()).hexdigest()==protocol['frozen_prototype_sha256']
original=json.loads((HERE/'independent-scope-acquisition-protocol-v1.json').read_text())
ns={'ast':ast,'copy':copy,'datetime':datetime,'hashlib':hashlib,'json':json,'os':os,'Path':Path,'collections':collections,'ROOT':ROOT,'HERE':HERE,'bounds':original['gate_frozen']}
for name,names in [('run_scope_acquisition_v1.py',{'digest','metadata_inventory','acquire'}),('compare_scope_binding_owners_v2.py',{'own_scope_declarations','binding_owner','acquire_v2'}),('observe_scope_continuity_utility_v3.py',{'v3_action'})]:
    tree=ast.parse((HERE/name).read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names];assert len(defs)==len(names)
    for n in tree.body:
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ALLOW_PREFIX' for t in n.targets):ns['ALLOW_PREFIX']=ast.literal_eval(n.value)
    exec(compile(ast.Module(body=defs,type_ignores=[]),name,'exec'),ns)
    if 'acquire' in ns:ns['acquire_v1']=ns['acquire']
sys.path.insert(0,str(ROOT/'agent/tools'));planner=runpy.run_path(str(ROOT/'agent/tools/documentation_lifecycle.py'));records=[]
for case in protocol['cases']:
    pf=ROOT/case['packet'];assert hashlib.sha256(pf.read_bytes()).hexdigest()==case['packet_sha256'];packet=json.loads(pf.read_text());root=ROOT/case['source_root']
    for f in case['files']:assert hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256']
    baseline=planner['decision'](packet);v2=ns['acquire_v2'](case,packet);v2_label='INCONCLUSIVE' if baseline['action']=='REMOVE' and not v2['closed_snapshot_remove_admissible'] else baseline['action'];v3_label,proof=ns['v3_action'](case,packet,v2,v2_label)
    row={'id':case['id'],'reference':case['reference_action'],'reference_reason':case['reference_reason'],'baseline_action':baseline['action'],'v2_action':v2_label,'v3_action':v3_label,'v2_evidence':v2,'v3_evidence':proof,'original_frozen_V3_unchanged':True,'control_source_executed':False,'documents_changed':False}
    with (pf.parent/'deletion-challenge-observation-v1.json').open('x') as f:json.dump(row,f,indent=2);f.write('\n')
    records.append(row)
labels=['ADD','MODIFY','REMOVE','NO-OP','INCONCLUSIVE']
def ratio(n,d):return {'numerator':n,'denominator':d,'ratio':n/d if d else None}
conditions={}
for field in ['baseline_action','v2_action','v3_action']:
    matrix={r:{c:0 for c in labels} for r in labels}
    for row in records:matrix[row['reference']][row[field]]+=1
    support={r:sum(matrix[r].values()) for r in labels}
    conditions[field]={'matrix_reference_rows_observed_columns':matrix,'reference_support':support,'exact_agreement':ratio(sum(matrix[l][l] for l in labels),len(records)),'false_remove':ratio(sum(matrix[l]['REMOVE'] for l in labels if l!='REMOVE'),len(records)-support['REMOVE']),'false_modify':ratio(sum(matrix[l]['MODIFY'] for l in labels if l!='MODIFY'),len(records)-support['MODIFY']),'missed_modify':ratio(support['MODIFY']-matrix['MODIFY']['MODIFY'],support['MODIFY']),'justified_abstention':ratio(matrix['INCONCLUSIVE']['INCONCLUSIVE'],support['INCONCLUSIVE'])}
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':'scope-binding-deletion-challenge-protocol-v1.json','cohort':'new-deletion-and-registry-order-challenge-6','records':records,'conditions':conditions,'interpretation':'Use the observed matrix to falsify broad safety claims. Earlier positive-continuity successes remain retained in separate exposed cohorts; no pooling into general lifecycle accuracy. V3 source tokens/identity markers are insufficient when binding deletion or registry reassignment is ignored.','not_production_ready':True,'no_reference_changes_or_output_repairs':True,'model_calls':0,'optimizer_updates':0,'gold':0,'permanent_tests_added':False}
with (HERE/'scope-binding-deletion-challenge-results-v1.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({k:{m:v for m,v in row.items() if m not in ['matrix_reference_rows_observed_columns','reference_support']} for k,row in conditions.items()},indent=2))
print('Individual actions',[(r['id'],r['reference'],r['v3_action']) for r in records])
