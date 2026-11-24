"""Finite source-identity and delegate-contract controls, isolated research only."""
import copy,datetime,hashlib,importlib.util,json,os,shutil
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('registered_helper_under_observation',P/'registered_helper_binding_v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
oracle=json.loads((P/'registered-helper-binding-oracle-v2.json').read_text());assert hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()==oracle['producer_sha256']
work=Path('/private/tmp/el-registered-helper-binding-20261120-v2');work.mkdir(exist_ok=False);rows=[];original=m.helper.decision
for case in oracle['cases']:
 name=case['id'];root=work/name;root.mkdir();packet=copy.deepcopy(oracle['packet']);sources={}
 for when,key in [('previous','previous_source'),('current','current_source')]:
  d=root/when;d.mkdir();raw=packet[key].encode();(d/'module.py').write_bytes(raw);sources[when]={'root':str(d),'revision':('1'if when=='previous'else'2')*40,'files':{'module.py':hashlib.sha256(raw).hexdigest()}}
 config={'schema_version':1,'scope':'registered-module-research','sources':sources,'contracts':{'owned.f':{'selector':'f','previous_path':'module.py','current_path':'module.py'}}}
 if name=='registered-hash-drift':config['sources']['current']['files']['module.py']='0'*64
 instance=m.RegisteredHelper(config);current=root/'current/module.py'
 if name=='inline-source-drift':packet['current_source']+='\n'
 if name=='logical-contract-drift':packet['logical_contract_id']='other.f'
 if name=='source-symlink':current.unlink();current.symlink_to(root/'previous/module.py')
 if name=='root-replacement-before':os.rename(root/'current',root/'current.old');shutil.copytree(root/'current.old',root/'current')
 if name=='registration-drift':instance.gate.registration['sources']['current']['revision']='3'*40
 def producer(value):
  out=original(value)
  if name=='same-bytes-leaf-replacement-during':
   raw=current.read_bytes();replacement=current.with_suffix('.replacement');replacement.write_bytes(raw);os.replace(replacement,current)
  if name=='changed-bytes-during':current.write_bytes(current.read_bytes()+b'\n')
  if name=='root-replacement-during':os.rename(root/'current',root/'current.old');shutil.copytree(root/'current.old',root/'current')
  replacements={'producer-mismatch':('producer_sha256','0'*64),'request-mismatch':('original_packet_sha256','0'*64),'selector-mismatch':('selector','other'),'remove-action':('action','REMOVE'),'write-count-bool':('writes',False),'model-count-one':('model_calls',1),'source-execution-unknown':('source_executed',None),'owner-approval-true':('owner_approved',True),'publication-unknown':('publication_authorized',None),'candidate-authority-true':('automatic_candidate_applier_supported',True)}
  if name in replacements:key,value=replacements[name];out[key]=value
  if name=='missing-execution-flag':out.pop('source_executed')
  return out
 m.helper.decision=producer
 try:observed=instance.decide(packet)
 finally:m.helper.decision=original
 passed=observed['action']==case['expected_action']and observed['physical_source_bytes_and_registered_paths_verified']is case['expected_physical_binding']
 if name in ['source-execution-unknown','missing-execution-flag']:passed=passed and observed['source_executed']is None
 rows.append({'id':name,'observed':observed,'pass':passed})
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':rows,'passes':sum(r['pass']for r in rows),'cases':len(rows),'source_executed':False,'fault_injection_is_owned':True,'training_excluded':True,'owner_approved':False,'not_independent_public_accuracy':True}
with(P/'registered-helper-binding-results-v2.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'passes':r['passes'],'cases':r['cases'],'failures':[{'id':x['id'],'reason':x['observed'].get('reason')}for x in rows if not x['pass']]})
