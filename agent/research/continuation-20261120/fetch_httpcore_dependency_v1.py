import base64, datetime, hashlib, json, urllib.request
from pathlib import Path
P=Path(__file__).resolve().parent
freeze=json.loads((P/'httpcore-dependency-freeze-v1.json').read_text())
rows=[]
for e in freeze['selected_blobs']:
 assert e['size']<=65536 and e['mode']=='100644'
 with urllib.request.urlopen(urllib.request.Request(e['url'],headers={'User-Agent':'EngineeringLibrarySourceResearch/1.0'}),timeout=35) as response: raw=response.read(131073)
 assert len(raw)<=131072
 envelope=json.loads(raw); body=base64.b64decode(envelope['content'])
 assert len(body)==e['size']
 assert hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()==e['sha']
 path=P/'new-public-sources-v1'/'encode--httpcore'/freeze['revision']/e['path']
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('xb') as f:f.write(body)
 rows.append({'path':str(path.relative_to(P)),'bytes':len(body),'git_blob':e['sha'],'sha256':hashlib.sha256(body).hexdigest()})
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository':freeze['repository'],'revision':freeze['revision'],'files':rows,'source_executed':False,'whole_package_imported':False,'installed_dependency_version_asserted':False,'application_http_requests':0,'training_excluded':True,'owner_approved':False}
with (P/'httpcore-dependency-fetch-v1.json').open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
print({'files':len(rows),'bytes':sum(r['bytes']for r in rows),'verified':True})
