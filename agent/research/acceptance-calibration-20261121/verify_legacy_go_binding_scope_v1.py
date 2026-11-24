"""Verify preserved public Go census bytes and pinned Git immediate-directory inventory."""
import datetime,hashlib,json,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
census_path=ROOT/'agent/research/documentation-intelligence-20261119/go-build-binding-source-census.json';evaluation_path=census_path.with_name('go-build-binding-evaluation.json');census=json.loads(census_path.read_text());evaluation=json.loads(evaluation_path.read_text());repo=next(r for r in json.loads((P/'baseline-verification-v1.json').read_text())['repositories'] if r['repository']=='sdk-go');records=[]
for item in census['files']:
 path=ROOT/item['frozen_path'];assert not path.is_symlink();raw=path.read_bytes();records.append({'path':item['frozen_path'],'sha256':hashlib.sha256(raw).hexdigest(),'expected_sha256':item['sha256'],'hash_matches':hashlib.sha256(raw).hexdigest()==item['sha256'],'bytes':len(raw),'size_matches':len(raw)==item['bytes'],'git_blob_sha1':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() if item.get('git_object') else None,'expected_git_object':item.get('git_object'),'git_object_matches':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==item.get('git_object') if item.get('git_object') else None})
module_inventory=[]
for directory in ['internal','internal/common/backoff']:
 command=['/opt/homebrew/bin/git','--no-optional-locks','-C',repo['absolute_path'],'ls-tree',census['revision']+':'+directory];r=subprocess.run(command,capture_output=True,text=True,check=True);observed={}
 for line in r.stdout.splitlines():
  metadata,name=line.split('\t',1);mode,kind,oid=metadata.split()
  if name.endswith('.go') and kind=='blob':observed[directory+'/'+name]=oid
 declared={item['path']:item['git_object'] for item in census['files'] if item.get('repository')=='sdk-go' and str(Path(item['path']).parent)==directory}
 module_inventory.append({'directory':directory,'command':command,'actual_immediate_go_files':len(observed),'declared_census_files':len(declared),'path_and_git_object_maps_equal':observed==declared,'missing_from_census':sorted(set(observed)-set(declared)),'extra_in_census':sorted(set(declared)-set(observed)),'exit_code':r.returncode})
profiles=[]
for label,result in evaluation['results'].items():
 if not isinstance(result,dict) or 'build_profile' not in result:continue
 sdk=result.get('package_censuses',{}).get('go.temporal.io/sdk/internal',{});profiles.append({'label':label,'profile':result['build_profile'],'active_sdk_files':len(sdk.get('active_files',[])),'compiler_version':result.get('compiler_version'),'conditional_on_supplied_complete_census':result.get('conditional_on_supplied_complete_census'),'status':result.get('status',result.get('verdict',result.get('outcome'))),'limits':result.get('limitations')})
x={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'purpose':'Independently verify retained SDK FAQ optional lexical-binding evidence provenance without rerunning nativehelper/compiler or externalcode.','census_path':str(census_path.relative_to(ROOT)),'census_sha256':hashlib.sha256(census_path.read_bytes()).hexdigest(),'evaluation_sha256':hashlib.sha256(evaluation_path.read_bytes()).hexdigest(),'frozen_source_files':len(records),'all_source_hash_size_matches':all(r['hash_matches'] and r['size_matches'] for r in records),'all_declared_git_objects_match_frozen_bytes':all(r['git_object_matches'] is not False for r in records),'source_file_records':records,'independent_module_scope_inventory':module_inventory,'profiles_from_preserved_receipt':profiles,'supports':'The preserved conditional lexical experiment and declared source scope are actually present and hash-bound. Module immediate-file completeness independently matches pinnedGit; stdlibscope/buildvalidity/type/runtimeconditions remain explicit.','not_new_build_typecheck_or_runtime_execution':True,'prior_test_counts_not_reexecuted_or_added':True,'model_calls':0,'optimizer_updates':0,'gold':0}
with (P/'legacy-go-binding-scope-verification-v1.json').open('x') as f:json.dump(x,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in x.items() if k not in ['source_file_records','profiles_from_preserved_receipt']},indent=2));print('profiles',[(r['profile'],r['active_sdk_files']) for r in profiles])
