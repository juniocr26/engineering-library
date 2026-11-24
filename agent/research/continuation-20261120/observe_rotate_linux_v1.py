"""Repeat the same frozen confined function cases on the existing Linux runtime."""
import datetime,json,subprocess,time
from pathlib import Path
P=Path(__file__).resolve().parent
script="""import importlib.util,json,sys
sys.dont_write_bytecode=True
p='/sources/engineering-library/agent/research/continuation-20261120/observe_rotate_confined_v1.py'
spec=importlib.util.spec_from_file_location('owned_confined_rotate_observer',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=m.observe('/tmp/el-boltons-rotate-confined-20261120-linux-v1')
r['existing_cases_repeated_on_second_os']=8;r['new_distinct_cases']=0
print(json.dumps(r))
"""
start=time.monotonic();r=subprocess.run(['docker','exec','engineering-library-backend-1','python3','-c',script],text=True,capture_output=True,timeout=90)
(P/'rotate-confined-linux-v1.stdout').write_text(r.stdout);(P/'rotate-confined-linux-v1.stderr').write_text(r.stderr)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':r.returncode,'wall_seconds':time.monotonic()-start}
if r.returncode==0:record.update(json.loads(r.stdout))
with(P/'rotate-confined-linux-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items()if k not in ['rows','limits','python','platform']}));raise SystemExit(r.returncode)
