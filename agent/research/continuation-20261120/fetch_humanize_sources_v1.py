"""Fetch only frozen public blobs; Git object identity verified before storing."""
import base64,datetime,hashlib,json,urllib.request
from pathlib import Path
P=Path(__file__).resolve().parent
freeze=json.loads((P/'humanize-source-family-freeze-v1.json').read_text());seen={};rows=[]
for cut in freeze['cuts']:
 for entry in cut['selected_blobs']:
  assert entry['mode']=='100644' and entry['size']<=65536 and '/'not in entry['path']
  reused=entry['sha']in seen
  if reused:body=seen[entry['sha']]
  else:
   with urllib.request.urlopen(urllib.request.Request(entry['url'],headers={'User-Agent':'EngineeringLibrarySourceResearch/1.0'}),timeout=35)as response:raw=response.read(262145)
   assert len(raw)<=262144
   body=base64.b64decode(json.loads(raw)['content'],validate=False)
  assert len(body)==entry['size']
  assert hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()==entry['sha']
  seen[entry['sha']]=body
  path=P/'new-public-sources-v1'/'dustin--go-humanize'/cut['revision']/entry['path'];path.parent.mkdir(parents=True,exist_ok=True)
  with path.open('xb')as f:f.write(body)
  rows.append({'tag':cut['tag'],'revision':cut['revision'],'path':str(path.relative_to(P)),'git_blob':entry['sha'],'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body),'reused_verified_blob':reused})
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':rows,'unique_blobs':len(seen),'all_git_blobs_verified':True,'source_executed':False,'packages_installed':False,'model_calls':0,'training_excluded':True,'owner_approved':False}
with(P/'humanize-source-fetch-v1.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'files':len(rows),'unique_blobs':len(seen),'bytes':sum(x['bytes']for x in rows)})
