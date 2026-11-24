"""Finite raw Git membership verifier, no repository, model or target execution."""
import hashlib,io

def object_id(kind,raw):return hashlib.sha1(kind.encode()+b' '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def decode_tree(raw):
 stream=io.BytesIO(raw);entries={}
 while stream.tell()<len(raw):
  header=bytearray()
  while True:
   ch=stream.read(1)
   if not ch:raise ValueError('TRUNCATED_TREE_HEADER')
   if ch==b'\0':break
   header.extend(ch)
  fields=bytes(header).split(b' ',1)
  if len(fields)!=2:raise ValueError('INVALID_TREE_HEADER')
  mode,name=fields;oid=stream.read(20)
  if len(oid)!=20 or not name or b'/' in name or name in (b'.',b'..') or name in entries:raise ValueError('INVALID_TREE_ENTRY')
  entries[name]=(mode.decode('ascii'),oid.hex())
 return entries

def verify_membership(commit,path,objects,expected_blob_sha256):
 components=path.split('/')
 if not components or any(x in ('','..','.') for x in components):raise ValueError('UNSAFE_SELECTED_PATH')
 def read(kind,oid):
  raw=objects.get((kind,oid))
  if raw is None:raise ValueError('MISSING_OBJECT')
  if object_id(kind,raw)!=oid:raise ValueError('OBJECT_HASH_MISMATCH')
  return raw
 raw=read('commit',commit);first=raw.partition(b'\n')[0]
 if not first.startswith(b'tree ') or len(first)!=45:raise ValueError('INVALID_COMMIT_TREE_HEADER')
 current=first[5:].decode('ascii');steps=[]
 for index,name in enumerate(components):
  entries=decode_tree(read('tree',current));entry=entries.get(name.encode())
  if entry is None:raise ValueError('PATH_NOT_MEMBER')
  mode,oid=entry;steps.append({'tree_oid':current,'name':name,'mode':mode,'entry_oid':oid})
  if index<len(components)-1:
   if mode!='40000':raise ValueError('NON_TREE_COMPONENT')
   current=oid
  else:
   if mode not in ('100644','100755'):raise ValueError('NONREGULAR_LEAF')
   blob=read('blob',oid);actual=hashlib.sha256(blob).hexdigest()
   if actual!=expected_blob_sha256:raise ValueError('EXPECTED_SOURCE_HASH_MISMATCH')
 return {'commit':commit,'path':path,'blob_oid':oid,'blob_sha256':actual,'path_steps':steps,'verdict':'POSITIVE_SOURCE_MEMBERSHIP_ONLY','global_scope_complete':False,'REMOVE_allowed':False}
