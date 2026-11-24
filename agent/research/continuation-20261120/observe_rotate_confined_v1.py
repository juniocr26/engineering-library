"""Execute one exact reviewed public function under a descriptor-only owned facade."""
import ast,datetime,hashlib,json,os,platform,posixpath,re,stat,sys,types
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()

def observe(root_override=None):
 protocol=json.loads((P/'rotate-confined-protocol-v1.json').read_text());source=ROOT/protocol['source_path'];raw=source.read_bytes();assert sha(raw)==protocol['source_sha256'];tree=ast.parse(raw.decode());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==protocol['selector']];assert len(nodes)==1;node=nodes[0]
 quote=''.join(raw.decode().splitlines(keepends=True)[node.lineno-1:node.end_lineno]);assert sha(quote.encode())==protocol['quote_sha256']
 assert node.decorator_list==[]and node.returns is None and len(node.args.args)==1 and node.args.args[0].arg=='filename'and len(node.args.kwonlyargs)==1 and node.args.kwonlyargs[0].arg=='keep'and ast.unparse(node.args.kwonlyargs[0].annotation)=='int'and ast.literal_eval(node.args.kw_defaults[0])==5
 calls=sorted({ast.unparse(n.func)for n in ast.walk(node)if isinstance(n,ast.Call)});assert calls==protocol['written_call_allowlist']
 assert sum(1 for _ in ast.walk(node))<400
 forbidden=(ast.Import,ast.ImportFrom,ast.Global,ast.Nonlocal,ast.ClassDef,ast.AsyncFunctionDef,ast.Lambda,ast.With,ast.AsyncWith,ast.While,ast.Try)
 assert not any(isinstance(n,forbidden)for n in ast.walk(node))and sum(isinstance(n,ast.FunctionDef)for n in ast.walk(node))==1
 allowed_attributes={'os.path','os.path.exists','os.path.isfile','os.path.splitext','os.rename','os.remove','kept_names.append'}
 assert all(ast.unparse(n)in allowed_attributes for n in ast.walk(node)if isinstance(n,ast.Attribute))
 assert all(n.id in {'filename','keep','int','ValueError','os','fn_root','fn_ext','kept_names','i','fns','orig_name','kept_name','reversed','list','zip','range'}for n in ast.walk(node)if isinstance(n,ast.Name))
 code=compile(ast.Module(body=[node],type_ignores=[]),'<exact-reviewed-rotate_file>','exec')
 base=Path(root_override or'/private/tmp/el-boltons-rotate-confined-20261120-macos-v1');base.mkdir(exist_ok=False);rows=[]
 for case in protocol['expected_cases']:
  owned=base/case['id'];owned.mkdir();work=owned/'fs';work.mkdir();filename=case['filename'];keep=case['keep'];assert -1<=keep<=5
  original=('ORIGINAL:'+case['id']+'\n').encode();root,ext=posixpath.splitext(filename)
  def numbered(i):return root+'.'+str(i)+ext if ext else root+'.'+str(i)
  if case.get('original_directory'):(work/filename).mkdir()
  elif not case.get('missing_original'):(work/filename).write_bytes(original)
  for i in range(1,case['existing_slots']+1):(work/numbered(i)).write_bytes(('SLOT:'+str(i)+':'+case['id']+'\n').encode())
  def snapshot():
   result={}
   for f in sorted(work.iterdir()):
    s=f.lstat();assert not stat.S_ISLNK(s.st_mode)
    result[f.name]={'kind':'directory'}if stat.S_ISDIR(s.st_mode)else{'kind':'file','utf8':f.read_text(),'sha256':sha(f.read_bytes())}
   return result
  before=snapshot();(owned/'exact-before.json').write_text(json.dumps(before,indent=2)+'\n');operations=[]
  descriptor=os.open(work,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
  def leaf(name):
   if type(name)is not str or not re.fullmatch(r'[A-Za-z0-9_.-]{1,80}',name)or name in ['.','..']:raise ValueError('facade refuses a non-leaf filename')
   if len(operations)>=64:raise ValueError('facade operation bound exceeded')
   try:
    entry=os.stat(name,dir_fd=descriptor,follow_symlinks=False)
    if stat.S_ISLNK(entry.st_mode):raise ValueError('facade refuses symlink')
   except FileNotFoundError:pass
   return name
  def exists(name):
   name=leaf(name)
   try:os.stat(name,dir_fd=descriptor,follow_symlinks=False);value=True
   except FileNotFoundError:value=False
   operations.append({'call':'exists','path':name,'result':value});return value
  def isfile(name):
   name=leaf(name);value=stat.S_ISREG(os.stat(name,dir_fd=descriptor,follow_symlinks=False).st_mode);operations.append({'call':'isfile','path':name,'result':value});return value
  def splitext(name):
   name=leaf(name);value=posixpath.splitext(name);operations.append({'call':'splitext','path':name,'result':list(value)});return value
  def rename(src,dst):
   src=leaf(src);dst=leaf(dst);os.rename(src,dst,src_dir_fd=descriptor,dst_dir_fd=descriptor);operations.append({'call':'rename','source':src,'destination':dst})
  def remove(name):
   name=leaf(name);os.unlink(name,dir_fd=descriptor);operations.append({'call':'remove','path':name})
  facade=types.SimpleNamespace(path=types.SimpleNamespace(exists=exists,isfile=isfile,splitext=splitext),rename=rename,remove=remove)
  namespace={'__builtins__':{'int':int,'ValueError':ValueError,'range':range,'reversed':reversed,'list':list,'zip':zip},'os':facade}
  error=None;returned=None
  try:
   exec(code,namespace);returned=namespace['rotate_file'](filename,keep=keep)
  except ValueError as exc:error={'type':'ValueError','message':str(exc)}
  finally:os.close(descriptor)
  after=snapshot();mutations=[o for o in operations if o['call']in ['rename','remove']]
  expected=case['expected']
  if expected=='ORIGINAL_MOVED_THEN_REMOVED':matches=after=={}and [o['call']for o in mutations]==['rename','remove']and error is None
  elif expected in ['ONE_ROTATED_SLOT_REMAINS','FOUR_ROTATED_SLOTS_REMAIN']:
   slots = 1 if expected == 'ONE_ROTATED_SLOT_REMAINS' else 4
   matches=set(after)=={numbered(i)for i in range(1,slots+1)}and after[numbered(1)]['utf8']==original.decode()and error is None
  elif expected=='NO_MUTATION':matches=before==after and not mutations and error is None
  else:matches=before==after and not mutations and error is not None and error['type']=='ValueError'
  rows.append({'id':case['id'],'expected':expected,'matches':matches,'before':before,'operations':operations,'after':after,'error':error,'returned':returned,'inspected_function_executed':True,'module_imported':False,'filesystem_confined':True})
 record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'platform':platform.platform(),'python':sys.version,'source_revision':protocol['revision'],'source_sha256':protocol['source_sha256'],'quote_sha256':protocol['quote_sha256'],'selected_public_function_executed':True,'whole_public_module_imported':False,'only_owned_temporary_payloads_mutated':True,'owned_root':str(base),'correct':sum(r['matches']for r in rows),'n':len(rows),'rows':rows,'source_repository_modified':False,'production_or_catalog_modified':False,'model_calls':0,'neural_training':False,'windows_verified':False,'limits':['Historical source and reviewed facade operations only.','The observation establishes these bounded native POSIX traces, not crash atomicity, race safety, Windows behavior or maintainer intent.','All test payload contents before mutation are retained exactly; no real user files are used.']}
 return record
if __name__=='__main__':
 record=observe()
 with(P/'rotate-confined-macos-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
 print(json.dumps({'correct':record['correct'],'n':record['n'],'selected_public_function_executed':True,'only_owned_payloads_mutated':True,'failed':[r['id']for r in record['rows']if not r['matches']]}))
