"""Read-only metadata correspondence; no framework imports or tensor payload reads."""
import json,hashlib,re,collections,datetime
from pathlib import Path
root=Path(__file__).resolve().parents[3]
p=root/'agent/research/final-intensive-20261121'
a=root/'agent/research/acceptance-calibration-20261121'
def load(x):return json.loads(x.read_text())
def evidence(x):return {'path':str(x.relative_to(root)),'sha256':hashlib.sha256(x.read_bytes()).hexdigest()}
d=load(p/'gguf-tensor-directory-results-v1.json')
i=load(a/'native-candidate-metadata-v1/model.safetensors.index.json')
c=load(a/'native-candidate-metadata-v1/config.json')
rows=[]
for t in d['records']:
 m=re.fullmatch(r'blk\.(\d+)\.attn_([qv])\.weight',t['name'])
 if not m:continue
 layer,kind=m.groups();stem=f'model.layers.{layer}.self_attn.{kind}_proj'
 keys=[stem+'.'+s for s in ('weight','scales','biases')]
 assert all(k in i['weight_map'] for k in keys)
 dims=t['dimensions_GGUF_order'];assert len(dims)==2
 rows.append({'gguf_name':t['name'],'dimensions_GGUF_order':dims,'ggml_type':t['ggml_type_name'],'candidate_index_keys':keys,'conditional_rank4_coefficient_count':4*sum(dims)})
assert len(rows)==56 and len({r['gguf_name'] for r in rows})==56
allkeys=[k for k in i['weight_map'] if re.fullmatch(r'model.layers.\d+.self_attn.[qv]_proj.(weight|scales|biases)',k)]
assert len(allkeys)==168
src=a/'native-release-source-v1/mlx_lm/tuner/lora.py'
text=src.read_text();assert 'shape=(input_dims, r)' in text and 'shape=(r, output_dims)' in text
n=sum(r['conditional_rank4_coefficient_count'] for r in rows)
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'METADATA_CORRESPONDENCE_ONLY_NOT_PILOT_ACCEPTANCE','inputs':[evidence(x) for x in (p/'gguf-tensor-directory-results-v1.json',a/'native-candidate-metadata-v1/model.safetensors.index.json',a/'native-candidate-metadata-v1/config.json',src)],'records':rows,'qv_projection_name_pairs':len(rows),'candidate_qv_index_arrays':len(allkeys),'candidate_total_index_arrays':len(i['weight_map']),'qv_ggml_type_counts':dict(collections.Counter(r['ggml_type'] for r in rows)),'candidate_quantization_config':c.get('quantization',c.get('quantization_config')),'rank4_conditional_coefficient_count':n,'rank4_conditional_AB_matrix_count':112,'hypothetical_fp32_coeff_gradient_two_moment_bytes':n*4*4,'conditional_formula':'sum_over_56_projections rank*(input_dimensions+output_dimensions); source shapes A=(input_dims,r), B=(r,output_dims)','actual_adapters_created':0,'actual_optimizer_states_created':0,'tensor_payload_bytes_read':0,'model_generation_calls':0,'limitations':['Index keys are not loaded module inventory or shape/dtype verification.','Quantization scales/biases are auxiliary arrays, not 168 projection modules or evidence of trainable bias.','GGUF mixed Q4_K/Q6_K and candidate 4-bit metadata do not prove numerically equivalent bases.','Conditional byte arithmetic excludes frozen weights, activations, temporary buffers and framework overhead; it is not peak RAM or capacity evidence.','Adapter baseline comparison requires the same actual trainable base and matched tokenization/rendering.','All nine fine-tuning gates remain NO_GO; no training or pilot authorized by this estimate.']}
assert n==1146880
(p/'qv-adapter-metadata-correspondence-review-v1.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ('records','inputs','limitations')},indent=2))
