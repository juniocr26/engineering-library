"""Fresh Git/AST proof plus finite-template document binding; no general prose verifier."""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess

P=Path(__file__).resolve().parent
class DocumentRefused(ValueError):pass

def owned_module(name,filename,expected):
    path=P/filename
    if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise DocumentRefused('registered own implementation changed')
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def fresh_sources():
    contract=json.loads((P/'python-cache-document-binding-contract-v1.json').read_text())
    reviewer=owned_module('separate_source_review',contract['source_verifier_file'],contract['source_verifier_sha256'])
    renderer=owned_module('fixed_profile_renderer',contract['renderer_file'],contract['renderer_sha256'])
    sources,identities=reviewer.reacquire()
    registry=json.loads((P/'source-freeze-v1.json').read_text())['files'];api=json.loads((P/'python-cache-example-api-shape-v1.json').read_text());repos=json.loads((P/'collection-inventory-v2.json').read_text())['repositories'];repo=next(r for r in repos if r['repository']=='fastapi')
    for name in ['tests/test_dependency_cache.py','LICENSE']:
        row=next(r for r in registry if r['repository']=='fastapi' and r['path']==name)
        raw=subprocess.check_output(['git','-c','core.fsmonitor=false','-C',repo['absolute_path'],'show',row['revision']+':'+name],env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'),timeout=15)
        if hashlib.sha256(raw).hexdigest()!=row['sha256']:raise DocumentRefused('test/license source differs')
        sources[name]=raw.decode();identities.append({'path':name,'revision':row['revision'],'sha256':row['sha256']})
    for row in api['sources']:
        raw=subprocess.check_output(['git','-c','core.fsmonitor=false','-C',repo['absolute_path'],'show',row['revision']+':'+row['path']],env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'),timeout=15)
        if len(raw)>512000 or hashlib.sha256(raw).hexdigest()!=row['sha256']:raise DocumentRefused('API source differs')
        sources[row['path']]=raw.decode();identities.append({'path':row['path'],'revision':row['revision'],'sha256':row['sha256']})
    return contract,reviewer,renderer,sources,identities

def verify_pair(documents,observation,context):
    contract,reviewer,renderer,sources,identities=context
    proof=reviewer.verify_observation(observation,sources,identities)
    if set(documents)!={'en','pt-BR'} or any(not isinstance(v,bytes) for v in documents.values()):raise DocumentRefused('complete bilingual byte pair required')
    expected=renderer.render(observation)
    for language in ['en','pt-BR']:
        if documents[language]!=expected[language]:raise DocumentRefused('document outside frozen finite rendering profile')
    ast.parse(renderer.EXAMPLE)
    init=ast.parse(sources['fastapi/__init__.py']);exports=[n for n in init.body if isinstance(n,ast.ImportFrom) and n.level==1 and n.module=='param_functions' and any(a.name=='Depends' and a.asname in [None,'Depends'] for a in n.names)]
    if len(exports)!=1:raise DocumentRefused('Depends export shape differs')
    api=ast.parse(sources['fastapi/param_functions.py']);functions=[n for n in api.body if isinstance(n,ast.FunctionDef) and n.name=='Depends']
    if len(functions)!=1:raise DocumentRefused('Depends declaration missing/ambiguous')
    fn=functions[0];pos=fn.args.posonlyargs+fn.args.args;kw={a.arg:default for a,default in zip(fn.args.kwonlyargs,fn.args.kw_defaults)}
    if not pos or pos[0].arg!='dependency' or not isinstance(kw.get('use_cache'),ast.Constant) or kw['use_cache'].value is not True:raise DocumentRefused('example keyword contract differs')
    tests=ast.parse(sources['tests/test_dependency_cache.py']);written=[]
    for name in ['test_normal_counter','test_sub_counter','test_sub_counter_no_cache']:
        fs=[n for n in tests.body if isinstance(n,ast.FunctionDef) and n.name==name]
        if len(fs)!=1 or not any(isinstance(n,ast.Assert) for n in ast.walk(fs[0])):raise DocumentRefused('required written test evidence absent')
        gets=[n for n in ast.walk(fs[0]) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='get' and isinstance(n.func.value,ast.Name) and n.func.value.id=='client']
        if len(gets)<2:raise DocumentRefused('repeated-request written evidence absent')
        written.append({'name':name,'written_client_get_calls':len(gets),'executed':False})
    if 'Permission is hereby granted, free of charge' not in sources['LICENSE']:raise DocumentRefused('registered MIT notice not established')
    return {'profile_status':'SOURCE_RULES_AND_FINITE_TEXT_BINDING_VERIFIED','source_rule_groups':len(proof['checks']),'written_tests':written,'fresh_source_identities':identities,'paired_documents':True,'faq_pairs':len(renderer.FAQ),'example_syntax_and_import_keyword_shape':True,'external_program_or_tests_executed':False,'runtime_or_whole_program_typechecking':False,'general_semantic_verification':False,'manual_semantic_review_still_required':True,'owner_approved':False,'training_gold':False}

if __name__=='__main__':
    context=fresh_sources();contract,reviewer,_,_,_=context;raw=(P/contract['observation_file']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=contract['observation_sha256']:raise DocumentRefused('observation changed after contract freeze')
    observation=reviewer.strict(raw);index=json.loads((P/contract['candidate_index']).read_text());documents={}
    for row in index['files']:
        data=Path(row['path']).read_bytes()
        if hashlib.sha256(data).hexdigest()!=row['sha256']:raise DocumentRefused('candidate index bytes changed')
        documents[row['language']]=data
    result=verify_pair(documents,observation,context)
    with (P/'python-cache-document-source-binding-review-v1.json').open('x') as out:out.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['profile_status'],'source_rule_groups':result['source_rule_groups'],'manual_semantic_review_required':True}))
