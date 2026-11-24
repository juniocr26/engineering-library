"""Decode an archived metadata-only GGUF prefix; exclude tensors and never load weights."""
from pathlib import Path
import argparse,hashlib,io,json,struct

def decode(raw):
 stream=io.BytesIO(raw)
 types={0:('<B',1),1:('<b',1),2:('<H',2),3:('<h',2),4:('<I',4),5:('<i',4),6:('<f',4),7:('<?',1),10:('<Q',8),11:('<q',8),12:('<d',8)}
 def read(n):
  assert 0<=n<=len(raw);b=stream.read(n);assert len(b)==n;return b
 def scalar(kind):
  fmt,size=types[kind];return struct.unpack(fmt,read(size))[0]
 def string():return read(scalar(10)).decode()
 def value(kind):
  if kind==8:return string()
  if kind in types:return scalar(kind)
  assert kind==9;inner=scalar(4);n=scalar(10);assert inner!=9 and n<=2000000
  return [value(inner) for _ in range(n)]
 assert read(4)==b'GGUF' and scalar(4)==3;tensors=scalar(10);n=scalar(10);assert n<=1000;meta={}
 for _ in range(n):
  k=string();assert k not in meta;meta[k]=value(scalar(4))
 assert stream.tell()==len(raw),'Unexpected tensor header/data or trailing bytes in metadata-only archive'
 return meta,tensors

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args();P=args.root/'agent/research/final-intensive-20261121';obs=json.loads((P/'gguf-tokenizer-metadata-observation-v1.json').read_text());raw=(P/'gguf-tokenizer-metadata-prefix-v1.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==obs['metadata_prefix_sha256'];meta,tensors=decode(raw)
 for key,v in meta.items():
  if isinstance(v,list):assert len(v)==obs['metadata'][key]['array_count'] and hashlib.sha256(json.dumps(v,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()==obs['metadata'][key]['normalized_json_sha256']
  else:assert v==obs['metadata'][key]
 print(json.dumps({'metadata_keys_verified':len(meta),'metadata_bytes':len(raw),'vocab_count':len(meta['tokenizer.ggml.tokens']),'declared_tensor_count_not_read':tensors,'tensor_bytes':0,'tokenizer_executed':False,'model_loaded':False}))
if __name__=='__main__':main()
