"""Normalize exact owned AST evidence; do not equate declaration with dispatch."""
from pathlib import Path
import datetime
import hashlib
import json
import re

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
OWNERS={'Base','Derived','Further','NotDerived'}
FUNCTIONS={'main','createAndRead','qualified','unqualified'}


def quote(raw,node):
    span=node.get('range',{})
    begin,end=span.get('begin',{}),span.get('end',{})
    if 'offset' not in begin or 'offset' not in end:
        return None
    return raw[begin['offset']:end['offset']+end.get('tokLen',0)].decode()


def projection(ast,raw):
    methods={}
    records=[]
    calls=[]
    using=[]

    def walk(node,owner=None,function=None):
        kind=node.get('kind')
        if kind=='CXXRecordDecl' and node.get('completeDefinition') and node.get('name') in OWNERS:
            owner=node['name']
            position=node['loc']['offset']
            assert raw[position:position+node['loc']['tokLen']].decode()==owner
            assert quote(raw,node).startswith('struct '+owner)
            records.append({'name':owner,'bases':node.get('bases',[]),'source_quote':quote(raw,node)})
        if kind=='CXXMethodDecl' and owner in OWNERS and not node.get('isImplicit'):
            label=owner+'::'+node['name']+' '+node['type']['qualType']
            function=label
            methods[node['id']]={'label':label,'owner':owner,'name':node['name'],
                'parameter_count':sum(c.get('kind')=='ParmVarDecl' for c in node.get('inner',[])),
                'virtual_JSON_field':node.get('virtual'),
                'override_attribute':any(c.get('kind')=='OverrideAttr' for c in node.get('inner',[])),
                'source_quote':quote(raw,node),'offset':node.get('loc',{}).get('offset')}
        if kind=='FunctionDecl' and node.get('name') in FUNCTIONS:
            function=node['name']+' '+node['type']['qualType']
        if kind in ['UsingDecl','UsingShadowDecl'] and owner in OWNERS:
            using.append({'owner':owner,'kind':kind,'name':node.get('name'),
                          'target_type':node.get('target',{}).get('type')})
        if kind=='CXXMemberCallExpr' and function:
            first=node.get('inner',[{}])[0]
            if first.get('kind')=='MemberExpr':
                calls.append({'function':function,'source_quote':quote(raw,node),
                              'member':first,'selected_ID':first.get('referencedMemberDecl')})
        for child in node.get('inner',[]):
            walk(child,owner,function)
    walk(ast)

    def normalize(node):
        if isinstance(node,list):return [normalize(x) for x in node]
        if not isinstance(node,dict):return node
        result={}
        for key,value in node.items():
            if key in ['id','loc','range']:continue
            if key=='referencedMemberDecl':value=methods.get(value,{}).get('label','UNRESOLVED')
            result[key]=normalize(value)
        return result

    for call in calls:
        call['selected_declaration']=methods.get(call.pop('selected_ID'),{}).get('label','UNRESOLVED')
        call['callee_JSON_without_locations_or_volatile_IDs']=normalize(call.pop('member'))
    return {'records':records,'methods':list(methods.values()),'calls':calls,'using_declarations':using}


acquisition=json.loads((P/'cpp-ast-dispatch-acquisition-v1.json').read_text())
results=[]
for row in acquisition['records']:
    source=ROOT/row['source']
    assert sha(source.read_bytes())==row['source_sha256']
    ast_file=ROOT/row['outputs']['ast.json']['path']
    assert sha(ast_file.read_bytes())==row['outputs']['ast.json']['sha256']
    observed=projection(json.loads(ast_file.read_text()),source.read_bytes())
    results.append({'id':row['id'],'compile_exit':row['exit_code'],
                    'admission':'STATIC_OWNED_AST_AVAILABLE' if row['exit_code']==0 else 'REFUSED_WHOLE_TRANSLATION_UNIT',
                    'partial_AST_never_promoted_on_error':True,'projection':observed})

pair_protocol=json.loads((P/'cpp-qualified-dispatch-protocol-v1.json').read_text())
pair_source=ROOT/pair_protocol['source']
assert sha(pair_source.read_bytes())==pair_protocol['source_sha256']
pair=projection(json.loads((pair_source.parent/'ast.json').read_text()),pair_source.read_bytes())
unqualified=next(c for c in pair['calls'] if c['function'].startswith('unqualified '))
qualified=next(c for c in pair['calls'] if c['function'].startswith('qualified '))
same_callee_JSON=(unqualified['callee_JSON_without_locations_or_volatile_IDs']==qualified['callee_JSON_without_locations_or_volatile_IDs'])
ir=(pair_source.parent/'ir.ll').read_text()


def ir_body(mangled):
    found=re.findall(r'^define[^\n]*@'+re.escape(mangled)+r'\([^\n]*\) [^\n]*\{\n(.*?)^\}',ir,re.M|re.S)
    assert len(found)==1,mangled
    return found[0]


unqualified_calls=[s.strip() for s in ir_body('_Z11unqualifiedR7Derived').splitlines() if 'call i32' in s]
qualified_calls=[s.strip() for s in ir_body('_Z9qualifiedR7Derived').splitlines() if 'call i32' in s]
assert len(unqualified_calls)==len(qualified_calls)==1
assert re.search(r'call i32 %\w+\(',unqualified_calls[0])
assert '@_ZNK4Base5valueEv(' in qualified_calls[0]
further=next(m for m in pair['methods'] if m['owner']=='Further' and m['name']=='value')
assert further['override_attribute'] is True
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'owned_prior_controls':results,
        'same_TU_pair_projection':pair,'same_TU_callee_JSON_equal_after_location_and_ID_normalization':same_callee_JSON,
        'IR_evidence':{'unqualified_calls':unqualified_calls,'qualified_calls':qualified_calls,
                       'target':'arm64-apple-macosx27.0.0','optimization':'O0','program_executed':False},
        'missing_virtual_field_on_override':{'override_attribute':further['override_attribute'],
                                             'virtual_JSON_field':further['virtual_JSON_field']},
        'finding':'For this owned pair the compiler selects the same Base declaration while emitted textual IR has indirect versus direct calls. Keep physical source qualification and override context; absent JSON fields cannot establish nonvirtual dispatch.',
        'scope':'Exact owned controls, native compiler and options only. No OpenCV/Raylib runtime or full-header compilation, inference, framework installation or generic C++ semantic verifier.',
        'new_independent_tasks':0,'neural_calls':0,'training_eligible':False}
with (P/'cpp-ast-dispatch-review-v1.json').open('x') as stream:
    json.dump(result,stream,indent=2)
    stream.write('\n')
print(json.dumps({'old_owned_controls':len(results),'partial_compile_errors_refused':sum(r['compile_exit']!=0 for r in results),
                  'same_TU_callee_JSON_equal':same_callee_JSON,'IR_calls_differ':True,
                  'override_virtual_field':further['virtual_JSON_field'],'targets_executed':False}))
