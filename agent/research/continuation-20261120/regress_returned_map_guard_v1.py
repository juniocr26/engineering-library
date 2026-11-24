"""Run justified existing checks after the two bounded production source edits."""
import datetime
import json
from pathlib import Path
import re
import subprocess
import time

P=Path(__file__).resolve().parent
commands=[('ruby-regression-after-returned-map-v1',['docker','exec','-e','RAILS_ENV=test','-e','DATABASE_URL=sqlite3::memory:','-w','/app/backend','engineering-library-backend-1','bundle','exec','ruby','-Itest','-e','Dir["test/offline/*_offline.rb"].sort.each { |path| require_relative path }']),('python-regression-after-returned-map-v1',['docker','exec','-e','PYTHONDONTWRITEBYTECODE=1','-w','/sources/engineering-library','engineering-library-backend-1','python3','backend/test/offline/python_structure_offline.py'])]
for name,command in commands:
 start=time.monotonic();process=subprocess.run(command,text=True,capture_output=True,timeout=180)
 with(P/(name+'.stdout')).open('x')as f:f.write(process.stdout)
 with(P/(name+'.stderr')).open('x')as f:f.write(process.stderr)
 record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':command,'exit_code':process.returncode,'wall_seconds':time.monotonic()-start,'permanent_tests_modified':False,'new_permanent_tests':0,'model_calls':0,'upstream_application_executed':False}
 if name.startswith('ruby'):
  match=re.search(r'(\d+) runs, (\d+) assertions, (\d+) failures, (\d+) errors, (\d+) skips',process.stdout)
  if match:record['summary']=dict(zip(['runs','assertions','failures','errors','skips'],map(int,match.groups())))
 else:
  match=re.search(r'Ran (\d+) tests',process.stderr)
  if match:record['existing_tests']=int(match[1])
 with(P/(name+'.json')).open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
 print(json.dumps(record),flush=True)
 if process.returncode!=0:raise SystemExit(process.returncode)
