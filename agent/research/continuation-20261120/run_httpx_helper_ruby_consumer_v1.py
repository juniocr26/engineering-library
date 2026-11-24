import datetime,json,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent;out=P/'helper-ruby-httpx-consumption-v1';payload=(out/'ruby-input.json').read_bytes();command=['docker','exec','-i','-e','RAILS_ENV=test','-e','DATABASE_URL=sqlite3::memory:','-w','/app/backend','engineering-library-backend-1','bundle','exec','ruby','/sources/engineering-library/agent/research/continuation-20261120/consume_httpx_helper_in_ruby_v1.rb'];r=subprocess.run(command,input=payload,capture_output=True,timeout=90)
(out/'ruby.stdout').write_bytes(r.stdout);(out/'ruby.stderr').write_bytes(r.stderr)
with(out/'process.json').open('x')as f:f.write(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':command,'exit':r.returncode},indent=2)+'\n')
assert r.returncode==0,r.stderr.decode()
result=json.loads(r.stdout);protocol=json.loads((P/'helper-ruby-httpx-consumption-protocol-v2.json').read_text());checks=[]
for row,case in zip(result['rows'],protocol['cases'],strict=True):checks.append({'id':row['id'],'expected':case['expected_status'],'observed':row['status'],'pass':row['id']==case['id']and row['status']==case['expected_status']})
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'observation':result,'checks':checks,'passes':sum(x['pass']for x in checks),'cases':len(checks),'source_executed':False,'owner_approved':False,'training_gold':False,'publication_authorized':False,'limit':'An exact real helper quote plus successful existing renderer is not semantic entailment; false suppression claim with unchanged Exception is a known expected accepted limitation.'}
with(P/'helper-ruby-httpx-consumption-results-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'passes':record['passes'],'cases':record['cases'],'card_keys':list(result['card']),'rows':checks})
