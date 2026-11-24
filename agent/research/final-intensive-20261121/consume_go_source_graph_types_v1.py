import argparse,json,hashlib,subprocess
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True,type=Path);a=ap.parse_args();root=a.root.resolve();p=root/'agent/research/final-intensive-20261121';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();binary=p/'offline-go-type-observer-v5/observer';build=json.loads((p/'go-source-graph-type-observer-build-v3.json').read_text());assert sha(binary)==build['binary_sha256'];assert sha(p/'offline-go-type-observer-v5/main.go')==build['source_sha256'];closure=json.loads((p/'go-stdlib-export-closure-v1/manifest-v2.json').read_text())
for edge in closure['records']:assert sha(root/edge['export_path'])==edge['export_sha256']
def replay(file,expected):
 raw=file.read_bytes()
 # Duplicate-key negative must retain exact input syntax; ordinary root rebinding cannot parse/reencode it.
 if file.name=='duplicate-json-key.request.json':
  original=json.loads(raw)['export_root'];raw=raw.replace(json.dumps(original).encode(),json.dumps(str(root)).encode())
 else:
  request=json.loads(raw);request['export_root']=str(root);raw=json.dumps(request).encode()
 run=subprocess.run([str(binary)],input=raw,capture_output=True,timeout=30);assert run.returncode==0;packet=json.loads(run.stdout);assert packet==expected,file.name
folder=p/'go-source-graph-controls-v3';protocol=json.loads((folder/'protocol.json').read_text());assert protocol['observer_binary_sha256']==sha(binary);results=json.loads((folder/'results.json').read_text());by={r['id']:r['packet'] for r in results['records']}
for case in protocol['cases']:replay(folder/(case['id']+'.request.json'),by[case['id']])
folder=p/'go-source-graph-determinism-v2';result=json.loads((folder/'results.json').read_text());assert len(result['packet_variants'])==1;expected=json.loads((folder/'run-01.stdout.json').read_text());replay(folder/'request.json',expected)
folder=p/'go-image-application-source-graph-v1';protocol=json.loads((folder/'protocol.json').read_text());assert protocol['binary_sha256']==sha(binary)
for edge in protocol['source_edges']:assert sha(root/edge['saved_path'])==edge['sha256']
expected=json.loads((folder/'result.json').read_text())['packet'];replay(folder/'request.json',expected)
print(json.dumps({'status':'PASS_FROZEN_GO_SOURCE_GRAPH_RECOVERY','owned_control_packets':len(by),'determinism_fixture_packet':1,'real_two_package_packet':1,'standard_export_files_verified':len(closure['records']),'target_source_executed':False,'new_model_calls':0,'scope':'Exact local binary/source/export replay, not SDK rebuild, whole repository build, runtime injection or prose correctness.'}))
