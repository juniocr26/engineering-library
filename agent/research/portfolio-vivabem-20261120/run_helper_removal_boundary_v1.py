"""Observe existing owned planner/native tool on archived inert source packets."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess
import sys
import time

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
freeze=json.loads((P/'helper-removal-boundary-input-freeze-v1.json').read_text())
restored=Path(freeze['restored_root'])/P.relative_to(ROOT)
inputs=restored/'helper-removal-boundary-v1'
manifest=json.loads((inputs/'frozen-input-manifest.json').read_text())
planner=ROOT/'agent/tools/documentation_lifecycle.py'
assert hashlib.sha256(planner.read_bytes()).hexdigest()==manifest['planner_sha256']
out=P/'helper-removal-boundary-v1'/'observations'
assert not out.exists(), 'Do not replay a started campaign observation'
out.mkdir()
(out/'started.json').write_text(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pid':os.getpid(),'frozen_manifest_sha256':hashlib.sha256((inputs/'frozen-input-manifest.json').read_bytes()).hexdigest()},indent=2)+'\n')
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
receipts=[]
for case in manifest['owned_cases']+manifest['real_source_admission_probes']:
    q=inputs/case['input']
    assert hashlib.sha256(q.read_bytes()).hexdigest()==case['sha256']
    start=time.monotonic()
    result=subprocess.run([sys.executable,'-I','-S','-B',str(planner),'--input',str(q)],capture_output=True,timeout=20,env=env,cwd=ROOT)
    name=case['id']
    (out/(name+'-stdout.json')).write_bytes(result.stdout)
    (out/(name+'-stderr.txt')).write_bytes(result.stderr)
    packet=json.loads(result.stdout) if result.returncode==0 else None
    receipts.append({'id':name,'returncode':result.returncode,'action':packet.get('action') if packet else None,'reason':packet.get('reason') if packet else None,'expected':case.get('expected_action',case.get('expected_safety_action')),'wall_seconds':time.monotonic()-start,'input_sha256':case['sha256'],'stdout_sha256':hashlib.sha256(result.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(result.stderr).hexdigest(),'source_executed':False})
    print(name,receipts[-1]['action'],receipts[-1]['reason'],flush=True)
q=inputs/manifest['native_negative_request']['path']
assert hashlib.sha256(q.read_bytes()).hexdigest()==manifest['native_negative_request']['sha256']
start=time.monotonic()
native=subprocess.run([sys.executable,'-I','-S','-B',str(ROOT/'agent/tools/go_source_ast.py')],input=q.read_bytes(),capture_output=True,timeout=25,env=env,cwd=ROOT)
(out/'native-negative-stdout.txt').write_bytes(native.stdout)
(out/'native-negative-stderr.txt').write_bytes(native.stderr)
native_receipt={'returncode':native.returncode,'stdout_sha256':hashlib.sha256(native.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(native.stderr).hexdigest(),'stderr':native.stderr.decode(),'wall_seconds':time.monotonic()-start,'request_sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'source_executed':False}
summary={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'planner_version':manifest['planner_version'],'planner_sha256':manifest['planner_sha256'],'cases':receipts,'native_negative':native_receipt,'scope':'Actual existing tools executed; target Go/Python source packets only parsed/inspected. Not application/testsuite execution, independent generalization, wholechapter decision success or model training.','model_calls':0,'writes_to_external_projects':0}
(out/'terminal.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print('native-negative',native.returncode,native.stderr.decode().strip(),flush=True)
