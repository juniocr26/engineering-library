"""Source-derived conditional integer arithmetic only; no framework code, tensors or optimizer."""
import ast,datetime,hashlib,json,textwrap
from pathlib import Path
P=Path(__file__).resolve().parent;protocol=json.loads((P/'lora-target-shape-protocol-v1.json').read_text());lm=P/'new-public-sources-v1/ml-explore--mlx-lm'/protocol['mlx_lm_revision'];mlx=P/'new-public-sources-v1/ml-explore--mlx'/protocol['mlx_reference_revision'];cfgpath=P/protocol['model_config'];assert hashlib.sha256(cfgpath.read_bytes()).hexdigest()==protocol['model_config_sha256'];cfg=json.loads(cfgpath.read_text());rank=protocol['rank'];assert all(type(cfg[k])is int and cfg[k]>0 for k in ['hidden_size','num_hidden_layers','intermediate_size','num_attention_heads','num_key_value_heads','vocab_size','head_dim'])and type(rank)is int and rank>0
units={}
def source_unit(id,file,selector):
 raw=file.read_bytes();text=raw.decode();tree=ast.parse(text);nodes=tree.body
 for name in selector.split('.'):
  choices=[n for n in nodes if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name==name];assert len(choices)==1;node=choices[0];nodes=node.body
 first=min([node.lineno]+[d.lineno for d in node.decorator_list]);quote='\n'.join(text.splitlines()[first-1:node.end_lineno]);units[id]={'path':str(file.relative_to(P)),'source_sha256':hashlib.sha256(raw).hexdigest(),'first_line':first,'last_line':node.end_lineno,'quote':quote,'quote_sha256':hashlib.sha256(quote.encode()).hexdigest(),'selector':selector,'source_executed':False};return node
selector=source_unit('selection',lm/'mlx_lm/tuner/utils.py','linear_to_lora_layers')
for id,name in [('linear-from-base','LoRALinear.from_base'),('linear-init','LoRALinear.__init__'),('linear-call','LoRALinear.__call__'),('embedding-init','LoRAEmbedding.__init__'),('embedding-from-base','LoRAEmbedding.from_base')]:source_unit(id,lm/'mlx_lm/tuner/lora.py',name)
attention=source_unit('attention-init',lm/'mlx_lm/models/llama/layers.py','Attention.__init__');mlp=source_unit('mlp-init',lm/'mlx_lm/models/llama/layers.py','MLP.__init__');source_unit('block-init',lm/'mlx_lm/models/llama/layers.py','TransformerBlock.__init__');source_unit('model-args',lm/'mlx_lm/models/llama/config.py','ModelArgs');source_unit('inner-model-init',lm/'mlx_lm/models/llama/model.py','LlamaModel.__init__');source_unit('outer-model-init',lm/'mlx_lm/models/llama/model.py','Model.__init__');source_unit('model-layers',lm/'mlx_lm/models/llama/model.py','Model.layers')
for name in ['named_modules','apply_to_modules','children','freeze','trainable_parameters','__getattr__','__setattr__']:source_unit('Module.'+name,mlx/'python/mlx/nn/layers/base.py','Module.'+name)
source_unit('tree_flatten',mlx/'python/mlx/utils.py','tree_flatten')
for file,name in [(mlx/'python/mlx/nn/layers/base.py','Module'),(mlx/'python/mlx/nn/layers/linear.py','Linear'),(mlx/'python/mlx/nn/layers/quantized.py','QuantizedLinear'),(mlx/'python/mlx/nn/layers/quantized.py','QuantizedEmbedding')]:
 tree=ast.parse(file.read_text());node=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name==name);assert not any(isinstance(n,ast.FunctionDef)and n.name=='to_lora'for n in node.body)
# Interpret only side-effect-free integer dimension expressions; never eval/exec or call source constructors.
def number(node,env):
 if isinstance(node,ast.Constant)and type(node.value)in [int,type(None)]:return node.value
 if isinstance(node,ast.Name)and node.id in env:return env[node.id]
 if isinstance(node,ast.Attribute)and isinstance(node.value,ast.Name)and node.value.id=='args':return cfg.get(node.attr)
 if isinstance(node,ast.BoolOp)and isinstance(node.op,ast.Or):
  for value in node.values:
   result=number(value,env)
   if result:return result
  return result
 if isinstance(node,ast.BinOp)and isinstance(node.op,(ast.Mult,ast.FloorDiv)):
  a,b=number(node.left,env),number(node.right,env);assert type(a)is int and type(b)is int;return a*b if isinstance(node.op,ast.Mult)else a//b
 raise ValueError('dimension expression outside explicit integer profile: '+ast.dump(node))
projections={}
for prefix,node in [('self_attn',attention),('mlp',mlp)]:
 env={}
 for statement in node.body:
  if not isinstance(statement,ast.Assign):continue
  call=statement.value
  if isinstance(call,ast.Call)and isinstance(call.func,ast.Attribute)and isinstance(call.func.value,ast.Name)and call.func.value.id=='nn'and call.func.attr=='Linear':
   assert len(statement.targets)==1 and isinstance(statement.targets[0],ast.Attribute);name=prefix+'.'+statement.targets[0].attr;dims=[number(a,env)for a in call.args];assert len(dims)==2 and all(type(n)is int and n>0 for n in dims);projections[name]={'kind':'linear','input_dims':dims[0],'output_dims':dims[1],'source_call':ast.unparse(call),'source_line':statement.lineno}
  elif any(isinstance(target,ast.Name)for target in statement.targets):
   # Only local dimension bindings are admitted; unrelated field initialization is not interpreted.
   value=number(statement.value,env)
   for target in statement.targets:
    if isinstance(target,ast.Name):env[target.id]=value
