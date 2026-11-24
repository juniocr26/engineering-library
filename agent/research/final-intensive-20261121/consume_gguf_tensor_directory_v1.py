"""Recover tensor-directory metadata using retained bounded bytes, without model access."""
import argparse,hashlib,json,math,struct
from pathlib import Path
from consume_gguf_metadata_prefix_v1 import decode
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);args=ap.parse_args();p=args.root/'agent/research/final-intensive-20261121'
expected=json.loads((p/'gguf-tensor-directory-results-v1.json').read_text());prefix=(p/'gguf-tokenizer-metadata-prefix-v1.bin').read_bytes();meta,count=decode(prefix)
raw=(p/'gguf-tensor-directory-v1.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==expected['tensor_directory_sha256'];position=0
rows=[]
def take(n):
 global position
 assert 0<=n<=len(raw)-position
 value=raw[position:position+n];position+=n;return value
def u64():return struct.unpack('<Q',take(8))[0]
def u32():return struct.unpack('<I',take(4))[0]
for _ in range(count):
 start=position+len(prefix);n=u64();assert 0<n<=64;name=take(n).decode();rank=u32();assert 1<=rank<=4;shape=[u64() for _ in range(rank)];kind=u32();offset=u64()
 rows.append(dict(name=name,dimensions_GGUF_order=shape,ggml_type_code=kind,ggml_type_name={0:'F32',1:'F16',12:'Q4_K',13:'Q5_K',14:'Q6_K',15:'Q8_K'}.get(kind,'UNDECODED_'+str(kind)),tensor_data_relative_offset=offset,directory_record_start=start,directory_record_end=position+len(prefix),logical_element_count=math.prod(shape)))
assert position==len(raw) and rows==expected['records']
alignment=meta.get('general.alignment',32);end=len(prefix)+position;assert end+(-end)%alignment==expected['tensor_data_start_computed_not_read']
review=json.loads((p/'qv-adapter-metadata-correspondence-review-v1.json').read_text())
for item in review['inputs']:
 assert hashlib.sha256((args.root/item['path']).read_bytes()).hexdigest()==item['sha256']
assert sum(4*sum(r['dimensions_GGUF_order']) for r in rows if r['name'].endswith(('.attn_q.weight','.attn_v.weight')))==review['rank4_conditional_coefficient_count']
print(json.dumps({'status':'PASS_RETAINED_DIRECTORY_AND_BOUND_CORRESPONDENCE','records':len(rows),'original_model_opened':False,'tensor_payload_bytes_read':0,'training':False}))
