"""Fetch only frozen selected public bodies, verify every Git blob."""
import datetime,hashlib,json,urllib.request
from pathlib import Path
P=Path(__file__).resolve().parent;freeze=json.loads((P/'backoff-source-family-freeze-v1.json').read_text());rows=[];seen={}
for cut in freeze['cuts']:
 for entry in cut['selected_blobs']:
  assert entry['mode']=='100644'and entry['size']<=65536 and'/'not in entry['path'];reused=entry['sha']in seen
  if reused:raw=seen[entry['sha']]
  else:
   url='https://raw.githubusercontent.com/cenkalti/backoff/'+cut['revision']+'/'+entry['path']
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EngineeringLibrarySourceResearch/1.0'}),timeout=35)as response:raw=response.read(65537)
  assert len(raw)==entry['size']and len(raw)<=65536;assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==entry['sha'];seen[entry['sha']]=raw;path=P/'new-public-sources-v1/cenkalti--backoff'/cut['revision']/entry['path'];path.parent.mkdir(parents=True,exist_ok=True)
  with path.open('xb')as f:f.write(raw)
  rows.append({'tag':cut['tag'],'revision':cut['revision'],'path':str(path.relative_to(P)),'git_blob':entry['sha'],'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'reused_verified_blob':reused})
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':rows,'unique_blobs':len(seen),'all_git_blobs_verified':True,'source_executed':False,'packages_installed':False,'training_excluded':True,'owner_approved':False,'model_calls':0}
with(P/'backoff-source-fetch-v1.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'files':len(rows),'unique_blobs':len(seen),'bytes':sum(x['bytes']for x in rows)})
