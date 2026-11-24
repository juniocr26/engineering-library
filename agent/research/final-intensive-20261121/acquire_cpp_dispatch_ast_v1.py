"""Acquire static compiler ASTs for existing owned controls; execute no targets."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
protocol=json.loads((P/'cpp-ast-dispatch-study-protocol-v1.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
output=P/'cpp-ast-dispatch-observations-v1'
output.mkdir()
version_command=[protocol['compiler'],'--version']
version=subprocess.run(version_command,capture_output=True,text=True,timeout=15)
records=[]
for case in protocol['cases']:
    source=ROOT/case['path']
    assert sha(source.read_bytes())==case['sha256']
    command=[protocol['compiler'],*protocol['command_flags'],str(source)]
    run=subprocess.run(command,capture_output=True,timeout=30)
    folder=output/case['id']
    folder.mkdir()
    paths={}
    for name,raw in [('ast.json',run.stdout),('stderr.txt',run.stderr)]:
        target=folder/name
        with target.open('xb') as stream:stream.write(raw)
        paths[name]={'path':str(target.relative_to(ROOT)),'sha256':sha(raw),'bytes':len(raw)}
    record={'id':case['id'],'source':case['path'],'source_sha256':case['sha256'],
            'command':command,'exit_code':run.returncode,'outputs':paths,
            'expected_compile_success':case['expected_compile_success'],
            'matched_compile_outcome':(run.returncode==0)==case['expected_compile_success'],
            'within_output_bound':len(run.stdout)<=protocol['output_bound_bytes'],
            'target_executed':False,'binary_or_object_emitted':False}
    records.append(record)
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'protocol_sha256':sha((P/'cpp-ast-dispatch-study-protocol-v1.json').read_bytes()),
        'compiler_version':{'command':version_command,'exit_code':version.returncode,
                            'stdout':version.stdout,'stderr':version.stderr},
        'records':records,'scope':'Own controls only; compiler syntax/type/declaration analysis, no program or OpenCV execution.',
        'prior_dynamic_results_rerun':False,'model_calls':0,'optimizer_updates':0}
with (P/'cpp-ast-dispatch-acquisition-v1.json').open('x') as stream:
    json.dump(result,stream,indent=2)
    stream.write('\n')
print(json.dumps({'cases':len(records),'expected_compile_outcomes':sum(r['matched_compile_outcome'] for r in records),
                  'AST_bytes':sum(r['outputs']['ast.json']['bytes'] for r in records),
                  'all_within_bound':all(r['within_output_bound'] for r in records),'targets_executed':False}))
