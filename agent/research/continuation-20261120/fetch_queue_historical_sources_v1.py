import base64,datetime,hashlib,json,urllib.request
from pathlib import Path
P=Path(__file__).resolve().parent;freeze=json.loads((P/'javascript-queue-historical-freeze-v1.json').read_text());existing=json.loads((P/'javascript-queue-source-fetch-v1.json').read_text())['files'];cache={e['git_blob']:P/e['path']for e in existing};rows=[]
for cut in freeze['cuts']:
 for entry in cut['selected_blobs']:
  assert entry['mode']=='100644'and entry['size']<=32768
  if entry['sha']in cache:body=cache[entry['sha']].read_bytes();method='reused exact already verified identical Git blob'
  else:
   with urllib.request.urlopen(urllib.request.Request(entry['url'],headers={'User-Agent':'EngineeringLibrarySourceResearch/1.0'}),timeout=35)as response:raw=response.read(131073)
   assert len(raw)<=131072;body=base64.b64decode(json.loads(raw)['content']);method='public Git blob GET'
  assert len(body)==entry['size']and hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()==entry['sha']
  path=P/'new-public-sources-v1'/cut['repository'].replace('/','--')/cut['revision']/entry['path'];path.parent.mkdir(parents=True,exist_ok=True)
  with path.open('xb')as f:f.write(body)
  rows.append({'repository':cut['repository'],'tag':cut['tag'],'revision':cut['revision'],'path':str(path.relative_to(P)),'git_blob':entry['sha'],'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body),'acquisition':method})
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':rows,'all_git_blobs_verified':True,'source_executed':False,'packages_installed':False,'training_excluded':True,'owner_approved':False,'prior_exposure':'Baselinefrontendlockfileexplicitlyadvertisesp-limit3.1.0andyocto-queue0.1.0;notindependentholdout. Lockfiledeclarationisnotaninstalledversionassertion.','model_calls':0}
with(P/'javascript-queue-historical-fetch-v1.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'files':len(rows),'bytes':sum(r['bytes']for r in rows),'reused_identical_blobs':sum(r['acquisition'].startswith('reused')for r in rows)})
