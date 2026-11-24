"""Consume relocated V5 grammar and source packs, then verify every expected file unchanged."""
import copy,datetime,hashlib,importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[2];cut=json.loads((P/'recovery-delta-receipt-v5.json').read_text());restore=Path(cut['restored_root']);manifest_path=ROOT/cut['input_manifest']['path'];assert hashlib.sha256(manifest_path.read_bytes()).hexdigest()==cut['input_manifest']['sha256'];manifest=json.loads(manifest_path.read_text());rp=restore/'agent/research/continuation-20261120';module_path=rp/'registered_helper_binding_v2.py';assert hashlib.sha256(module_path.read_bytes()).hexdigest()==manifest['effective_expected_files'][str(module_path.relative_to(restore))]['sha256']
spec=importlib.util.spec_from_file_location('actual_restored_registered_helper_v5',module_path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
assert Path(m.helper.__file__).is_relative_to(restore)and Path(m.binding.workspace.__file__).is_relative_to(restore)
original_registry=json.loads((rp/'registered-helper-boltons-registry-v2.json').read_text());registry=copy.deepcopy(original_registry)
for when in ['previous','current']:
 original=Path(registry['sources'][when]['root']);registry['sources'][when]['root']=str(restore/original.relative_to(ROOT))
instance=m.RegisteredHelper(registry);oracle_path=restore/'agent/research/documentation-intelligence-20261120/public-lifecycle-oracle-v1.json';assert hashlib.sha256(oracle_path.read_bytes()).hexdigest()=='27ccb0d9e6aaf78f06ee6f160290c474e93ee85bc5462ac99aa2aedeb4821ca7';oracle=json.loads(oracle_path.read_text());rows=[]
for case in oracle['cases']:
 file=oracle_path.parent/'public-lifecycle-results-v1'/(case['id']+'.json');assert hashlib.sha256(file.read_bytes()).hexdigest()==manifest['effective_expected_files'][str(file.relative_to(restore))]['sha256'];packet=json.loads(file.read_text())['input'];observed=instance.decide(packet);expected=case.get('expected_action',case.get('expected'));rows.append({'id':case['id'],'expected':expected,'observed':observed,'pass':observed['action']==expected and observed['physical_source_bytes_and_registered_paths_verified']is True})
source_checks=[]
for name in ['humanize-source-pack-v1.json','backoff-source-pack-v1.json']:
 pack=json.loads((rp/name).read_text())
 for id,u in pack['units'].items():
  raw=(rp/u['source_snapshot']).read_bytes();quote='\n'.join(raw.decode().splitlines()[u['first_line']-1:u['last_line']]);source_checks.append({'pack':name,'id':id,'pass':hashlib.sha256(raw).hexdigest()==u['source_sha256']and quote==u['quote']and hashlib.sha256(quote.encode()).hexdigest()==u['quote_sha256']})
all_expected=True
for name,entry in manifest['effective_expected_files'].items():
 file=restore/name
 if not file.is_file()or file.stat().st_size!=entry['bytes']or hashlib.sha256(file.read_bytes()).hexdigest()!=entry['sha256']:raise ValueError('restored expected file changed: '+name)
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'ACTUAL_RELOCATED_RESEARCH_CONSUMER_VERIFIED','restored_root':str(restore),'loaded_module':str(module_path),'loaded_helper_grammar':str(Path(m.helper.__file__)),'loaded_workspace':str(Path(m.binding.workspace.__file__)),'rows':rows,'existing_exposed_packets_replayed':len(rows),'new_independent_cases':0,'all_eight_expected_actions_and_physical_bindings':all(row['pass']for row in rows),'source_quote_checks':source_checks,'source_quote_count':len(source_checks),'all_source_quotes_verified':all(c['pass']for c in source_checks),'all_expected_file_hashes_unchanged':all_expected,'effective_expected_file_count':len(manifest['effective_expected_files']),'registry_relocation':'Explicit new operator configuration changes only source roots to the restored tree; original frozen registry remains unchanged. Not automatic journal migration or upstream Git authentication.','original_registry_sha256':hashlib.sha256(m.binding.canonical(original_registry)).hexdigest(),'relocated_registry_sha256':hashlib.sha256(m.binding.canonical(registry)).hexdigest(),'public_source_executed':False,'native_binaries_or_models_rerun':False,'model_calls':0,'training_steps':0,'publication':False,'owner_approved':False,'limits':'Verified point-in-time code/source/evidence consumption on host Python3.14. No full cold-runtime,remote,image/model-store or future filesystem-edit guarantee.'}
with(P/'restored-research-consumption-v5.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'replayed_packets':len(rows),'all_expected':r['all_eight_expected_actions_and_physical_bindings'],'source_quotes':len(source_checks),'all_quotes_verified':r['all_source_quotes_verified'],'expected_files_unchanged':len(manifest['effective_expected_files'])})
