"""Consume the same registered claim prototype on existing Linux/Python3.11."""
import datetime,hashlib,json,subprocess,time
from pathlib import Path
P=Path(__file__).resolve().parent
REMOTE=r'''
import copy,hashlib,importlib.util,json,pathlib,sys
sys.dont_write_bytecode=True
root=pathlib.Path('/sources/engineering-library');p=root/'agent/research/continuation-20261120'
spec=importlib.util.spec_from_file_location('linux_claim_candidate',p/'registered_claim_candidate_v2.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
pre=json.loads((root/'.local-backups/continuation-20261120/paired-claim-controls-v1/receipt.json').read_text())
# Exact initial documents/packet are already preserved in the host regular-file archive.
import tarfile
with tarfile.open(root/'.local-backups/continuation-20261120/paired-claim-controls-v1/regular-control-preimages-and-documents.tar.gz')as tar:
 name='el-claim-candidate-controls-20261120-v1/valid-paired-modify/exact-control-preimage.json';raw=tar.extractfile(name).read()
 expected=next(e for e in pre['regular_files']if e['path']==name);assert hashlib.sha256(raw).hexdigest()==expected['sha256'];initial=json.loads(raw)
base=pathlib.Path('/tmp/el-claim-candidate-linux-20261120-v1');base.mkdir(exist_ok=False)
registration=copy.deepcopy(initial['registration']);hostroot='/Users/juniorosa/Documents/Projetos/Projeto VivaBem/engineering-library'
for source in registration['source_registration']['sources'].values():
 assert source['root'].startswith(hostroot+'/');source['root']=str(root)+source['root'][len(hostroot):]
rows=[]
for action in ['MODIFY','NO-OP']:
 docs=base/action;docs.mkdir();r=copy.deepcopy(registration);r['documentation_root']=str(docs);packet=copy.deepcopy(initial['packet']);replacement=copy.deepcopy(initial['replacements'])
 if action=='NO-OP':packet['documentation']={k:v[:-1]for k,v in replacement.items()};replacement=None
 for language,text in initial['original_documents'].items():
  if action=='NO-OP':text=text.replace(initial['packet']['documentation'][language],packet['documentation'][language])
  raw=text.encode();(docs/(language+'.md')).write_bytes(raw);r['documents'][language]['file_sha256']=hashlib.sha256(raw).hexdigest();r['documents'][language]['block_sha256']=hashlib.sha256((packet['documentation'][language]+'\n').encode()).hexdigest()
 candidate=m.RegisteredClaimCandidate(r);result=candidate.prepare(packet,replacement,action);assert result['status']=='PREPARED',result
 for language,row in result['candidates'].items():
  assert hashlib.sha256(row['markdown'].encode()).hexdigest()==row['candidate_sha256']
 rows.append({'action':action,'result':result})
print(json.dumps({'status':'VERIFIED','python':sys.version,'platform':sys.platform,'rows':rows,'existing_cases_repeated_on_second_os':2,'new_distinct_cases':0,'source_executed':False,'model_calls':0,'publication_authorized':False,'windows_verified':False,'producer_sha256':hashlib.sha256((p/'registered_claim_candidate_v2.py').read_bytes()).hexdigest()}))
'''
start=time.monotonic();r=subprocess.run(['docker','exec','-i','engineering-library-backend-1','python3','-c',REMOTE],text=True,capture_output=True,timeout=120)
(P/'registered-claim-linux-v1.stdout').write_text(r.stdout);(P/'registered-claim-linux-v1.stderr').write_text(r.stderr)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':r.returncode,'wall_seconds':time.monotonic()-start}
if r.returncode==0:record.update(json.loads(r.stdout))
(P/'registered-claim-linux-v1.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items()if k!='rows'}));raise SystemExit(r.returncode)