assert set(projections)=={'self_attn.q_proj','self_attn.k_proj','self_attn.v_proj','self_attn.o_proj','mlp.gate_proj','mlp.down_proj','mlp.up_proj'}
layers=cfg['num_hidden_layers'];root_modules={}
for i in range(layers):
 for key,shape in projections.items():root_modules['model.layers.'+str(i)+'.'+key]={**shape,'layer_index':i}
root_modules['model.embed_tokens']={'kind':'embedding','num_embeddings':cfg['vocab_size'],'dims':cfg['hidden_size'],'layer_index':None}
def elements(shape):return rank*(shape['input_dims']+shape['output_dims'])if shape['kind']=='linear'else rank*(shape['num_embeddings']+shape['dims'])
rows=[]
for case in protocol['cases']:
 indices=list(range(layers))[-max(case['num_layers'],0):];keys=set(projections)if case['explicit_keys']is None else set(case['explicit_keys']);selected={}
 for i in indices:
  for key in projections:
   if key in keys:name='model.layers.'+str(i)+'.'+key;selected[name]={**root_modules[name],'selection_stage':'layer-relative'}
 for name,shape in root_modules.items():
  if name in keys:
   assert name not in selected,'Overlapping relative/global keys require a separate conversion analysis; not silently counted twice'
   selected[name]={**shape,'selection_stage':'whole-model'}
 total=sum(elements(shape)for shape in selected.values());outside=any(shape['selection_stage']=='whole-model'and(shape['layer_index']is None or shape['layer_index']not in indices)for shape in selected.values());checks={'module_count':len(selected)==case['expected_modules'],'adapter_elements':total==case['expected_adapter_elements'],'global_outside':outside==case['expected_global_outside_layer_selection']};rows.append({'id':case['id'],'selected_layer_indices':indices,'selected_modules':{name:{**shape,'adapter_elements':elements(shape)}for name,shape in selected.items()},'module_count':len(selected),'adapter_elements':total,'global_outside_layer_selection':outside,'hypothetical_adapter_bytes_if_2byte_elements':total*2,'hypothetical_adapter_bytes_if_4byte_elements':total*4,'illustrative_four_equal_fp32_buffers_bytes_not_optimizer_measurement':total*4*4,'checks':checks,'pass':all(checks.values())})
# Verify the exact written field multiplier and shape tuple forms without executing those functions.
linear_init=ast.parse(textwrap.dedent(units['linear-init']['quote'])).body[0];scale_field=next(n for n in ast.walk(linear_init)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Attribute)and ast.unparse(t)=='self.scale'for t in n.targets));assert isinstance(scale_field.value,ast.Name)and scale_field.value.id=='scale';assert 'shape=(input_dims, r)'in units['linear-init']['quote']and'shape=(r, output_dims)'in units['linear-init']['quote'];assert'self.scale * z'in units['linear-call']['quote']
r={'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'initial_driver_correction':'Dedent a parsing view of an indented complete method;physical quote bytes are unchanged.','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'SOURCE_DERIVED_CONDITIONAL_ARITHMETIC_NOT_TRAINING_FEASIBILITY','protocol_sha256':hashlib.sha256((P/'lora-target-shape-protocol-v1.json').read_bytes()).hexdigest(),'source_units':units,'model_metadata':{k:cfg[k]for k in ['model_type','hidden_size','num_hidden_layers','intermediate_size','num_attention_heads','num_key_value_heads','head_dim','vocab_size','tie_word_embeddings','quantization']},'projections':projections,'rows':rows,'passes':sum(r['pass']for r in rows),'cases':len(rows),'proposed_rank':rank,'source_direct_scale_multiplier':protocol['scale'],'scale_divided_by_rank_in_selected_call':False,'scale_local_rebinding_note':'self.scale is assigned from the supplied parameter before local scale is rebound for random initializer bounds;do not confuse those roles.','important_findings':['Default omittedkeys select all7supported projection paths per reviewed Llama block,not assumedq/vonly.','Zero num_layers uses[-0:]and symbolically selects all28blocks;negativevalues also reachall bymax clamp.','Explicit fullmodel keys can target embedding or earlierlayer outside the last-two-block selection.','LoRALinear.from_base constructs a new linear module before replacing it with the base linear. Finaladapter counts do not establish transientallocation/MLXlazyexecution peak memory.','Minimum-version reference classes lack to_lora definitions in the reviewed source/base chain;custom/newerframework hooks remain outside scope.'],'source_conditions':protocol['source_conditions'],'nn_modules_or_tensors_instantiated':False,'upstream_source_bytecode_generated_or_executed':False,'source_parsed_to_AST_only':True,'owned_whitelisted_integer_AST_interpreter_used':True,'framework_imported_or_installed':False,'weights_or_tokenizer_loaded':False,'optimizer_state_or_memory_measured':False,'hardware_feasibility_proved':False,'training_steps':0,'owner_approved':False,'training_gold':False,'launch_allowed':False,'readiness':'NO-GO_UNCHANGED','limits':protocol['memory_output_scope']}
with(P/'lora-target-shape-audit-v1.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'symbolic_cases':len(rows),'passes':r['passes'],'default_two_layers_elements':rows[0]['adapter_elements'],'explicit_qv_elements':rows[1]['adapter_elements'],'source_units':len(units),'training_steps':0,'memory_measured':False})
