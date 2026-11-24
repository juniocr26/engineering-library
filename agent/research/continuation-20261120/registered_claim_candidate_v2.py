"""Paired in-memory claim candidates from registered sources and owned documents.

Research only. No filesystem applier or production planner handoff is provided.
"""
import copy
from contextlib import ExitStack
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

P=Path(__file__).resolve().parent;ROOT=P.parents[2];sys.path.insert(0,str(ROOT/'agent/tools'))
import documentation_candidates as candidates
import documentation_workspace as workspace
spec=importlib.util.spec_from_file_location('claim_candidate_source_binding',P/'registered_declaration_binding_v2.py');binding=importlib.util.module_from_spec(spec);spec.loader.exec_module(binding)
OWN_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
BINDING_SHA=hashlib.sha256(Path(binding.__file__).read_bytes()).hexdigest()
CANDIDATES_SHA=hashlib.sha256(Path(candidates.__file__).read_bytes()).hexdigest()
SHA=re.compile(r'[0-9a-f]{64}')
canonical=binding.canonical
sha=lambda raw:hashlib.sha256(raw).hexdigest()

class SourceExecutionUncertain(ValueError):
 pass

class RegisteredClaimCandidate:
 def __init__(self,registration):
  if type(registration)is not dict:raise ValueError('explicit paired review registration required')
  self.registration=copy.deepcopy(registration);r=self.registration
  if set(r)!={'schema_version','scope','source_registration','documentation_root','documents','claim_id','managed_ownership','human_authored'}or type(r['schema_version'])is not int or r['schema_version']!=1 or r['scope']!='registered-declaration-review':raise ValueError('closed research review registration required')
  if r['managed_ownership']is not True or r['human_authored']is not False:raise ValueError('explicit owned synthetic claim required; markers alone grant no ownership')
  if type(r['claim_id'])is not str or not re.fullmatch(candidates.IDENTIFIER,r['claim_id']):raise ValueError('bounded claim identity required')
  root=Path(r['documentation_root'])
  if not root.is_absolute()or'..'in root.parts:raise ValueError('absolute canonical documentation root required')
  with workspace.directory(root)as fd:entry=os.fstat(fd);self._root_identity=(entry.st_dev,entry.st_ino)
  if type(r['documents'])is not dict or set(r['documents'])!={'en','pt-br'}:raise ValueError('explicit paired document registration required')
  for row in r['documents'].values():
   if type(row)is not dict or set(row)!={'path','file_sha256','block_sha256'}:raise ValueError('closed document path/hash registration required')
   workspace.relative_path(row['path'])
   if not row['path'].endswith('.md')or any(type(row[k])is not str or not SHA.fullmatch(row[k])for k in ['file_sha256','block_sha256']):raise ValueError('bounded Markdown path and exact hashes required')
  if len({v['path']for v in r['documents'].values()})!=2:raise ValueError('language documents must have distinct registered paths')
  self.source_binding=binding.RegisteredDeclaration(r['source_registration'])
  if r['claim_id']not in r['source_registration']['contracts']:raise ValueError('claim outside registered source contracts')
  self._registration_bytes=canonical(r);self._registration_sha256=sha(self._registration_bytes)

 def configuration(self):
  if canonical(self.registration)!=self._registration_bytes:raise ValueError('candidate registration changed; explicit new instance required')
  return json.loads(self._registration_bytes)

 def source_result(self,packet,expected):
  result=copy.deepcopy(self.source_binding.decide(copy.deepcopy(packet)))
  if type(result)is not dict or result.get('action')!=expected or expected not in ['MODIFY','NO-OP']:raise ValueError('source recommendation differs from requested supported review action')
  if result.get('physical_source_bytes_and_registered_paths_verified')is not True:raise ValueError('current source paths and bytes not verified')
  if result.get('source_executed')is not False:raise SourceExecutionUncertain('delegate execution report violates the required no-execution contract; overall status is uncertain')
  for flag in ['physical_documentation_certified','upstream_git_revision_authenticated','owner_approved','training_gold','publication_authorized','automatic_candidate_applier_supported']:
   if result.get(flag)is not False:raise ValueError('source delegate changed false authority/execution contract: '+flag)
  for count in ['writes','model_calls']:
   if type(result.get(count))is not int or result[count]!=0:raise ValueError('source delegate changed zero-operation contract')
  if result.get('registration_sha256')!=self.source_binding._registration_sha256 or result.get('request_sha256')!=sha(canonical(packet)):raise ValueError('source delegate belongs to a different registration or packet')
  return result

 def prepare(self,packet,replacements,expected_action):
  result={'version':'0.0.2-research','status':'REFUSED','writes':0,'model_calls':0,'source_executed':False,'owner_approved':False,'training_gold':False,'publication_authorized':False,'automatic_candidate_applier_supported':False,'physical_documentation_certified':False,'registration_sha256':self._registration_sha256}
  try:
   if sha(Path(__file__).read_bytes())!=OWN_SHA or sha(Path(binding.__file__).read_bytes())!=BINDING_SHA or sha(Path(candidates.__file__).read_bytes())!=CANDIDATES_SHA:raise ValueError('loaded review producer changed; reload required')
   config=self.configuration();packet=copy.deepcopy(packet);replacements=copy.deepcopy(replacements)
   if type(packet)is not dict or packet.get('logical_contract_id')!=config['claim_id']:raise ValueError('packet does not address registered claim')
   if expected_action not in ['MODIFY','NO-OP']:raise ValueError('review prototype supports no addition or retirement')
   if type(packet.get('documentation'))is not dict or set(packet['documentation'])!={'en','pt-br'}:raise ValueError('paired original claim required')
   if expected_action=='NO-OP':
    if replacements is not None:raise ValueError('NO-OP cannot carry replacement')
   elif type(replacements)is not dict or set(replacements)!={'en','pt-br'}:raise ValueError('complete paired replacement required')
   with ExitStack()as stack:
    docs_fd=stack.enter_context(workspace.directory(config['documentation_root']));s=os.fstat(docs_fd)
    if (s.st_dev,s.st_ino)!=self._root_identity:raise ValueError('documentation root replaced since registration')
    source_fds={};source_identities={}
    contract=config['source_registration']['contracts'][config['claim_id']]
    for when in ['previous','current']:
     registered=config['source_registration']['sources'][when];fd=stack.enter_context(workspace.directory(registered['root']));source_fds[when]=fd
     rootstat=os.fstat(fd);source_identities[when]=((rootstat.st_dev,rootstat.st_ino),binding.leaf_identity(fd,contract[when+'_path']))
    documents={}
    for lang,entry in config['documents'].items():
     identity=binding.leaf_identity(docs_fd,entry['path']);raw,meta=workspace.read(docs_fd,entry['path'],candidates.MAX_DOCUMENT)
     if identity!=binding.leaf_identity(docs_fd,entry['path'])or meta['sha256']!=entry['file_sha256']:raise ValueError('registered whole document identity changed')
     blocks=candidates.blocks(raw)
     if config['claim_id']not in blocks:raise ValueError('registered addressed claim block is missing')
     start,end=blocks[config['claim_id']];body=raw[start.end():end.start()]
     if sha(body)!=entry['block_sha256']or candidates.claim_text(body)!=packet['documentation'][lang]:raise ValueError('registered block hash or physical claim text differs')
     documents[lang]={'raw':raw,'identity':identity,'start':start.end(),'end':end.start(),'body':body,'outside_sha256':sha(raw[:start.end()]+raw[end.start():])}
    original=self.source_result(packet,expected_action)
    if expected_action=='MODIFY':
     for text in replacements.values():
      if type(text)is not str or len(text.encode())>65536 or '<!-- documentation-agent:'in text:raise ValueError('invalid bounded marker-free replacement')
      candidates.claim_text(text.encode())
     proposal=copy.deepcopy(packet);proposal['documentation']={k:candidates.claim_text(v.encode())for k,v in replacements.items()}
     proposed=self.source_result(proposal,'NO-OP')
     if proposed['physical_source_binding']!=original['physical_source_binding']:raise ValueError('source changed between original and replacement recommendations')
    else:proposed=original
    prepared={}
    for lang,doc in documents.items():
     raw=doc['raw'];candidate=raw if expected_action=='NO-OP'else raw[:doc['start']]+replacements[lang].encode()+raw[doc['end']:]
     if len(candidate)>candidates.MAX_DOCUMENT:raise ValueError('candidate exceeds document size bound')
     candidates.blocks(candidate)
     prepared[lang]={'markdown':candidate.decode(),'original_sha256':sha(raw),'candidate_sha256':sha(candidate),'outside_managed_body_sha256':doc['outside_sha256'],'changed':candidate!=raw,'path':config['documents'][lang]['path']}
    # Neither language result escapes before the complete pair and all paths recheck.
    for lang,entry in config['documents'].items():
     raw,meta=workspace.read(docs_fd,entry['path'],candidates.MAX_DOCUMENT)
     if raw!=documents[lang]['raw']or binding.leaf_identity(docs_fd,entry['path'])!=documents[lang]['identity']:raise ValueError('documentation changed during source observation')
    with workspace.directory(config['documentation_root'])as fd:
     s=os.fstat(fd)
     if (s.st_dev,s.st_ino)!=self._root_identity:raise ValueError('documentation root path changed during source observation')
    for when,fd in source_fds.items():
     registered=config['source_registration']['sources'][when]
     with workspace.directory(registered['root'])as reopened:
      rootstat=os.fstat(reopened)
      if (rootstat.st_dev,rootstat.st_ino)!=source_identities[when][0]:raise ValueError('source root path changed during candidate preparation')
     if binding.leaf_identity(fd,contract[when+'_path'])!=source_identities[when][1]:raise ValueError('source file identity changed during candidate preparation')
    self.configuration()
    result.update(status='PREPARED',action=expected_action,candidates=prepared,physical_claim_block_bytes_verified=True,physical_source_bytes_and_registered_paths_verified=True,original_source_observation=original,replacement_source_observation=proposed,producer_sha256=OWN_SHA,limits=['One addressed owned claim body only; no complete chapter, link/citation freshness or semantic certification.','No filesystem publication/applier or production planner integration.','Operator registration is not a signature or independent upstream Git authentication.','Sequential checks do not prevent future owner edits after return.'])
   return result
  except SourceExecutionUncertain as error:
   result.update(source_executed=None,source_execution_status='No inspected source executed by candidate layer; delegate execution report is inconsistent or unknown.',reason=str(error));return result
  except (ValueError,TypeError,KeyError,UnicodeError,OSError,RecursionError)as error:
   result['reason']=str(error)[:1024];return result
