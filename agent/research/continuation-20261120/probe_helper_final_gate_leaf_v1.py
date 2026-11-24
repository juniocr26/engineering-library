"""New owned final-gate timing mutation; frozen expectation, no source execution."""
import copy,datetime,hashlib,importlib.util,json,os,sys
from pathlib import Path
P=Path(__file__).resolve().parent;version=sys.argv[1]if len(sys.argv)>1 else'v1';assert version in ['v1','v2']
oracle_path=P/'registered-helper-final-gate-oracle-v1.json'
if not oracle_path.exists():
 assert version=='v1'
 oracle={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'id':'same-bytes-leaf-replacement-before-second-gate','expected_action':'INCONCLUSIVE','expected_physical_binding':False,'mutation':'Owned wrapper replaces current source leaf with identical bytes immediately before invoking second existing physical gate. The composition must compare its held pre-helper leaf identity after that final gate as well.','source_executed':False,'training_excluded':True}
 with oracle_path.open('x')as f:f.write(json.dumps(oracle,indent=2)+'\n')
oracle=json.loads(oracle_path.read_text());spec=importlib.util.spec_from_file_location('helper_final_gate_'+version,P/('registered_helper_binding_'+version+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
work=Path('/private/tmp/el-helper-final-gate-leaf-20261120-'+version);work.mkdir(exist_ok=False);packet=copy.deepcopy(json.loads((P/'registered-helper-binding-oracle-v2.json').read_text())['packet']);sources={}
for when,key in [('previous','previous_source'),('current','current_source')]:
 root=work/when;root.mkdir();raw=packet[key].encode();(root/'module.py').write_bytes(raw);sources[when]={'root':str(root),'revision':('1'if when=='previous'else'2')*40,'files':{'module.py':hashlib.sha256(raw).hexdigest()}}
config={'schema_version':1,'scope':'registered-module-research','sources':sources,'contracts':{'owned.f':{'selector':'f','previous_path':'module.py','current_path':'module.py'}}};instance=m.RegisteredHelper(config);original=instance.gate.decide;calls=0;identities=[]
def gate(value):
 global calls
 calls+=1
 if calls==2:
  path=work/'current/module.py';before=path.stat();raw=path.read_bytes();tmp=path.with_suffix('.replacement');tmp.write_bytes(raw);os.replace(tmp,path);after=path.stat();identities.append({'old_inode':before.st_ino,'new_inode':after.st_ino,'same_bytes':path.read_bytes()==raw})
 return original(value)
instance.gate.decide=gate;observed=instance.decide(packet);passed=observed['action']==oracle['expected_action']and observed['physical_source_bytes_and_registered_paths_verified']is oracle['expected_physical_binding']
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'version':version,'oracle_sha256':hashlib.sha256(oracle_path.read_bytes()).hexdigest(),'observed':observed,'mutation':identities,'physical_gate_calls':calls,'pass':passed,'source_executed':False,'owned_timing_injection_not_observed_external_attack':True}
with(P/('registered-helper-final-gate-result-'+version+'.json')).open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'version':version,'pass':passed,'action':observed['action'],'physical_binding':observed['physical_source_bytes_and_registered_paths_verified'],'mutation':identities})
