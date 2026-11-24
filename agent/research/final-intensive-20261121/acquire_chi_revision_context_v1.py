"""Read pinned local Chi objects only; disable lazy acquisition and diff drivers."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
protocol=json.loads((P/'chi-revision-context-protocol-v1.json').read_text())
baseline=json.loads((P/'baseline-verification-v1.json').read_text())
repo=next(r for r in baseline['repositories'] if r['repository']=='chi')
preflight=json.loads((P/'chi-local-object-access-preflight-v1.json').read_text())
assert all(r['exit_code']==1 and not r['stdout'] for r in preflight['observations'][1:])
env={**os.environ,'GIT_NO_LAZY_FETCH':'1','GIT_TERMINAL_PROMPT':'0'}
before,after=protocol['before'],protocol['after']
folder=P/'chi-revision-context-evidence-v1'
folder.mkdir()
records=[]
sha=lambda b:hashlib.sha256(b).hexdigest()


def observe(ident,args,target):
    command=['git','--no-optional-locks','-C',repo['absolute_path'],*args]
    run=subprocess.run(command,capture_output=True,timeout=30,env=env)
    path=folder/target
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as stream:stream.write(run.stdout)
    error=path.with_name(path.name+'.stderr')
    with error.open('xb') as stream:stream.write(run.stderr)
    records.append({'id':ident,'command':command,'exit_code':run.returncode,
                    'stdout_path':str(path.relative_to(ROOT)),'stdout_sha256':sha(run.stdout),
                    'stderr_path':str(error.relative_to(ROOT)),'stderr_sha256':sha(run.stderr),
                    'bytes':len(run.stdout),'source_executed':False})


for label,revision in [('before',before),('after',after)]:
    observe(label+'-commit',['show','--no-patch','--format=%H%n%P%n%aI%n%cI%n%s',revision],label+'/commit.txt')
    observe(label+'-lexical-wrapper-refs',['grep','-n','-F','NewWrapResponseWriter',revision,'--','*.go'],label+'/wrapper-lexical-refs.txt')
    for source in ['middleware/wrap_writer.go','middleware/wrap_writer_test.go','go.mod','LICENSE']:
        observe(label+':'+source,['show',revision+':'+source],label+'/'+source)
observe('changed-paths',['diff','--no-ext-diff','--no-textconv','--name-status',before,after,'--'],'changed-paths.txt')
observe('selected-patch',['diff','--no-ext-diff','--no-textconv','--no-renames',before,after,'--',
                          'middleware/wrap_writer.go','middleware/wrap_writer_test.go','go.mod','LICENSE'],'selected.patch')
observe('available-ancestry',['merge-base','--is-ancestor',before,after],'ancestry.stdout')
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'protocol_sha256':sha((P/'chi-revision-context-protocol-v1.json').read_bytes()),
        'records':records,'external_writes':False,'fetch_or_transport_requested':False,
        'lazy_fetch_disabled':True,'external_diff_and_textconv_disabled':True,
        'ancestry_caution':'Nonzero ancestry status in incomplete shallow history is not proof of unrelated commits.',
        'source_programs_executed':False,'new_model_calls':0,'training_eligible':False}
with (P/'chi-revision-context-acquisition-v1.json').open('x') as stream:
    json.dump(result,stream,indent=2)
    stream.write('\n')
print(json.dumps({'commands':len(records),'exit_counts':{str(code):sum(r['exit_code']==code for r in records) for code in sorted({r['exit_code'] for r in records})}}))
