"""Primary release listings only; no wheel download, resolver, installation or import."""
import datetime,hashlib,json,platform,sys,sysconfig,urllib.request
from pathlib import Path
P=Path(__file__).resolve().parent
protocol={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'FROZEN_BEFORE_METADATA_REQUESTS','hypothesis':'Primary PyPI metadata for the minimum versions named by pinned MLX-LM may reveal nominal artifact tags for the current interpreter. Listings alone cannot establish complete dependency resolution,installation,Metal support or training feasibility.','packages':[{'name':'mlx','version':'0.32.3'},{'name':'transformers','version':'5.7.0'}],'maximum_metadata_bytes_each':524288,'wheel_or_sdist_body_requests_allowed':False,'packages_installed':False,'framework_imported':False,'weights_or_tokenizer_requested':False,'training_steps':0,'owner_approved':False,'launch_allowed':False}
with(P/'future-framework-release-metadata-protocol-v1.json').open('x')as f:f.write(json.dumps(protocol,indent=2)+'\n')
rows=[]
for package in protocol['packages']:
 label=package['name']+'-'+package['version'];url='https://pypi.org/pypi/'+package['name']+'/'+package['version']+'/json';row={'package':package['name'],'requested_version':package['version'],'url':url,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EngineeringLibraryMetadataResearch/1.0'}),timeout=35)as response:raw=response.read(524289);status=response.status
  assert len(raw)<=524288
  with(P/(label+'-pypi-metadata-v1.json')).open('xb')as f:f.write(raw)
  data=json.loads(raw);assert data['info']['name'].casefold()==package['name']and data['info']['version']==package['version'];files=[{'filename':e['filename'],'package_type':e['packagetype'],'python_version':e['python_version'],'requires_python':e.get('requires_python'),'yanked':e.get('yanked'),'bytes':e['size'],'sha256':e['digests']['sha256'],'upload_time':e['upload_time_iso_8601']}for e in data['urls']];row.update(status='PRESERVED_METADATA_ONLY',http_status=status,metadata_bytes=len(raw),metadata_sha256=hashlib.sha256(raw).hexdigest(),requires_python=data['info'].get('requires_python'),requires_dist=data['info'].get('requires_dist'),files=files)
 except Exception as error:row.update(status='UNRESOLVED_NO_INSTALL_OR_RETRY',error=str(error)[:600])
 rows.append(row)
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':rows,'current_interpreter':{'version':sys.version,'cache_tag':sys.implementation.cache_tag,'abi_flags':sys.abiflags,'sysconfig_platform':sysconfig.get_platform(),'machine':platform.machine(),'system':platform.system()},'full_wheel_tag_compatibility_solver_used':False,'wheel_files_downloaded':0,'packages_installed':0,'framework_imports':0,'optimizer_steps':0,'dependency_environment_locked':False,'owner_gold':0,'launch_allowed':False,'readiness':'NO-GO_UNCHANGED','limits':'All artifact filenames preserved rather than misclassifying absent exactcp314tags as incompatibility. StableABI/universal/macOSminimum/dependency resolution and actual execution require separate authorizedenvironmentwork.'}
with(P/'future-framework-release-metadata-results-v1.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'packages':[{'name':r['package'],'status':r['status'],'artifact_count':len(r.get('files',[]))}for r in rows],'wheel_downloads':0,'installations':0})
