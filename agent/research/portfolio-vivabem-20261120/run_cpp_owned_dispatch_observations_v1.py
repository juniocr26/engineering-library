from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,hashlib,time,os
p=Path(__file__).parent
protocol=json.loads((p/'cpp-owned-dispatch-observation-protocol-v1.json').read_text())
root=p/'cpp-owned-dispatch-observations-v1'
result=p/'cpp-owned-dispatch-observation-results-v1.json'
assert not result.exists()
compiler=subprocess.check_output(['/usr/bin/clang++','--version'],text=True)
rows=[]
for case in protocol['cases']:
 folder=root/case['id'];src=folder/'source.cpp';binary=folder/'program'
 assert not binary.exists()
 command=['/usr/bin/clang++','-std=c++17','-Wall','-Wextra','-pedantic-errors',str(src),'-o',str(binary)]
 start=time.monotonic();c=subprocess.run(command,capture_output=True,text=True,timeout=15)
 (folder/'compile.stdout').write_text(c.stdout);(folder/'compile.stderr').write_text(c.stderr)
 row={'case':case['id'],'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'compile_command':command,'compile_returncode':c.returncode,'compile_seconds':time.monotonic()-start,'compile_expectation_matches':(c.returncode==0)==(case['compile']=='PASS'),'run_attempted':False}
 if c.returncode==0 and case['compile']=='PASS':
  start=time.monotonic();r=subprocess.run([str(binary.resolve())],cwd=folder,capture_output=True,text=True,timeout=3,env={'PATH':'/usr/bin:/bin','LANG':'C'})
  (folder/'run.stdout').write_text(r.stdout);(folder/'run.stderr').write_text(r.stderr)
  value=json.loads(r.stdout);row.update(run_attempted=True,run_returncode=r.returncode,run_seconds=time.monotonic()-start,actual=value,expected=case['run_json'],run_expectation_matches=r.returncode==0 and value==case['run_json'],binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest())
 rows.append(row)
result.write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'compiler':compiler,'cases':rows,'all_expectations_match':all(r['compile_expectation_matches'] and r.get('run_expectation_matches',True) for r in rows),'source_programs_executed':'Five fully owned synthetic C++ programs only; no OpenCV source/header/linking or application execution.','training_gold':False,'production_changes':False},indent=2)+'\n')
print(json.dumps({'receipt':str(result),'cases':len(rows),'all_expectations_match':all(r['compile_expectation_matches'] and r.get('run_expectation_matches',True) for r in rows)}))
