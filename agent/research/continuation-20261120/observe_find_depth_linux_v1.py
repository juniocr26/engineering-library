"""Repeat the same seven native-tree generator observations on existing Linux."""
import datetime,json,subprocess,time
from pathlib import Path
P = Path(__file__).resolve().parent
script = """import importlib.util,json,sys
sys.dont_write_bytecode=True
path='/sources/engineering-library/agent/research/continuation-20261120/observe_find_depth_confined_v1.py'
spec=importlib.util.spec_from_file_location('linux_owned_depth_observer',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
record=module.observe('/tmp/el-find-depth-confined-20261120-linux-v1')
record['existing_cases_repeated_on_second_os']=7
record['new_distinct_cases']=0
print(json.dumps(record))
"""
start = time.monotonic()
result = subprocess.run(['docker','exec','engineering-library-backend-1','python3','-c',script], text=True, capture_output=True, timeout=90)
(P/'find-depth-confined-linux-v1.stdout').write_text(result.stdout)
(P/'find-depth-confined-linux-v1.stderr').write_text(result.stderr)
record = {'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':result.returncode,'wall_seconds':time.monotonic()-start}
if result.returncode == 0:
    record.update(json.loads(result.stdout))
with (P/'find-depth-confined-linux-v1.json').open('x') as stream:
    stream.write(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k not in ['rows','limits','python','platform']}))
raise SystemExit(result.returncode)
