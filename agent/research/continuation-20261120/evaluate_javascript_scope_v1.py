import datetime,hashlib,json,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent
version=int(sys.argv[1]);assert version in [2,3]
oracle=json.loads((P/'javascript-evaluation-scope-oracle-v1.json').read_text());filename='javascript_module_observer_v'+str(version)+'.cjs'
program='''const fs=require('node:fs');const observer=require(process.argv[1]);const cases=JSON.parse(fs.readFileSync(0,'utf8'));const rows=cases.map(c=>{let result;try{result=observer.observe(observer.strictJson(Buffer.from(c.raw_request)))}catch(e){result={status:'INCONCLUSIVE',reason:String(e.message)}}return {id:c.id,expected:c.expected_status,result,matches:result.status===c.expected_status}});process.stdout.write(JSON.stringify({node:process.version,rows}));'''
r=subprocess.run(['docker','exec','-i','-e','NODE_PATH=/app/frontend/node_modules','-w','/app/frontend','engineering-library-frontend-1','node','-e',program,'/sources/engineering-library/agent/research/continuation-20261120/'+filename],input=json.dumps(oracle['cases']).encode(),capture_output=True,timeout=90)
(P/('javascript-scope-v'+str(version)+'.stdout')).write_bytes(r.stdout);(P/('javascript-scope-v'+str(version)+'.stderr')).write_bytes(r.stderr)
assert r.returncode==0,r.stderr.decode()
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'producer':filename,'producer_sha256':hashlib.sha256((P/filename).read_bytes()).hexdigest(),'oracle_sha256':hashlib.sha256((P/'javascript-evaluation-scope-oracle-v1.json').read_bytes()).hexdigest(),**json.loads(r.stdout),'source_executed':False,'model_calls':0,'new_infrastructure':False,'permanent_test_suite_changed':False}
record.update(correct=sum(row['matches']for row in record['rows']),n=len(record['rows']))
with(P/('javascript-evaluation-scope-v'+str(version)+'.json')).open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'correct':record['correct'],'n':record['n'],'misses':[row['id']for row in record['rows']if not row['matches']]})
