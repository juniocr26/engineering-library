"""Fresh read-only Git observations for two frozen chapter re-reviews."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
baseline=json.loads((P/'baseline-verification-v1.json').read_text())
repos={r['repository']:r for r in baseline['repositories']}
tasks=[
    ('fastapi-request-context','fastapi','05e6df7e906c3decba377c37548019973f40bf15',name) for name in [
        'fastapi/routing.py','fastapi/dependencies/utils.py','tests/test_dependency_cache.py','tests/test_dependency_yield_scope.py','LICENSE']
]+[
    ('chi-wrapper-context','chi','9f8adb1aabaa8a91180a821111d3f8e668d1c0bf',name) for name in ['middleware/wrap_writer.go','middleware/wrap_writer_test.go']
]+[
    ('chi-wrapper-context','chi','04f7f55a7b5ddb2ecd79a8d813b2256c1113b8a9','middleware/wrap_writer.go'),
    ('chi-local-head-comparison','chi',repos['chi']['head'],'middleware/wrap_writer.go'),
]
output=P/'context-topic-sources-v1'
output.mkdir()
rows=[]
for topic,repository,revision,name in tasks:
    command=['git','--no-optional-locks','-C',repos[repository]['absolute_path'],'show',revision+':'+name]
    result=subprocess.run(command,capture_output=True,timeout=30)
    target=output/topic/revision/name
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as stream:stream.write(result.stdout)
    rows.append({'topic':topic,'repository':repository,'revision':revision,'source_path':name,
                 'command':command,'exit_code':result.returncode,'stderr':result.stderr.decode(),
                 'saved_path':str(target.relative_to(ROOT)),'sha256':hashlib.sha256(result.stdout).hexdigest(),'bytes':len(result.stdout),
                 'independently_reacquired':result.returncode==0,'source_executed':False})
with (P/'context-topic-source-acquisition-v1.json').open('x') as stream:
    json.dump({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'observations':rows,'external_writes':0,'gold':0},stream,indent=2)
    stream.write('\n')
print(json.dumps({'requests':len(rows),'successful':sum(r['exit_code']==0 for r in rows),'failed':[{k:r[k] for k in ['topic','revision','source_path','stderr']} for r in rows if r['exit_code']]}))
