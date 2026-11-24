"""Read a bounded GGUF v3 tensor directory only, never its tensor payload or model runtime."""
from pathlib import Path
import collections,datetime,hashlib,json,math,struct
from consume_gguf_metadata_prefix_v1 import decode
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sha=lambda b:hashlib.sha256(b).hexdigest();observation=json.loads((P/'gguf-tokenizer-metadata-observation-v1.json').read_text());path=ROOT/observation['source_path'];prefix=(P/'gguf-tokenizer-metadata-prefix-v1.bin').read_bytes();assert sha(prefix)==observation['metadata_prefix_sha256'];metadata,count=decode(prefix);alignment=metadata.get('general.alignment',32);assert isinstance(alignment,int) and alignment>=8 and alignment%8==0;assert count<=10000
protocol={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hypothesis':'The global Q4_K_M/file-type label does not establish all per-tensor types or equality with an MLX4bit candidate. Directory names/dimensions/types can improve a conditional Q/V proposal without loading weights.','source_path':str(path.relative_to(ROOT)),'source_full_digest_previously_verified':observation['source_digest_previously_stream_verified'],'metadata_prefix_sha256':sha(prefix),'tensor_count':count,'alignment':alignment,'max_directory_bytes':1048576,'specification':'GGUFv3 tensor info sequence/name<=64bytes, dimensions<=4, rawggmltype, relativeoffset; primary reference snapshot retained.','scope':'Metadata-only directory observation; no tensor bytes, model/tokenizer inference, trainable arrays, adapter or optimizer.'}
with (P/'gguf-tensor-directory-protocol-v1.json').open('x') as f:json.dump(protocol,f,indent=2);f.write('\n')
rows=[];before=path.stat();start=len(prefix)
with path.open('rb') as stream:
 assert stream.read(start)==prefix
 def read(n):
  assert 0<=n<=1048576 and stream.tell()+n-start<=1048576
  b=stream.read(n);assert len(b)==n;return b
 def u32():return struct.unpack('<I',read(4))[0]
 def u64():return struct.unpack('<Q',read(8))[0]
 seen=set()
 for _ in range(count):
  row_start=stream.tell();length=u64();assert 0<length<=64;name=read(length).decode('utf-8');assert name not in seen;seen.add(name);dimensions=u32();assert 1<=dimensions<=4;shape=[u64() for _ in range(dimensions)];assert all(n>0 for n in shape);kind=u32();offset=u64();assert offset%alignment==0
  rows.append({'name':name,'dimensions_GGUF_order':shape,'ggml_type_code':kind,'ggml_type_name':{0:'F32',1:'F16',12:'Q4_K',13:'Q5_K',14:'Q6_K',15:'Q8_K'}.get(kind,'UNDECODED_'+str(kind)),'tensor_data_relative_offset':offset,'directory_record_start':row_start,'directory_record_end':stream.tell(),'logical_element_count':math.prod(shape)})
 end=stream.tell();stream.seek(start);directory=read(end-start)
after=path.stat();assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns);data_start=end+(-end)%alignment;assert all(data_start+r['tensor_data_relative_offset']<before.st_size for r in rows)
with (P/'gguf-tensor-directory-v1.bin').open('xb') as f:f.write(directory)
qv=[r for r in rows if r['name'].endswith(('.attn_q.weight','.attn_v.weight'))];types=dict(collections.Counter(r['ggml_type_name'] for r in rows));qvtypes=dict(collections.Counter(r['ggml_type_name'] for r in qv));result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':sha((P/'gguf-tensor-directory-protocol-v1.json').read_bytes()),'source_path':str(path.relative_to(ROOT)),'source_file_size':before.st_size,'source_stat_stable':True,'current_full_weight_rehash':False,'metadata_prefix_bytes_read':start,'tensor_directory_bytes_read':len(directory),'tensor_directory_sha256':sha(directory),'tensor_directory_end':end,'tensor_data_start_computed_not_read':data_start,'tensor_payload_bytes_read':0,'model_loaded':False,'records':rows,'tensor_type_counts':types,'qv_tensor_count':len(qv),'qv_type_counts':qvtypes,'logical_elements_sum_not_unique_trainable_parameters':sum(r['logical_element_count'] for r in rows),'global_file_type_code':metadata.get('general.file_type'),'global_file_type_is_not_tensor_type_enum':True,'new_model_calls':0,'optimizer_updates':0,'training_ready':False}
with (P/'gguf-tensor-directory-results-v1.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['records']}));print(json.dumps(qv[:4]))
