"""Additional public dependency artifact metadata; no distributions or installation."""
from pathlib import Path
import urllib.request,json,hashlib,datetime
P=Path(__file__).resolve().parent;out=P/'native-wheel-metadata-v1';records=[]
for package,version in [('mlx-metal','0.32.3'),('tokenizers','0.23.0')]:
 url='https://pypi.org/pypi/'+package+'/'+version+'/json'
 with urllib.request.urlopen(url,timeout=45) as response:raw=response.read(4000001);assert len(raw)<=4000000
 (out/(package+'.json')).write_bytes(raw);d=json.loads(raw);matches=[{k:x[k] for k in ['filename','size','digests','requires_python','yanked']} for x in d['urls'] if x['filename'].endswith('.whl') and ('arm64' in x['filename'] or 'none-any' in x['filename'])];records.append({'package':package,'version':version,'URL':url,'metadata_sha256':hashlib.sha256(raw).hexdigest(),'requires_python':d['info'].get('requires_python'),'requires_dist':[s for s in d['info'].get('requires_dist',[]) if 'extra ==' not in s],'declared_arm64_or_universal_wheels':matches})
(P/'native-wheel-metadata-supplement-v2.json').write_text(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'packages':records,'distribution_bytes_downloaded':0,'framework_installed':False,'optimizer_updates':0,'not_a_dependency_lock_or_native_validation':True},indent=2)+'\n');print(json.dumps({'packages':[(r['package'],len(r['declared_arm64_or_universal_wheels'])) for r in records],'binary_downloads':0}))
