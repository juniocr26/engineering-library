"""Fetch implementation-frozen public source/notice snapshots; never execute."""
import concurrent.futures
import datetime
import hashlib
import json
from pathlib import Path
import urllib.request

P=Path(__file__).resolve().parent;freeze=json.loads((P/'slugify-evaluation-freeze-v1.json').read_text())
root=P/'new-public-sources-v1/un33k--python-slugify';root.mkdir(exist_ok=False)

def fetch(item):
    rev,name=item;url='https://raw.githubusercontent.com/un33k/python-slugify/'+rev+'/'+name
    row={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'revision':rev,'path':name,'url':url}
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EngineeringLibrarySourceResearch/1.0'}),timeout=40)as response:raw=response.read(65537);row['http_status']=response.status
        if len(raw)>65536:raise ValueError('whole-source bound exceeded;no truncation')
        dest=root/rev/name;dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open('xb')as stream:stream.write(raw)
        row.update(status='preserved',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),local_path=str(dest.relative_to(P)))
    except Exception as error:row.update(status='failed',error=str(error))
    return row

with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:rows=list(pool.map(fetch,[(r['sha'],name)for r in freeze['revisions'].values()for name in freeze['files']]))
with(P/'slugify-source-provenance-v1.json').open('x')as stream:json.dump({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'freeze':'slugify-evaluation-freeze-v1.json','rows':rows,'source_executed':False,'packages_installed':False},stream,indent=2)
print(json.dumps({'preserved':sum(x['status']=='preserved'for x in rows),'failed':[x for x in rows if x['status']!='preserved']}))
