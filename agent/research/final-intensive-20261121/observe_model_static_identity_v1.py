"""Read-only local artifact identity; never loads a model."""
from pathlib import Path
import hashlib,json,datetime,struct,time
P=Path(__file__).resolve().parent
root=P.parents[2]; protocol=json.loads((P/'model-static-identity-protocol-v1.json').read_text()); manifest=root/protocol['manifest']; blobs=root/'ollama/models/blobs'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(manifest.read_bytes())==protocol['manifest_sha256']
rows=[];seen=set();started=time.monotonic()
def inspect(entry):
 digest=entry['digest'];kind=entry['mediaType']
 if digest in seen:return
 seen.add(digest)
 assert digest.startswith('sha256:') and len(digest)==71
 path=blobs/digest.replace(':','-');row={'path':str(path.relative_to(root)),'media_type':kind,'declared_digest':digest,'declared_size':entry['size']}
 if not path.is_file():row['status']='MISSING';rows.append(row);return
 st=path.stat();hasher=hashlib.sha256()
 with path.open('rb') as f:
  while chunk:=f.read(8*1024*1024):hasher.update(chunk)
 row.update(actual_size=st.st_size,actual_sha256=hasher.hexdigest(),status='PASS' if st.st_size==entry['size'] and hasher.hexdigest()==digest[7:] else 'MISMATCH')
 rows.append(row)
 if row['status']!='PASS':return
 if kind=='application/vnd.ollama.image.model':
  with path.open('rb') as f:header=f.read(24)
  row['header_hex']=header.hex()
  if header[:4]==b'GGUF':row['gguf_header']={'version':struct.unpack('<I',header[4:8])[0],'tensor_count':struct.unpack('<Q',header[8:16])[0],'metadata_count':struct.unpack('<Q',header[16:24])[0]}
 elif st.st_size<65536 and (kind.endswith('+json') or kind.endswith('.params')):
  try:obj=json.loads(path.read_text());row['json']=obj
  except (ValueError,UnicodeError):return
  if isinstance(obj,dict):
   for edge in [obj.get('config'),*obj.get('layers',[])]:
    if edge:inspect(edge)
obj=json.loads(manifest.read_text())
for edge in [obj['config'],*obj['layers']]:inspect(edge)
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':sha((P/'model-static-identity-protocol-v1.json').read_bytes()),'manifest_sha256':sha(manifest.read_bytes()),'rows':rows,'duration_seconds':time.monotonic()-started,'status':'STATIC_LOCAL_IDENTITY_CONSISTENT' if all(r['status']=='PASS' for r in rows) else 'STATIC_LOCAL_IDENTITY_INCOMPLETE','running_server_identity':'UNVERIFIED','trainable_base':'UNVERIFIED','new_model_calls':0,'optimizer_updates':0,'weights_modified':False}
with (P/'model-static-identity-results-v1.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result))
