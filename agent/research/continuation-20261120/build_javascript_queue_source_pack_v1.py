import datetime,hashlib,json,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent;freeze=json.loads((P/'javascript-queue-source-freeze-v1.json').read_text());fetch=json.loads((P/'javascript-queue-source-fetch-v1.json').read_text());cards=[]
for row in fetch['files']:
 raw=(P/row['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==row['sha256'];cards.append({'repository':row['repository'],'revision':row['revision'],'path':row['path'].split('/')[-1],'sha256':row['sha256'],'source':raw.decode()})
r=subprocess.run(['docker','exec','-i','-e','NODE_PATH=/app/frontend/node_modules','-w','/app/frontend','engineering-library-frontend-1','node','/sources/engineering-library/agent/research/continuation-20261120/extract_javascript_queue_units_v1.cjs'],input=json.dumps({'cards':cards}).encode(),capture_output=True,timeout=20)
(P/'javascript-queue-source-pack-v1.stdout').write_bytes(r.stdout);(P/'javascript-queue-source-pack-v1.stderr').write_bytes(r.stderr);assert r.returncode==0,r.stderr.decode();result=json.loads(r.stdout)
for key,u in result['units'].items():
 path=P/'new-public-sources-v1'/u['repository'].replace('/','--')/u['revision']/u['path'];raw=path.read_bytes();quote=''.join(raw.decode().splitlines(keepends=True)[u['first_line']-1:u['last_line']]);assert quote==u['quote']and hashlib.sha256(quote.encode()).hexdigest()==u['quote_sha256']and hashlib.sha256(raw).hexdigest()==u['source_sha256']
result.update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),all_physical_units_verified=True,owner_approved=False,training_excluded=True)
with(P/'javascript-queue-source-pack-v1.json').open('x')as f:f.write(json.dumps(result,indent=2)+'\n')
print({'physical_units':len(result['units']),'all_verified':True})
