"""Rebind unchanged exposed public packets; no source/package execution."""
import datetime,hashlib,importlib.util,json
from pathlib import Path
P=Path(__file__).resolve().parent;old=P.parent/'documentation-intelligence-20261120'
spec=importlib.util.spec_from_file_location('registered_public_helper',P/'registered_helper_binding_v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
oraclepath=old/'public-lifecycle-oracle-v1.json';oracle_raw=oraclepath.read_bytes();assert hashlib.sha256(oracle_raw).hexdigest()=='27ccb0d9e6aaf78f06ee6f160290c474e93ee85bc5462ac99aa2aedeb4821ca7';oracle=json.loads(oracle_raw)
packets=[];sources={};contracts={};packetfiles={}
for when,tag,revision in [('previous','24.0.0','992a58c1036fcf4d52cbf3313b6217b7c07b11d9'),('current','25.0.0','c23dbdadb6fecdf505eb4231559561913b84c13f')]:
 root=old/'public-sources'/tag;files={str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest()for f in root.rglob('*.py')};sources[when]={'root':str(root),'revision':revision,'files':files}
for case in oracle['cases']:
 id=case['id'];path=old/'public-lifecycle-results-v1'/(id+'.json');raw=path.read_bytes();packet=json.loads(raw)['input'];packetfiles[str(path)]=hashlib.sha256(raw).hexdigest();packets.append((case,packet));entry={'selector':packet['logical_contract_id'].rsplit('.',1)[-1]}
 for when,key in [('previous','previous_source'),('current','current_source')]:
  digest=hashlib.sha256(packet[key].encode()).hexdigest();matches=[name for name,sha in sources[when]['files'].items()if sha==digest];assert len(matches)==1;entry[when+'_path']=matches[0]
 contracts[packet['logical_contract_id']]=entry
registry={'schema_version':1,'scope':'registered-module-research','sources':sources,'contracts':contracts}
with(P/'registered-helper-boltons-registry-v1.json').open('x')as f:f.write(json.dumps(registry,indent=2)+'\n')
instance=m.RegisteredHelper(registry);rows=[]
for case,packet in packets:
 observed=instance.decide(packet);expected=case.get('expected_action',case.get('expected'));rows.append({'id':case['id'],'expected_action':expected,'observed':observed,'pass':observed['action']==expected and observed['physical_source_bytes_and_registered_paths_verified']is True})
unchanged=hashlib.sha256(oraclepath.read_bytes()).hexdigest()==hashlib.sha256(oracle_raw).hexdigest()and all(hashlib.sha256(Path(name).read_bytes()).hexdigest()==sha for name,sha in packetfiles.items())
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'classification':'DEVELOPMENT_EXPOSED_RESEARCH_PROFILE_WITH_EXISTING_LOCAL_PHYSICAL_BINDING','rows':rows,'passes':sum(x['pass']for x in rows),'cases':len(rows),'frozen_oracle_and_packet_files_unchanged':unchanged,'physical_gate_reused_not_new_algorithm':True,'production_planner_unchanged_score':'0/8','source_executed':False,'upstream_git_authentication_by_binding':False,'training_excluded':True,'owner_approved':False,'publication_authorized':False,'automatic_candidate_applier_supported':False}
with(P/'registered-helper-boltons-results-v1.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'passes':r['passes'],'cases':r['cases'],'unchanged':unchanged,'failures':[{'id':x['id'],'reason':x['observed'].get('reason'),'action':x['observed']['action'],'expected':x['expected_action']}for x in rows if not x['pass']]})
