"""Preserve complete tracked non-test root Go package; verify Git blob identities."""
import concurrent.futures
import datetime
import hashlib
import json
from pathlib import Path
import urllib.request

P=Path(__file__).resolve().parent
protocol=json.loads((P/'go-geom-root-package-protocol-v1.json').read_text())
tree=json.loads((P/'go-geom-revision-tree-v1.json').read_text())
revision=protocol['revision'];base=P/'new-public-sources-v1/twpayne--go-geom'/revision
entries=protocol['root_non_test_go_files']+[x for x in tree['tree']if x['type']=='blob'and x['path']in['go.mod','go.sum']]


def fetch(entry):
    path=base/entry['path'];url='https://raw.githubusercontent.com/twpayne/go-geom/'+revision+'/'+entry['path'];r={'path':entry['path'],'revision':revision,'git_blob':entry['sha'],'url':url,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        if path.exists():raw=path.read_bytes();r['origin']='already-preserved'
        else:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EngineeringLibrarySourceResearch/1.0'}),timeout=40)as response:raw=response.read(262145)
            if len(raw)>262144:raise ValueError('per-file bound exceeded')
            blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            if blob!=entry['sha']:raise ValueError('Git tree/body identity mismatch')
            with path.open('xb')as stream:stream.write(raw)
            r['origin']='new-read-only-snapshot'
        blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if blob!=entry['sha']:raise ValueError('preserved source differs from exact Git tree')
        r.update(status='verified',sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),git_blob_verified=True)
    except Exception as error:r.update(status='failed',error=str(error))
    return r


with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:rows=list(pool.map(fetch,entries))
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'revision':revision,'rows':rows,'source_executed':False,'source_compiled':False,'new_packages_installed':False,'tree_complete_reported':True}
with(P/'go-geom-root-package-provenance-v1.json').open('x')as stream:json.dump(r,stream,indent=2)
print(json.dumps({'verified':sum(x['status']=='verified'for x in rows),'new_files':sum(x.get('origin')=='new-read-only-snapshot'for x in rows),'failed':[x for x in rows if x['status']!='verified']}))
