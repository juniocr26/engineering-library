"""Own recovery worker: verify a restricted local capsule before tool replay."""
import base64
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import subprocess
import sys
import tarfile
import tempfile
import time


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    payload=json.load(sys.stdin)
    archive=base64.b64decode(payload['archive_b64'],validate=True)
    assert sha(archive)==payload['archive_sha256']
    manifest_bytes=base64.b64decode(payload['member_manifest_b64'],validate=True)
    assert sha(manifest_bytes)==payload['member_manifest_sha256']
    manifest=json.loads(manifest_bytes)
    expected={r['path']:r for r in manifest['files']}
    assert len(expected)==len(manifest['files'])
    root=Path(tempfile.mkdtemp(prefix='el-operational-capsule-',dir='/private/tmp' if platform.system()=='Darwin' else '/tmp'))
    os.chmod(root,0o700)
    capsule=root/'capsule'
    capsule.mkdir(mode=0o700)
    verified=[]
    # Manual regular-member extraction also works on the older container Python.
    # No symlinks, hardlinks, devices, absolute paths or parent traversal admitted.
    with tarfile.open(fileobj=io.BytesIO(archive),mode='r:gz') as stream:
        members=stream.getmembers()
        names=[m.name for m in members]
        assert len(names)==len(set(names))
        assert set(names)==set(expected)|{'capsule-manifest.json'}
        for member in members:
            name=PurePosixPath(member.name)
            assert member.isfile() and not name.is_absolute() and '..' not in name.parts
            assert str(name)==member.name and 0<=member.size<=20*1024*1024
            raw=stream.extractfile(member).read()
            assert len(raw)==member.size
            if member.name=='capsule-manifest.json':
                assert raw==manifest_bytes
            else:
                record=expected[member.name]
                assert len(raw)==record['bytes'] and sha(raw)==record['sha256']
            target=capsule/member.name
            target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as output:
                output.write(raw)
            os.chmod(target,0o700 if '/bin/' in member.name else 0o600)
            verified.append(member.name)
    # All capsule members verified before any restored program is invoked.
    inputs=root/'inputs'
    outputs=root/'outputs'
    inputs.mkdir(mode=0o700)
    outputs.mkdir(mode=0o700)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    planner=capsule/'agent/tools/documentation_lifecycle.py'
    launcher=capsule/'agent/tools/go_source_ast.py'
    observations=[]
    for case in payload['planner_cases']:
        raw=base64.b64decode(case['input_b64'],validate=True)
        assert sha(raw)==case['input_sha256']
        q=inputs/(case['id']+'.json')
        with q.open('xb') as output:
            output.write(raw)
        start=time.monotonic()
        result=subprocess.run([sys.executable,'-I','-S','-B',str(planner),'--input',str(q)],capture_output=True,timeout=25,env=env,cwd=capsule)
        (outputs/(case['id']+'-stdout.json')).write_bytes(result.stdout)
        (outputs/(case['id']+'-stderr.txt')).write_bytes(result.stderr)
        observations.append({'id':case['id'],'returncode':result.returncode,'wall_seconds':time.monotonic()-start,'stdout_sha256':sha(result.stdout),'stderr_sha256':sha(result.stderr),'stdout_matches_original':sha(result.stdout)==case['expected_stdout_sha256'],'stderr_matches_original':sha(result.stderr)==case['expected_stderr_sha256'],'stdout':result.stdout.decode(),'stderr':result.stderr.decode()})
    native=[]
    for key in ['native_negative','native_positive']:
        case=payload[key]
        raw=base64.b64decode(case['input_b64'],validate=True)
        assert sha(raw)==case['input_sha256']
        start=time.monotonic()
        result=subprocess.run([sys.executable,'-I','-S','-B',str(launcher)],input=raw,capture_output=True,timeout=25,env=env,cwd=capsule)
        (outputs/(key+'-stdout.json')).write_bytes(result.stdout)
        (outputs/(key+'-stderr.txt')).write_bytes(result.stderr)
        row={'kind':key,'returncode':result.returncode,'wall_seconds':time.monotonic()-start,'stdout_sha256':sha(result.stdout),'stderr_sha256':sha(result.stderr),'stdout':result.stdout.decode(),'stderr':result.stderr.decode()}
        if key=='native_negative':
            row['stdout_matches_original']=sha(result.stdout)==case['expected_stdout_sha256']
            row['stderr_matches_original']=sha(result.stderr)==case['expected_stderr_sha256']
        else:
            data=json.loads(result.stdout) if result.returncode==0 else {}
            row['positive_syntax_projection_matches']=(data.get('syntax_only') is True and data.get('source_executed') is False and data.get('profile')=='go-standard-parser-declarations-v1' and data.get('source_sha256')==case['source_sha256'] and len(data.get('units',[]))==1 and data['units'][0]['selector']=='RecoveryProbe' and data['units'][0]['quote']=='func RecoveryProbe() int { return 7 }')
        native.append(row)
    result={'platform':{'system':platform.system(),'machine':platform.machine(),'python':platform.python_version(),'isolated':sys.flags.isolated,'no_bytecode':sys.dont_write_bytecode},'restored_root':str(root),'capsule_sha256':sha(archive),'members_verified_before_execution':verified,'planner_cases':observations,'native_observations':native,'replay_passes':all(r['returncode']==0 and r['stdout_matches_original'] and r['stderr_matches_original'] for r in observations) and all((r.get('stdout_matches_original') and r.get('stderr_matches_original')) if r['kind']=='native_negative' else r['returncode']==0 and r.get('positive_syntax_projection_matches') for r in native),'target_source_executed':False,'application_database_model_or_training_access':False}
    json.dump(result,sys.stdout,ensure_ascii=False)
    sys.stdout.write('\n')


if __name__=='__main__':
    main()
