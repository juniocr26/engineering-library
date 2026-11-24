import subprocess,json,datetime,os,hashlib
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[2];prior=json.loads((p/'repository-action-ledger-v7.json').read_text());records=[];env={**os.environ,'GIT_OPTIONAL_LOCKS':'0','GIT_NO_LAZY_FETCH':'1'}
for r in prior['records']:
 commands=[]
 for args in [['rev-parse','HEAD'],['status','--porcelain=v1','--untracked-files=normal']]:
  cmd=['git','--no-optional-locks','-c','core.fsmonitor=false','-C',r['absolute_path']]+args;out=subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=30);commands.append({'command':cmd,'exit_code':out.returncode,'stdout':out.stdout,'stderr':out.stderr})
  assert out.returncode==0,r['repository']
 records.append({'repository':r['repository'],'absolute_path':r['absolute_path'],'head':commands[0]['stdout'].strip(),'head_matches_baseline':commands[0]['stdout'].strip()==r['preexisting_head'],'status':commands[1]['stdout'],'status_matches_baseline':commands[1]['stdout']==r['preexisting_status'],'commands':commands,'private_external_body_read':False})
external=[r for r in records if r['repository']!='engineering-library'];assert len(records)==42 and all(r['head_matches_baseline'] for r in records) and all(r['status_matches_baseline'] for r in external)
with (p/'repository-state-observation-v4.json').open('x') as f:json.dump({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'repository_count':42,'all_heads_match':True,'all41_external_statuses_match':True,'no_git_mutation':True},f,indent=2);f.write('\n')
commands=[]
for args in [['diff','--name-only'],['diff','--cached','--name-only']]:
 cmd=['git','--no-optional-locks','-c','core.fsmonitor=false','-C',str(root)]+args;o=subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=30);commands.append({'command':cmd,'exit_code':o.returncode,'stdout':o.stdout,'stderr':o.stderr});assert o.returncode==0 and o.stdout==''
with (p/'campaign-scope-observation-v6.json').open('x') as f:json.dump({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tracked_and_staged_diffs_empty':True,'commands':commands,'engineering_library_status':next(r['status'] for r in records if r['repository']=='engineering-library'),'expected_untracked':'Four root reports and isolated agent/research/final-intensive-20261121 research tree','external_source_edits':False},f,indent=2);f.write('\n')
print(json.dumps({'heads_match':42,'external_statuses_match':41,'tracked_or_staged_changes':0}))
