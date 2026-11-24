"""Read public PyPI version/dependency declarations, no installation or binaries."""
from pathlib import Path
import json,hashlib,datetime,urllib.request
P=Path(__file__).resolve().parent;out=P/'native-wheel-metadata-v1'
url='https://pypi.org/pypi/tokenizers/json'
with urllib.request.urlopen(url,timeout=45) as r:raw=r.read(4000001);assert len(raw)<=4000000
with (out/'tokenizers-latest-version-census.json').open('xb') as f:f.write(raw)
data=json.loads(raw)
versions=sorted(v for v in data['releases'] if v.startswith('0.22.') or v.startswith('0.23.'))
rows=[]
for v in versions:
 if any(c.isalpha() for c in v):continue
 u='https://pypi.org/pypi/tokenizers/'+v+'/json'
 with urllib.request.urlopen(u,timeout=45) as r:b=r.read(4000001);assert len(b)<=4000000
 with (out/('tokenizers-'+v+'-dependency.json')).open('xb') as f:f.write(b)
 d=json.loads(b);rows.append({'version':v,'url':u,'sha256':hashlib.sha256(b).hexdigest(),'requires_dist':d['info'].get('requires_dist'),'requires_python':d['info'].get('requires_python'),'arm64_wheels':[{'filename':x['filename'],'sha256':x['digests']['sha256'],'yanked':x.get('yanked')} for x in d['urls'] if 'arm64' in x['filename'] and x['filename'].endswith('.whl')]})
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'census_url':url,'census_sha256':hashlib.sha256(raw).hexdigest(),'latest_reported':data['info']['version'],'range_release_keys':versions,'stable_range_version_metadata':rows,'trigger':'Transformers5.7.0 requires huggingface-hub>=1.5,<2 while tokenizers0.22.0 floor metadata requires hub<1.0. A permissible range alone is not a mutually resolvable lock. Inspect other published allowed versions without installing.','no_binary_download':True,'no_installs':True,'not_resolver_run':True,'gold':0,'optimizer_updates':0}
with (P/'native-tokenizers-dependency-range-metadata-v1.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
