"""Fetch only the eight frozen public blob identities; no package/runtime import."""
import concurrent.futures
import datetime
import hashlib
import json
from pathlib import Path
import urllib.request

P = Path(__file__).resolve().parent
freeze = json.loads((P/'httpx-source-family-freeze-v1.json').read_text())

def fetch(pair):
    cut, entry = pair
    revision = cut['revision']
    path = P/'new-public-sources-v1/encode--httpx'/revision/entry['path']
    url = 'https://raw.githubusercontent.com/encode/httpx/' + revision + '/' + entry['path']
    result = {'revision':revision,'tag':cut['tag'],'path':entry['path'],'url':url,'expected_git_blob':entry['sha']}
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EngineeringLibrarySourceResearch/1.0'}),timeout=35) as response:
            raw=response.read(65537)
        if len(raw)>65536:
            raise ValueError('frozen source-byte budget exceeded')
        observed=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if observed!=entry['sha']:
            raise ValueError('public source differs from frozen Git tree blob')
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as stream:
            stream.write(raw)
        result.update(status='VERIFIED',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),git_blob_matches=True)
    except Exception as error:
        result.update(status='FAILED',error=str(error))
    return result

pairs=[(cut,entry)for cut in freeze['revisions']for entry in cut['selected_blobs']]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    rows=list(pool.map(fetch,pairs))
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'freeze_sha256':hashlib.sha256((P/'httpx-source-family-freeze-v1.json').read_bytes()).hexdigest(),'rows':rows,'source_executed':False,'package_installed':False,'http_application_requests':0,'model_calls':0,'training_excluded':True,'certified_neural_holdout':False}
with(P/'httpx-source-provenance-v1.json').open('x') as stream:
    stream.write(json.dumps(record,indent=2)+'\n')
print(json.dumps({'verified':sum(r['status']=='VERIFIED'for r in rows),'failed':[r for r in rows if r['status']!='VERIFIED'],'bytes':sum(r.get('bytes',0)for r in rows)}))
