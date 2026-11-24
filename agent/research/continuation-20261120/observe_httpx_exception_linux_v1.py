import datetime,json,subprocess,time
from pathlib import Path
P=Path(__file__).resolve().parent
script="""import pathlib,sys
sys.dont_write_bytecode=True
path=pathlib.Path('/sources/engineering-library/agent/research/continuation-20261120/observe_httpx_exception_composition_v1.py')
source=path.read_text().replace("output=P/('httpx-exception-composition-'+sys.argv[1]+'-v1.json')", "output=Path('/tmp/el-httpx-exception-composition-linux-v1.json')")
sys.argv=[str(path),'linux']
exec(compile(source,str(path),'exec'),{'__name__':'__main__','__file__':str(path)})
print(pathlib.Path('/tmp/el-httpx-exception-composition-linux-v1.json').read_text())
"""
start=time.monotonic()
r=subprocess.run(['docker','exec','engineering-library-backend-1','python3','-c',script],text=True,capture_output=True,timeout=90)
(P/'httpx-exception-composition-linux-v1.stdout').write_text(r.stdout)
(P/'httpx-exception-composition-linux-v1.stderr').write_text(r.stderr)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':r.returncode,'wall_seconds':time.monotonic()-start,'existing_cases_repeated':21,'new_distinct_cases':0}
if r.returncode==0:record['observation']=json.loads(r.stdout[r.stdout.index('\n')+1:])
with(P/'httpx-exception-composition-linux-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'exit_code':r.returncode,'all_pass':record.get('observation',{}).get('all_pass'),'new_distinct_cases':0})
raise SystemExit(r.returncode)
