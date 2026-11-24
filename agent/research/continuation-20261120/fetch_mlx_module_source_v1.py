"""Preserve exact public Module implementation/license; no import or installation."""
import datetime,hashlib,json,urllib.request
from pathlib import Path
P=Path(__file__).resolve().parent;freeze=json.loads((P/'mlx-module-source-scope-freeze-v1.json').read_text());rows=[]
for e in freeze['selected_blobs']:
 url='https://raw.githubusercontent.com/ml-explore/mlx/'+freeze['revision']+'/'+e['path']
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EngineeringLibrarySourceResearch/1.0'}),timeout=35)as response:raw=response.read(131073)
 assert len(raw)==e['size']and len(raw)<=131072 and hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==e['sha'];file=P/'new-public-sources-v1/ml-explore--mlx'/freeze['revision']/e['path'];file.parent.mkdir(parents=True,exist_ok=True)
 with file.open('xb')as f:f.write(raw)
 rows.append({'path':str(file.relative_to(P)),'upstream_path':e['path'],'revision':freeze['revision'],'git_blob':e['sha'],'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':rows,'all_git_blobs_verified':True,'source_executed':False,'framework_imported':False,'packages_installed':False,'weights_downloaded':False,'training_steps':0,'owner_approved':False,'training_excluded':True}
with(P/'mlx-module-source-fetch-v1.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'source_files':len(rows),'bytes':sum(e['bytes']for e in rows)})
