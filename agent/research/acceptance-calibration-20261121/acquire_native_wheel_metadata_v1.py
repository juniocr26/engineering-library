"""Read PyPI JSON metadata only. No wheel/source distribution download or package installation."""
from pathlib import Path
import json,hashlib,datetime,urllib.request,sys,sysconfig,platform
P=Path(__file__).resolve().parent;out=P/'native-wheel-metadata-v1';out.mkdir(exist_ok=False);records=[]
for package,version in [('mlx','0.32.3'),('transformers','5.7.0'),('mlx-lm',None)]:
 url='https://pypi.org/pypi/'+package+('/'+version if version else '')+'/json'
 with urllib.request.urlopen(url,timeout=45) as r:raw=r.read(4000001);assert len(raw)<=4000000
 f=out/(package+'.json');f.write_bytes(raw);data=json.loads(raw);record={'package':package,'requested_version':version,'reported_version':data['info']['version'],'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'requires_python':data['info'].get('requires_python'),'requires_dist':data['info'].get('requires_dist'),'distribution_names':[x['filename'] for x in data['urls']],'binary_distribution_bytes_downloaded':0};records.append(record)
receipt={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':{'python':sys.version,'cache_tag':sys.implementation.cache_tag,'sysconfig_platform':sysconfig.get_platform(),'architecture':platform.machine(),'mac_ver':platform.mac_ver()[0],'GIL_disabled':sysconfig.get_config_var('Py_GIL_DISABLED')},'packages':records,'scope':'Metadata and declared artifact tag availability only; not resolved dependency lock, installation/import/ABI/Metal validation or native hardware measurement. Latest released package is not assumed to equal separately pinned sourcecommit.','binary_distributions_downloaded':0,'source_distributions_downloaded':0,'framework_installed':False,'weights_downloaded':0,'optimizer_updates':0,'all_nine_readiness_gates_still_NO_GO':True}
(P/'native-wheel-metadata-receipt-v1.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
