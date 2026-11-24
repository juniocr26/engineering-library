import pathlib,json,hashlib,datetime,importlib.util,subprocess
P=pathlib.Path(__file__).resolve().parent
oracle=json.loads((P/'new-public-written-signature-oracle-v1.json').read_text())
s=importlib.util.spec_from_file_location('observer',P/'module_contract_observer_v5.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
rows=[];js=[]
for case in oracle['cases']:
 raw=(P/case['path']).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=case['source_sha256']:raise ValueError('oracle source identity changed')
 if case['language']=='python':
  result=m.observe({'path':'jmespath/__init__.py','revision':case['path'].split('/')[2],'source':raw.decode(),'sha256':case['source_sha256']},case['selector'])
  sig=result.get('signature',{});names=sig.get('positional_only',[])+sig.get('positional_or_keyword',[])+sig.get('keyword_only',[])
  checks={'status':result['status']==case['expected_status'],'parameters':names==case['expected_parameters'],'defaults':all(sig.get('defaults',{}).get(k)==v for k,v in case['expected_default'].items())}
  rows.append({'id':case['id'],'language':'python','checks':checks,'matches':all(checks.values()),'result':result})
 else:js.append({'id':case['id'],'request':{'source':raw.decode(),'path':case['path'].split('/')[-1],'selector':case['selector'],'source_sha256':case['source_sha256']}})
program="""const fs=require('node:fs');const o=require(process.argv[1]);const cases=JSON.parse(fs.readFileSync(0,'utf8'));const rows=cases.map(c=>{let r;try{r=o.observe(o.strictJson(Buffer.from(JSON.stringify(c.request))))}catch(e){r={status:'INCONCLUSIVE',reason:String(e.message)}}return {id:c.id,result:r}});process.stdout.write(JSON.stringify(rows));"""
cmd=['docker','exec','-i','-e','NODE_PATH=/app/frontend/node_modules','-w','/app/frontend','engineering-library-frontend-1','node','-e',program,'/sources/engineering-library/agent/research/continuation-20261120/javascript_module_observer_v2.cjs']
r=subprocess.run(cmd,input=json.dumps(js).encode(),capture_output=True,timeout=120)
(P/'new-public-signatures-v1.stdout').write_bytes(r.stdout);(P/'new-public-signatures-v1.stderr').write_bytes(r.stderr)
if r.returncode:raise RuntimeError('runtime failed; raw evidence retained')
byid={c['id']:c for c in oracle['cases']}
for row in json.loads(r.stdout):
 c=byid[row['id']];out=row['result'];sig=out.get('signature',{});params=sig.get('parameters',[])
 checks={'status':out['status']==c['expected_status'],'parameters':[p['name']for p in params]==c['expected_parameters'],'local_selector':out.get('local_selector')==c['expected_local_selector'],'async':sig.get('async')==c['expected_async'],'defaults':all(next((p['default_expression']for p in params if p['name']==k),None)==v for k,v in c['expected_default_expression'].items())}
 rows.append(dict(row,language='javascript',checks=checks,matches=all(checks.values())))
for row in rows:
 r=row['result'];quote=r.get('evidence',{});c=byid[row['id']];raw=(P/c['path']).read_bytes()
 if quote:
  text=quote.get('quote','').encode();start=quote.get('quote_byte_start');end=quote.get('quote_byte_end')
  physical=raw[start:end]==text if isinstance(start,int)and isinstance(end,int)else text in raw
  row['checks']['physical_quote']=physical and hashlib.sha256(text).hexdigest()==quote.get('quote_sha256')
  row['matches']=all(row['checks'].values())
report={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'oracle_sha256':hashlib.sha256((P/'new-public-written-signature-oracle-v1.json').read_bytes()).hexdigest(),'cases':rows,'correct':sum(r['matches']for r in rows),'n':len(rows),'task':'WRITTEN_SIGNATURE_FACTS_ONLY_NOT_LIFECYCLE','independent_families':2,'neural_evaluation':False,'model_calls':0,'source_executed':False}
with (P/'new-public-signatures-v1.json').open('x')as f:json.dump(report,f,indent=2)
print(json.dumps({'correct':report['correct'],'n':report['n'],'checks':[{k:r[k]for k in ('id','checks','matches')}for r in rows]}))
