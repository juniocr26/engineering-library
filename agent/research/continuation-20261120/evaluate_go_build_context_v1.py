"""Run owned frozen context controls against preserved compiled observer."""
import copy
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

P=Path(__file__).resolve().parent
protocol=json.loads((P/'go-build-context-protocol-v1.json').read_text())
cases=[]
for case in protocol['controls']:
    files=[dict(f,sha256=hashlib.sha256(f['source'].encode()).hexdigest())for f in case['files']]
    expected=case['expected_selected']
    if expected=='DUPLICATE_PATH':files.append(copy.deepcopy(files[0]))
    cases.append({'id':case['id'],'request':{'context':protocol['context'],'files':files},
                  'expected_status':'INCONCLUSIVE'if expected is None or expected=='DUPLICATE_PATH'else'CONSTRAINT_MATCH_OBSERVATIONS',
                  'expected_selected':expected if isinstance(expected,list)else None,
                  'expected_flags':{'cgo_paths':['cgo.go']}if case['id']=='cgo-unknown-package-selection'else{}})
cases+=json.loads((P/'go-build-context-control-supplement-v1.json').read_text())['cases']
receipt=json.loads((P/'go-build-context-v1/build-artifacts/build-receipt.json').read_text())
freeze={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'binary_sha256':receipt['binary_sha256'],
        'source_sha256':receipt['original_source_sha256'],'cases':len(cases),'expected_inputs_frozen_before_predictions':True}
with(P/'go-build-context-evaluation-freeze-v1.json').open('x')as stream:json.dump(freeze,stream,indent=2)
rows=[]
command=['docker','exec','-i','engineering-library-backend-1','/tmp/el-cont-20261120-build-context-v2/build-artifacts/build-context-linux-arm64']
for case in cases:
    wire=(case.get('raw_request')or json.dumps(case['request'])).encode()
    result=subprocess.run(command,input=wire,capture_output=True,timeout=15)
    if result.returncode:body={'status':'PROCESS_FAILED','stderr':result.stderr.decode()}
    else:body=json.loads(result.stdout)
    checks={'status':body['status']==case['expected_status'],'source_not_executed':body.get('source_executed')is False}
    if case['expected_selected']is not None:checks['matched_paths']=body.get('matched_paths')==sorted(case['expected_selected'])
    if body['status']=='CONSTRAINT_MATCH_OBSERVATIONS':
        checks['no_package_or_runtime_promotion']=body['package_completeness_verified']is False and body['runtime_name_binding_verified']is False and body['source_compiled']is False
    flags=case['expected_flags']
    if 'cgo_paths'in flags:checks['cgo_unresolved']=body.get('matched_import_C_paths')==flags['cgo_paths']
    if 'ambiguous_dirs'in flags:checks['mixed_package_remains_ambiguous']=body.get('ambiguous_library_package_directories')==flags['ambiguous_dirs']
    if 'test_file'in flags:checks['test_not_library']=any(r['path']==flags['test_file']and r['test_file_not_default_library']and not r['library_census_input_candidate']for r in body.get('files',[]))
    rows.append({'id':case['id'],'checks':checks,'matches':all(checks.values()),'request_sha256':hashlib.sha256(wire).hexdigest(),'response_sha256':hashlib.sha256(result.stdout).hexdigest(),'result':body,'stderr':result.stderr.decode()})
report={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'correct':sum(r['matches']for r in rows),'n':len(rows),'rows':rows,
        'scope':'OWNED_BUILD_CONTEXT_CONTROLS_NOT_NEW_INDEPENDENT_SOURCE_FAMILIES','model_calls':0,'permanent_tests_changed':False}
with(P/'go-build-context-controls-v1.json').open('x')as stream:json.dump(report,stream,indent=2)
print(json.dumps({'correct':report['correct'],'n':report['n'],'failures':[{'id':r['id'],'result':r['result']}for r in rows if not r['matches']]}))
