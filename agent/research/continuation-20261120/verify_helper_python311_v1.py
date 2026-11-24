import datetime,hashlib,json,subprocess,time
from pathlib import Path
P=Path(__file__).resolve().parent
program="""import json,pathlib,sys,unittest
sys.dont_write_bytecode=True
root=pathlib.Path('/sources/engineering-library');sys.path.insert(0,str(root/'agent/tools'));import documentation_retrieval as helper
assert helper.VERSION=='0.1.4'
loader=unittest.TestLoader();suite=unittest.TestSuite()
for pattern in ['documentation_retrieval_test.py','documentation_job_budget_test.py']:suite.addTests(loader.discover(str(root/'agent/test'),pattern=pattern))
result=unittest.TextTestRunner(verbosity=1).run(suite)
print(json.dumps({'python':sys.version,'helper_version':helper.VERSION,'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'success':result.wasSuccessful()}))
sys.exit(0 if result.wasSuccessful()else 1)
"""
command=['docker','exec','-e','PYTHONDONTWRITEBYTECODE=1','-e','GIT_OPTIONAL_LOCKS=0','-w','/sources/engineering-library','engineering-library-backend-1','python3','-c',program];start=time.monotonic();r=subprocess.run(command,capture_output=True,text=True,timeout=120);(P/'helper-python311-existing-tests-v1.stdout').write_text(r.stdout);(P/'helper-python311-existing-tests-v1.stderr').write_text(r.stderr);record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':r.returncode,'wall_seconds':time.monotonic()-start,'source_tool_sha256':hashlib.sha256(Path('agent/tools/documentation_retrieval.py').read_bytes()).hexdigest(),'permanent_tests_modified':False,'new_distinct_tests':0,'new_model_calls':0}
if r.stdout.strip():record['result']=json.loads(r.stdout)
with(P/'helper-python311-existing-tests-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print(record);raise SystemExit(r.returncode)
