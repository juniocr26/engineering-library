from pathlib import Path
import json,hashlib,datetime,subprocess,os
P=Path(__file__).resolve().parent;ROOT=P.parents[2];protocol=P/'pinned-tree-positive-witness-protocol-v1.json';p=json.loads(protocol.read_bytes());ledger=json.loads((P/'repository-action-ledger-v23.json').read_bytes());repo=Path(next(r['absolute_path'] for r in ledger['records'] if r['repository']==p['repository']));folder=P/'pinned-tree-positive-witness-v1';folder.mkdir(mode=0o700,exist_ok=False);objects=folder/'objects';objects.mkdir(mode=0o700);sha=lambda b:hashlib.sha256(b).hexdigest();commands=[];links=[];saved=[];env={**os.environ,'GIT_OPTIONAL_LOCKS':'0','GIT_NO_LAZY_FETCH':'1','GIT_NO_REPLACE_OBJECTS':'1','GIT_TERMINAL_PROMPT':'0'}
def command(args):
 argv=['git','--no-optional-locks','-c','core.fsmonitor=false','-C',str(repo)]+args;run=subprocess.run(argv,capture_output=True,timeout=15,env=env);record={'command':argv,'exit_code':run.returncode,'stdout_sha256':sha(run.stdout),'stdout_bytes':len(run.stdout),'stderr':run.stderr.decode('utf-8',errors='replace')};commands.append(record)
 if run.returncode:raise ValueError('READONLY_GIT_COMMAND_FAILED_NO_RETRY')
 return run.stdout
def object_bytes(kind,oid):
 raw=command(['cat-file',kind,oid]);actual=hashlib.sha1(kind.encode()+b' '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
 if actual!=oid:raise ValueError('GIT_OBJECT_HASH_MISMATCH')
 path=objects/(kind+'-'+oid+'.bin');path.write_bytes(raw);os.chmod(path,0o600);saved.append({'path':str(path.relative_to(ROOT)),'kind':kind,'git_oid':oid,'sha256':sha(raw),'bytes':len(raw)});return raw
def tree_entries(raw):
 entries=[];offset=0
 while offset<len(raw):
  space=raw.index(b' ',offset);nul=raw.index(b'\0',space+1);mode=raw[offset:space].decode('ascii');name=raw[space+1:nul];end=nul+21
  if end>len(raw) or not name or b'/' in name or name in (b'.',b'..'):raise ValueError('MALFORMED_TREE_ENTRY')
  entries.append({'mode':mode,'name':name,'oid':raw[nul+1:end].hex()});offset=end
 if len({x['name'] for x in entries})!=len(entries):raise ValueError('DUPLICATE_TREE_ENTRY')
 return entries
out={'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':sha(protocol.read_bytes()),'repository':p['repository'],'repository_path':str(repo),'pin':p['pin'],'selected_path':p['selected_path'],'commands':commands,'path_links':links,'saved_objects':saved,'status':'RUNNING','model_calls':0,'production_changes':0,'training_approval':False}
try:
 before={'head':command(['rev-parse','HEAD']).decode().strip(),'status':command(['status','--porcelain=v1','--untracked-files=normal']).decode()};fmt=command(['rev-parse','--show-object-format']).decode().strip();assert fmt=='sha1';commit=object_bytes('commit',p['pin']);line=commit.split(b'\n',1)[0];assert line.startswith(b'tree ');tree=line[5:].decode('ascii');out['root_tree_oid']=tree;parts=p['selected_path'].split('/')
 for i,part in enumerate(parts):
  raw=object_bytes('tree',tree);entries=tree_entries(raw);found=[e for e in entries if e['name']==part.encode()]
  if len(found)!=1:raise ValueError('SELECTED_PATH_MISSING_OR_AMBIGUOUS')
  e=found[0];links.append({'tree_oid':tree,'path_prefix':'/'.join(parts[:i+1]),'entry_name':part,'entry_mode':e['mode'],'entry_oid':e['oid'],'tree_entry_count':len(entries)})
  if i<len(parts)-1:
   if e['mode']!='40000':raise ValueError('NON_TREE_PATH_COMPONENT')
   tree=e['oid']
  else:
   if e['mode'] not in ['100644','100755']:raise ValueError('SELECTED_LEAF_NOT_REGULAR_BLOB')
   blob=object_bytes('blob',e['oid']);assert sha(blob)==p['known_source_sha256'];out['leaf_blob_oid']=e['oid'];out['leaf_sha256']=sha(blob)
 known=ROOT/'agent/research/final-intensive-20261121/go-image-animation-source-context-v1/backend/internal/infrastructure/imaging/limits.go';assert known.read_bytes()==blob
 after={'head':command(['rev-parse','HEAD']).decode().strip(),'status':command(['status','--porcelain=v1','--untracked-files=normal']).decode()};assert before==after;out.update(status='PASS_POSITIVE_PINNED_TREE_MEMBERSHIP_ONLY',before=before,after=after,selected_reviewed_source_bytes_match=True,original_repository_state_unchanged=True,global_scope_complete_proved=False,automatic_REMOVE_allowed=False,lifecycle_action='INCONCLUSIVE_WITH_POSITIVE_SOURCE_MEMBERSHIP_WITNESS',scope='Git commit/tree/path/blob membership independently acquired from fixed local public objects. Not global declaration enumeration,whole-repository semantics,retirement proof,automaticMODIFY,modelgain or production integration.')
except Exception as e:out.update(status='FAILED_PRESERVED_NO_RETRY',exception_type=type(e).__name__,exception=str(e));raise
finally:
 out['finished']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with (P/'pinned-tree-positive-witness-results-v1.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
 print(json.dumps({k:v for k,v in out.items() if k not in ['commands','saved_objects','path_links','before','after']},ensure_ascii=False))
