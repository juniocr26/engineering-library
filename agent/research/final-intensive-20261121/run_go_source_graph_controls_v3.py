import json,datetime,hashlib,subprocess
from pathlib import Path
p=Path(__file__).resolve().parent;folder=p/'go-source-graph-controls-v3';folder.mkdir();binary=p/'offline-go-type-observer-v5/observer';spec=[]
for parent in ['go-source-graph-controls-v1','go-source-graph-path-boundary-v1']:
 protocol=json.loads((p/parent/'protocol.json').read_text())
 for case in protocol['cases']:spec.append({'id':case['id'],'source_request':str((p/parent/(case['id']+'.request.json')).relative_to(p)),'expected':case['expected']})
(folder/'protocol.json').open('x').write(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'observer_binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'cases':spec,'role':'Original9ownedcontrols plus3newnamespace-boundary regressions; correlated development mechanisms, no independent score'},indent=2)+'\n');records=[]
for case in spec:
 raw=(p/case['source_request']).read_bytes();(folder/(case['id']+'.request.json')).open('xb').write(raw);r=subprocess.run([str(binary)],input=raw,capture_output=True,timeout=25);(folder/(case['id']+'.stdout.json')).open('xb').write(r.stdout);(folder/(case['id']+'.stderr.txt')).open('xb').write(r.stderr);packet=json.loads(r.stdout);assert r.returncode==0
 if packet['status']!='TYPECHECKED_FROZEN_SOURCE_GRAPH':assert not packet['relations'] and not packet['declarations'] and not packet['partial_type_info_admitted']
 records.append({'id':case['id'],'expected':case['expected'],'packet':packet,'matched':packet['status']==case['expected']})
(folder/'results.json').open('x').write(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'mechanism_expectations_matched':sum(x['matched'] for x in records),'total':len(records),'old_v3_namespace_failures_preserved':True,'target_source_executed':False,'model_calls':0},indent=2)+'\n');print(json.dumps({'cases':len(records),'matched':sum(r['matched'] for r in records),'source_target_executed':False}));assert all(r['matched'] for r in records)
