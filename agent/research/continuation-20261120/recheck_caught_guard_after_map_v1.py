"""Retain the twelve existing catch-reference outcomes after helper factoring."""
import datetime
import json
from pathlib import Path
import subprocess

P=Path(__file__).resolve().parent
rows=[]
for name in ['ruby-exception-guard-protocol-v1.json','ruby-exception-guard-ambiguity-protocol-v1.json']:
 protocol=json.loads((P/name).read_text())
 command=['docker','exec','-i','-e','RAILS_ENV=test','-e','DATABASE_URL=sqlite3::memory:','-w','/app/backend','engineering-library-backend-1','bundle','exec','ruby','/sources/engineering-library/agent/research/continuation-20261120/probe_ruby_exception_guard_v3.rb']
 process=subprocess.run(command,input=json.dumps(protocol),text=True,capture_output=True,timeout=90)
 assert process.returncode==0,process.stderr
 observed=json.loads(process.stdout)
 for result,reference in zip(observed['rows'],protocol['cases'],strict=True):
  assert result['id']==reference['id']and result['status']==reference['expected_status']
 rows.append({'protocol':name,'result':observed,'stderr':process.stderr})
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'current_caller':'1.9.43','existing_distinct_case_count':12,'all_previous_catch_outcomes_preserved':True,'rows':rows,'new_distinct_catch_cases':0,'model_calls':0,'source_executed':False,'permanent_tests_modified':False}
with(P/'caught-guard-after-returned-map-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'existing_catch_outcomes_preserved':'12/12','new_distinct_cases':0,'source_execution':False})
