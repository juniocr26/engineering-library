"""Read bounded GGUF metadata only; no tensor allocation, model loading or tokenization."""
from pathlib import Path
import struct,json,hashlib,datetime
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sha=lambda b:hashlib.sha256(b).hexdigest()
identity=json.loads((P/'model-static-identity-results-v1.json').read_text());row=next(r for r in identity['rows'] if r['media_type']=='application/vnd.ollama.image.model');path=ROOT/row['path'];assert path.stat().st_size==row['actual_size'];limit=32*1024*1024
scalars={0:('<B',1),1:('<b',1),2:('<H',2),3:('<h',2),4:('<I',4),5:('<i',4),6:('<f',4),7:('<?',1),10:('<Q',8),11:('<q',8),12:('<d',8)}
with path.open('rb') as stream:
 def read(n):
  assert 0<=n<=limit and stream.tell()+n<=limit,'metadata read exceeds frozen bound';b=stream.read(n);assert len(b)==n;return b
 def scalar(kind):
  fmt,size=scalars[kind];return struct.unpack(fmt,read(size))[0]
 def string():
  n=scalar(10);return read(n).decode('utf-8')
 def value(kind):
  if kind==8:return string()
  if kind in scalars:return scalar(kind)
  assert kind==9,kind
  inner=scalar(4);count=scalar(10);assert count<=2000000
  assert inner!=9,'nested arrays not supported by this bounded observer'
  return [value(inner) for _ in range(count)]
 assert read(4)==b'GGUF';version=scalar(4);assert version==3;tensors=scalar(10);count=scalar(10);assert count<=1000
 metadata={}
 for _ in range(count):
  key=string();assert key not in metadata;kind=scalar(4);metadata[key]=value(kind)
 end=stream.tell();stream.seek(0);raw=read(end)
vocab=metadata.get('tokenizer.ggml.tokens',[]);specials={k:v for k,v in metadata.items() if k.startswith('tokenizer.') and (k.endswith('_token_id') or k.endswith('add_bos_token') or k.endswith('add_eos_token'))}
summary={}
for k,v in metadata.items():
 if isinstance(v,list):
  encoded=json.dumps(v,ensure_ascii=False,separators=(',',':')).encode();summary[k]={'array_count':len(v),'normalized_json_sha256':sha(encoded),'full_array_exported':False}
 else:summary[k]=v
special_text={k:{'id':v,'vocabulary_text':vocab[v] if isinstance(v,int) and 0<=v<len(vocab) else None} for k,v in specials.items() if k.endswith('_token_id')}
markers=['<|begin_of_text|>','<|end_of_text|>','<|start_header_id|>','<|end_header_id|>','<|eot_id|>','<|eom_id|>','<|finetune_right_pad_id|>','<|python_tag|>'];marker_ids={marker:[i for i,text in enumerate(vocab) if text==marker] for marker in markers}
# Metadata-only extraction explicitly excludes all tensor headers/data.
with (P/'gguf-tokenizer-metadata-prefix-v1.bin').open('xb') as f:f.write(raw)
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_path':row['path'],'source_digest_previously_stream_verified':row['actual_sha256'],'source_current_size':path.stat().st_size,'current_full_weight_rehash':False,'gguf_version':version,'tensor_count_declared_not_read':tensors,'metadata_count':count,'metadata_prefix_bytes':end,'metadata_prefix_sha256':sha(raw),'metadata':summary,'special_token_text':special_text,'selected_marker_ids':marker_ids,'scope':'Static metadata correspondence only; no tokenizer execution, tensor read, chat rendering, token budget measurement or served runtime identity. GGUF vocab metadata does not establish trainable base/tokenizer parity.','new_model_calls':0,'optimizer_updates':0,'weights_modified':False}
with (P/'gguf-tokenizer-metadata-observation-v1.json').open('x') as f:json.dump(result,f,indent=2,ensure_ascii=False);f.write('\n')
print(json.dumps({'metadata_bytes':end,'vocab_count':len(vocab),'specials':special_text,'markers':marker_ids,'tensor_data_read':False}))
