"""Compose existing physical-source gate with the closed helper grammar.
Operator registration is not Git authentication; no documentation patch authority.
"""
import copy,hashlib,importlib.util,os
from contextlib import ExitStack
from pathlib import Path
P=Path(__file__).resolve().parent

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
binding=module('helper_existing_physical_gate',P/'registered_declaration_binding_v2.py')
helper=module('registered_closed_helper_v3',P/'closed_helper_lifecycle_v3.py')
OWN_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
DEPENDENCIES={str(Path(m.__file__)):hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()for m in [binding,helper]}

def sha(value):return hashlib.sha256(binding.canonical(value)).hexdigest()

class RegisteredHelper:
 def __init__(self,registration):
  self.gate=binding.RegisteredDeclaration(registration)
 def decide(self,packet):
  result={'version':'0.0.1-research','action':'INCONCLUSIVE','source_executed':False,'physical_source_bytes_and_registered_paths_verified':False,'physical_documentation_certified':False,'upstream_git_revision_authenticated':False,'owner_approved':False,'training_gold':False,'publication_authorized':False,'automatic_candidate_applier_supported':False,'model_calls':0,'writes':0,'producer_sha256':OWN_SHA,'binding_reused':'registered_declaration_binding_v2.py','helper_grammar':'closed_helper_lifecycle_v3.py'}
  try:
   if hashlib.sha256(Path(__file__).read_bytes()).hexdigest()!=OWN_SHA or any(hashlib.sha256(Path(path).read_bytes()).hexdigest()!=expected for path,expected in DEPENDENCIES.items()):raise ValueError('loaded composition implementation drift; reload required')
   packet=copy.deepcopy(packet);request_sha=sha(packet);config=self.gate.configuration()
   if type(packet)is not dict or packet.get('logical_contract_id')not in config['contracts']:raise ValueError('registered logical contract required')
   contract=config['contracts'][packet['logical_contract_id']]
   first=self.gate.decide(copy.deepcopy(packet))
   if first.get('source_executed')is not False:result['source_executed']=None;raise ValueError('physical gate execution report uncertain')
   if first.get('physical_source_bytes_and_registered_paths_verified')is not True:raise ValueError('existing physical gate refused: '+first.get('reason','unspecified'))
   snapshots={};fds={}
   with ExitStack()as stack:
    for when,key in [('previous','previous_source'),('current','current_source')]:
     source=config['sources'][when];fd=stack.enter_context(binding.workspace.directory(source['root']));fds[when]=fd;st=os.fstat(fd)
     if(st.st_dev,st.st_ino)!=self.gate._root_identities[when]:raise ValueError('registered root changed before helper observation')
     name=contract[when+'_path'];identity=binding.leaf_identity(fd,name);raw,meta=binding.workspace.read(fd,name,65536)
     if identity!=binding.leaf_identity(fd,name)or meta['sha256']!=source['files'][name]or raw!=packet[key].encode():raise ValueError('registered leaf changed before helper observation')
     snapshots[when]={'identity':identity,'raw':raw,'path':name,'sha256':meta['sha256']}
    observed=copy.deepcopy(helper.decision(copy.deepcopy(packet)))
    if type(observed)is not dict:raise ValueError('helper result must be an explicit object')
    for flag in ['source_executed','runtime_bindings_verified','physical_source_paths_authenticated','physical_documentation_certified','owner_approved','training_gold','publication_authorized','automatic_candidate_applier_supported']:
     if observed.get(flag)is not False:
      if flag=='source_executed':result['source_executed']=None
      raise ValueError('helper authority/execution flag changed: '+flag)
    for count in ['writes','model_calls']:
     if type(observed.get(count))is not int or observed[count]!=0:raise ValueError('helper zero-operation contract changed: '+count)
    if observed.get('helper_admission_fallback')is True:
     if observed.get('helper_admission_producer_sha256')!=helper.OWN_SHA or observed.get('producer_sha256')!=helper.fallback.OWN_SHA:raise ValueError('helper fallback producer mismatch')
    elif observed.get('producer_sha256')!=helper.OWN_SHA:raise ValueError('helper producer mismatch')
    if observed.get('action')not in ['ADD','MODIFY','NO-OP','INCONCLUSIVE']:raise ValueError('helper action outside no-retirement contract')
    if observed['action']!='INCONCLUSIVE':
     if observed.get('original_packet_sha256')!=request_sha:raise ValueError('helper packet identity mismatch')
     selected=observed.get('selector')
     if selected is None and observed.get('helper_admission_fallback')is True:
      nested=observed.get('declaration_observation',{})
      if nested.get('producer_sha256')!=helper.declaration.OWN_SHA or nested.get('original_packet_sha256')!=request_sha:raise ValueError('nested declaration producer/request mismatch')
      selected=nested.get('selector')
     if selected!=contract['selector']:raise ValueError('helper selector differs from registration')
    for when in ['previous','current']:
     source=config['sources'][when];fd=fds[when];snapshot=snapshots[when]
     with binding.workspace.directory(source['root'])as reopened:
      a,b=os.fstat(fd),os.fstat(reopened)
      if(a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino):raise ValueError('registered source root replaced during helper observation')
     raw,meta=binding.workspace.read(fd,snapshot['path'],65536)
     if raw!=snapshot['raw']or meta['sha256']!=snapshot['sha256']or binding.leaf_identity(fd,snapshot['path'])!=snapshot['identity']:raise ValueError('physical source leaf identity/bytes changed during helper observation')
    second=self.gate.decide(copy.deepcopy(packet))
    if second.get('source_executed')is not False:result['source_executed']=None;raise ValueError('final physical gate execution report uncertain')
    if second.get('physical_source_bytes_and_registered_paths_verified')is not True or second.get('request_sha256')!=request_sha:raise ValueError('final physical gate refused')
    self.gate.configuration()
    result.update(action=observed['action'],reason=observed.get('reason'),observation=observed,request_sha256=request_sha,registration_sha256=self.gate._registration_sha256,physical_source_bytes_and_registered_paths_verified=True,physical_source_binding=second['physical_source_binding'],legacy_gate_actions_ignored=[first['action'],second['action']],binding_scope='Existing descriptor-checked local paths/bytes and held leaf identities across closed helper observation; operator revision assertions are not independent Git authentication. Future edits and physical documentation are not certified.')
   return result
  except(ValueError,TypeError,KeyError,UnicodeError,OSError,RecursionError)as error:
   result.update(action='INCONCLUSIVE',reason=str(error)[:1024]);return result
