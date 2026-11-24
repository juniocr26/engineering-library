import datetime,hashlib,json,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent
legacy=json.loads((P/'javascript-module-control-oracle-v1.json').read_text())['cases']
public=[c for c in json.loads((P/'new-public-written-signature-oracle-v1.json').read_text())['cases']if c['language']=='javascript']
cases=[]
for c in legacy:cases.append(dict(c,kind='existing-owned'))
for c in public:
 raw=(P/c['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==c['source_sha256']
 request={'source':raw.decode(),'path':Path(c['path']).name,'selector':c['selector'],'source_sha256':c['source_sha256']}
 cases.append({'id':c['id'],'kind':'existing-public-exposed','raw_request':json.dumps(request),'expected_status':c['expected_status']})
program='''const fs=require('node:fs');const o=require(process.argv[1]);const cases=JSON.parse(fs.readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(cases.map(c=>{let r;try{r=o.observe(o.strictJson(Buffer.from(c.raw_request)))}catch(e){r={status:'INCONCLUSIVE',reason:String(e.message)}}return {id:c.id,kind:c.kind,expected:c.expected_status,require_alias_wire_citation:!!c.require_alias_wire_citation,result:r,matches:r.status===c.expected_status&&(!c.require_alias_wire_citation||!!r.export_evidence)}})));'''
r=subprocess.run(['docker','exec','-i','-e','NODE_PATH=/app/frontend/node_modules','-w','/app/frontend','engineering-library-frontend-1','node','-e',program,'/sources/engineering-library/agent/research/continuation-20261120/javascript_module_observer_v3.cjs'],input=json.dumps(cases).encode(),capture_output=True,timeout=90)
(P/'javascript-v3-regressions-v1.stdout').write_bytes(r.stdout);(P/'javascript-v3-regressions-v1.stderr').write_bytes(r.stderr);assert r.returncode==0
rows=json.loads(r.stdout);expected={c['id']:c for c in public}
for row in rows:
 if row['kind']=='existing-public-exposed':
  c=expected[row['id']];result=row['result'];sig=result.get('signature',{});params=sig.get('parameters',[]);e=result.get('evidence',{});raw=(P/c['path']).read_bytes()
  checks={'parameters':[p['name']for p in params]==c['expected_parameters'],'local_selector':result.get('local_selector')==c['expected_local_selector'],'async':sig.get('async')==c['expected_async'],'default_expressions':all(next((p['default_expression']for p in params if p['name']==k),None)==v for k,v in c['expected_default_expression'].items()),'physical_quote':raw[e['quote_byte_start']:e['quote_byte_end']]==e['quote'].encode()and hashlib.sha256(e['quote'].encode()).hexdigest()==e['quote_sha256']}
  row['checks']=checks;row['matches']=row['matches']and all(checks.values())
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':rows,'correct':sum(row['matches']for row in rows),'n':len(rows),'existing_owned':len(legacy),'existing_real_source':len(public),'new_distinct_cases':0,'source_executed':False,'model_calls':0,'producer_sha256':hashlib.sha256((P/'javascript_module_observer_v3.cjs').read_bytes()).hexdigest(),'permanent_tests_changed':False}
with(P/'javascript-v3-regressions-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'correct':record['correct'],'n':len(rows),'owned':len(legacy),'public':len(public),'new_distinct_cases':0})
