"""Frozen paired-candidate controls; all mutable files are exclusive owned /tmp data."""
import argparse,copy,datetime,hashlib,importlib.util,json,os
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('version',choices=['1','2']);args=parser.parse_args()
 spec=importlib.util.spec_from_file_location('candidate_under_observation',P/('registered_claim_candidate_v'+args.version+'.py'));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 protocol=json.loads((P/'registered-claim-candidate-protocol-v1.json').read_text());source=json.loads((P/'registered-slugify-real-protocol-v1.json').read_text())
 base=Path('/private/tmp/el-claim-candidate-controls-20261120-v'+args.version);base.mkdir(exist_ok=False);rows=[]
 for control in protocol['expected_controls']:
  id=control['id'];case=base/id;case.mkdir();docs=case/'docs';docs.mkdir();packet=copy.deepcopy(source['cases'][0]['packet']);claim=packet['logical_contract_id']
  replacement={'en':'smart_truncate has a word_boundary parameter.\n','pt-br':'smart_truncate possui parâmetro word_boundary.\n'};action='MODIFY'
  if id=='valid-addressed-noop':packet['documentation']={k:v[:-1]for k,v in replacement.items()};action='NO-OP';replacement=None
  entries={};original_docs={}
  for lang in ['en','pt-br']:
   body=(packet['documentation'][lang]+'\n').encode();raw=b'# Human context before\n\n'+('<!-- documentation-agent:claim:'+claim+':start -->\n').encode()+body+('<!-- documentation-agent:claim:'+claim+':end -->\n').encode()+b'\nHuman context after; citations remain separately unverified.\n';(docs/(lang+'.md')).write_bytes(raw);original_docs[lang]=raw;entries[lang]={'path':lang+'.md','file_sha256':sha(raw),'block_sha256':sha(body)}
  registration={'schema_version':1,'scope':'registered-declaration-review','source_registration':source['registration'],'documentation_root':str(docs),'documents':entries,'claim_id':claim,'managed_ownership':True,'human_authored':False}
  initial={'registration':copy.deepcopy(registration),'original_documents':{k:v.decode()for k,v in original_docs.items()},'packet':copy.deepcopy(packet),'replacements':copy.deepcopy(replacement),'requested_action':action}
  (case/'exact-control-preimage.json').write_text(json.dumps(initial,ensure_ascii=False,indent=2)+'\n')
  if id in ['stale-en-file','stale-pt-file']:
   lang='en'if id=='stale-en-file'else'pt-br';(docs/(lang+'.md')).write_bytes(original_docs[lang]+b'Changed outside claim.\n')
  if id in ['stale-en-block','stale-pt-block']:entries['en'if id=='stale-en-block'else'pt-br']['block_sha256']='0'*64
  if id in ['actual-en-claim-differs','actual-pt-claim-differs']:packet['documentation']['en'if id=='actual-en-claim-differs'else'pt-br']='Different actual claim.'
  if id=='human-authored-registry':registration['human_authored']=True
  if id=='managed-ownership-missing':registration['managed_ownership']=False
  if id in ['missing-owned-marker','nested-owned-marker']:
   raw=original_docs['en']
   if id=='missing-owned-marker':raw=b'No addressed markers here.\n'
   else:raw=raw.replace(b'# Human context before\n\n',b'<!-- documentation-agent:claim:other:start -->\n')+b'<!-- documentation-agent:claim:other:end -->\n'
   (docs/'en.md').write_bytes(raw);entries['en']['file_sha256']=sha(raw)
  if id in ['symlink-doc','fifo-doc']:
   (docs/'en.md').rename(case/'preserved-en.md')
   if id=='symlink-doc':(docs/'en.md').symlink_to(case/'preserved-en.md')
   else:os.mkfifo(docs/'en.md')
  if id=='incorrect-replacement-one-language':replacement['pt-br']='smart_truncate possui parâmetro word_boundaries.\n'
  if id=='replacement-marker-injection':replacement['en']+='<!-- documentation-agent:claim:other:start -->\n'
  if id=='requested-remove':action='REMOVE'
  calls=[0]
  try:
   candidate=module.RegisteredClaimCandidate(registration);original=candidate.source_binding.decide
   def delegate(p):
    calls[0]+=1;result=original(p)
    if id=='doc-changes-during-source-observation'and calls[0]==1:(docs/'pt-br.md').write_bytes(original_docs['pt-br']+b'Concurrent owned change.\n')
    if id=='doc-root-replaced-during-observation'and calls[0]==1:
     docs.rename(case/'retained-original-doc-root');docs.mkdir()
     for lang,raw in original_docs.items():(docs/(lang+'.md')).write_bytes(raw)
    if id=='delegate-claims-owner-approval':result['owner_approved']=True
    if id=='delegate-request-identity-mismatch':result['request_sha256']='0'*64
    if id=='delegated-partial-pair-must-not-escape'and calls[0]==2:(docs/'pt-br.md').write_bytes(original_docs['pt-br']+b'Late pair drift.\n')
    return result
   candidate.source_binding.decide=delegate
   result=candidate.prepare(packet,replacement,action)
  except (ValueError,TypeError,KeyError,OSError)as error:result={'status':'REFUSED','reason':str(error),'writes':0,'source_executed':False}
  actual=result['status'];match=actual==control['expected'];assert 'candidates'not in result if actual!='PREPARED'else set(result['candidates'])=={'en','pt-br'}
  if actual=='PREPARED':
   for lang,row in result['candidates'].items():
    proposed=row['markdown'].encode();assert b'# Human context before\n\n'in proposed and b'Human context after; citations remain separately unverified.\n'in proposed
    if action=='NO-OP':assert proposed==original_docs[lang]
  rows.append({'id':id,'expected':control['expected'],'actual':actual,'matches':match,'source_delegate_calls':calls[0],'result':result})
 record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'version':args.version,'controls':len(rows),'correct':sum(r['matches']for r in rows),'rows':rows,'producer_sha256':sha((P/('registered_claim_candidate_v'+args.version+'.py')).read_bytes()),'owned_control_root':str(base),'production_or_public_source_files_written':0,'original_catalog_files_written':0,'neural_model_calls':0,'source_executed':False,'permanent_tests_changed':False,'publication_authorized':False}
 with(P/('registered-claim-candidate-results-v'+args.version+'.json')).open('x')as f:f.write(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'controls':len(rows),'correct':record['correct'],'failures':[{'id':r['id'],'actual':r['actual'],'reason':r['result'].get('reason')}for r in rows if not r['matches']]}))
