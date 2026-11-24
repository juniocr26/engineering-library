import urllib.request,json,hashlib,datetime
base="http://ollama:11434"
tags=json.load(urllib.request.urlopen(base+"/api/tags",timeout=10))
expected="a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72"
known=[r for r in tags.get("models",[]) if r.get("name")=="llama3.2:3b"]
assert len(known)==1 and known[0].get("digest")==expected,"expected model identity unavailable"
request=urllib.request.Request(base+"/api/show",data=json.dumps({"name":"llama3.2:3b","verbose":False}).encode(),headers={"Content-Type":"application/json"},method="POST")
with urllib.request.urlopen(request,timeout=20) as response: raw=response.read(8388609)
assert len(raw)<=8388608,"metadata response exceeds bound"
show=json.loads(raw); info=show.get("model_info",{})
keys=["general.architecture","general.parameter_count","general.file_type","general.quantization_version","llama.block_count","llama.embedding_length","llama.feed_forward_length","llama.context_length","llama.attention.head_count","llama.attention.head_count_kv","llama.attention.key_length","llama.attention.value_length","llama.rope.dimension_count","tokenizer.ggml.model","tokenizer.ggml.bos_token_id","tokenizer.ggml.eos_token_id","tokenizer.ggml.padding_token_id","tokenizer.ggml.add_bos_token"]
filtered={k:info[k] for k in keys if k in info}
assert all(isinstance(v,(str,int,float,bool)) for v in filtered.values())
print(json.dumps({"at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"model":"llama3.2:3b","digest":expected,"tag_size_bytes":known[0].get("size"),"details":{k:show.get("details",{}).get(k) for k in ["format","family","parameter_size","quantization_level"]},"metadata":filtered,"missing_keys":[k for k in keys if k not in info],"show_wire_sha256":hashlib.sha256(raw).hexdigest(),"show_wire_bytes":len(raw),"template_system_token_arrays_excluded":True,"inference_or_training":False}))
