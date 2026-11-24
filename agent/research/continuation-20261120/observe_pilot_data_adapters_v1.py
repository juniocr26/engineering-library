"""Execute reviewed pure adapters with owned rows/method sinks; never load real data/tokenizers."""
import ast,builtins,copy,datetime,hashlib,json,sys,types,typing
from pathlib import Path
P=Path(__file__).resolve().parent;protocol=json.loads((P/'pilot-data-adapter-protocol-v1.json').read_text());file=P/protocol['source_path'];raw=file.read_bytes();assert hashlib.sha256(raw).hexdigest()==protocol['source_sha256'];text=raw.decode();tree=ast.parse(text);names=set(protocol['selected_classes']+protocol['selected_functions']);nodes=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef))and n.name in names];assert len(nodes)==6
for node in nodes:
 assert not node.decorator_list
 if isinstance(node,ast.ClassDef):assert not node.bases
 for item in ast.walk(node):
  assert not isinstance(item,(ast.Import,ast.ImportFrom,ast.With,ast.AsyncWith,ast.Global,ast.Nonlocal))
  if isinstance(item,ast.Name):assert item.id not in ['open','eval','exec','compile','__import__','Path','json','rprint','load_dataset','load_hf_dataset','load_local_dataset']
  if isinstance(item,ast.Call)and isinstance(item.func,ast.Name):assert item.func.id in ['len','sum','enumerate','getattr','ValueError','TextDataset','ChatDataset','CompletionsDataset']
namespace={'__name__':'owned_selected_pure_data_adapters','__builtins__':{'__build_class__':builtins.__build_class__,'object':object,'len':len,'sum':sum,'enumerate':enumerate,'getattr':getattr,'ValueError':ValueError,'str':str,'int':int},'List':typing.List,'Dict':typing.Dict,'Any':typing.Any,'PreTrainedTokenizer':object};before=set(sys.modules);exec(compile(ast.Module(body=copy.deepcopy(nodes),type_ignores=[]),str(file)+'::selected-pure-adapters','exec'),namespace);create=namespace['create_dataset'];Chat=namespace['ChatDataset'];Cache=namespace['CacheDataset'];Concat=namespace['ConcatenatedDataset']
class OwnedMethodSink:
 eos_token_id=99
 def __init__(self):self.calls=[]
 def encode(self,text):self.calls.append({'method':'encode','text':text});return list(range(11 if'owned-long'in text else3))
 def apply_chat_template(self,messages,tools=None,return_dict=False,add_generation_prompt=False):
  self.calls.append({'method':'apply_chat_template','messages':copy.deepcopy(messages),'tools':tools,'return_dict':return_dict,'add_generation_prompt':add_generation_prompt});return list(range(11 if any('owned-long'in m.get('content','')for m in messages)else3))if messages else[]
class TrackedRow(dict):
 def __init__(self,*a,**kw):super().__init__(*a,**kw);self.reads=[]
 def __getitem__(self,k):self.reads.append(k);return super().__getitem__(k)
 def __contains__(self,k):self.reads.append(k);return super().__contains__(k)
 def get(self,k,default=None):self.reads.append(k);return super().get(k,default)
class OwnedRows:
 def __init__(self,name,rows):self.name=name;self.rows=rows
 def __len__(self):return len(self.rows)
 def __getitem__(self,i):return self.rows[i]
 def process(self,d):return self.name
flags={'owner_approved':False,'training_gold':False,'training_use_approved':False}
def chatrow(long=False):return{'messages':[{'role':'user','content':'owned input'},{'role':'assistant','content':'owned-long'if long else'owned-short'}]}
def cfg(mask=False):return types.SimpleNamespace(mask_prompt=mask)
def error(fn):
 try:fn()
 except Exception as e:return type(e).__name__
 return'NO_ERROR'
observed={};inputs={}
for case,datum in [('chat-unapproved-flags',{**chatrow(),**flags}),('completion-unapproved-flags',{'prompt':'owned input','completion':'owned-short',**flags}),('text-unapproved-flags',{'text':'owned-short',**flags})]:
 row=TrackedRow(datum);sink=OwnedMethodSink();adapter=create([row],sink,cfg());processed=adapter.process(adapter[0]);observed[case]={'adapter':type(adapter).__name__,'processed':isinstance(processed,tuple),'approval_fields_consulted':any(k in flags for k in row.reads),'read_keys':row.reads,'sink_calls':sink.calls};inputs[case]=datum
observed['text-mask-refusal']={'error_type':error(lambda:create([{'text':'owned'}],OwnedMethodSink(),cfg(True)))}
observed['empty-input-format-dispatch']={'error_type':error(lambda:create([],OwnedMethodSink(),cfg()))}
adapter=create([chatrow(),{'text':'owned secondformat'}],OwnedMethodSink(),cfg());observed['mixed-row-formats']={'adapter':type(adapter).__name__,'second_row_error':error(lambda:adapter.process(adapter[1]))}
row={'messages':[{'role':'user','content':'owned first'},{'role':'user','content':'owned last'}]};adapter=create([row],OwnedMethodSink(),cfg(True));result=adapter.process(adapter[0]);observed['last-user-not-refused']={'processed':isinstance(result,tuple),'last_role':row['messages'][-1]['role']}
adapter=create([{'messages':[]}],OwnedMethodSink(),cfg(True));observed['empty-messages-with-mask']={'error_type':error(lambda:adapter.process(adapter[0]))}
row=chatrow();sink=OwnedMethodSink();cache=Cache(Chat([row],sink));first=cache[0];row['messages'][-1]['content']='owned-long';second=cache[0];observed['cache-after-row-change']={'processing_calls':len(sink.calls),'same_cached_object':first is second,'first_length':len(first[0]),'second_length':len(second[0]),'underlying_row_after':row}
rows=[chatrow(True),{**chatrow(),**flags}];sink=OwnedMethodSink();cache=Cache(Chat(rows,sink));itemlens=[cache.itemlen(i)for i in range(2)];before_processing_calls=len(sink.calls);lengths=[len(cache[i][0])for i in range(2)];observed['cache-sort-proxy']={'itemlen_values':itemlens,'processed_lengths':lengths,'source_sort_indices':sorted(range(2),key=cache.itemlen),'token_length_sort_indices':sorted(range(2),key=lambda i:lengths[i]),'processing_calls_before_items':before_processing_calls}
def concatenated():return Concat([OwnedRows('A',[{'id':'A0'},{'id':'A1'}]),OwnedRows('B',[{'id':'B0'},{'id':'B1'},{'id':'B2'}])])
concat=concatenated();observed['concatenated-boundary-index']={'declared_length':len(concat),'index_len_returns':concat[len(concat)]['id']}
concat=concatenated();iterator=iter(concat);ids=[];stopped=False
for _ in range(9):
 try:ids.append(next(iterator)['id'])
 except StopIteration:stopped=True;break
observed['concatenated-sequence-iteration']={'declared_length':len(concat),'iterated_length':len(ids),'ids':ids,'stop_seen_within9':stopped}
shared={'text':'owned shared'};concat=Concat([OwnedRows('A',[shared]),OwnedRows('B',[shared])]);held=concat[0];initial=concat.process(held);other=concat[1];observed['concatenated-shared-row-routing']={'same_row_object':held is other,'initial_origin':initial,'held_origin_after_other_access':concat.process(held)}
row={'id':'owned'};concat=Concat([OwnedRows('A',[row])]);has='_dataset'in row;returned=concat[0];observed['concatenated-metadata-mutation']={'before_has_dataset_key':has,'after_dataset_index':row['_dataset'],'returned_is_original':returned is row}
results=[]
for case in protocol['cases']:
 actual=observed[case['id']];checks={k:type(actual.get(k))is type(v)and actual.get(k)==v for k,v in case['expected_fields'].items()};results.append({'id':case['id'],'observed':actual,'expected_fields':case['expected_fields'],'checks':checks,'pass':all(checks.values())})
new=set(sys.modules)-before;assert not any(name.split('.')[0]in ['mlx','mlx_lm','transformers','numpy','yaml']for name in new)
spans=[]
for node in nodes:
 quote='\n'.join(text.splitlines()[node.lineno-1:node.end_lineno]);spans.append({'name':node.name,'first_line':node.lineno,'last_line':node.end_lineno,'quote':quote,'quote_sha256':hashlib.sha256(quote.encode()).hexdigest(),'source_sha256':protocol['source_sha256']})
trainer=P/'training-primary-sources-v1/mlx-lm--mlx_lm--tuner--trainer.py';ts=trainer.read_text();tt=ast.parse(ts);fn=next(n for n in tt.body if isinstance(n,ast.FunctionDef)and n.name=='iterate_batches');sort_branch=fn.body[0];assert isinstance(sort_branch,ast.If)and'CacheDataset'in ast.unparse(sort_branch.test)and'dataset.itemlen(idx)'in ast.unparse(sort_branch)
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'SELECTED_PURE_DATA_ADAPTER_BOUNDARIES_OBSERVED','source_sha256':protocol['source_sha256'],'git_blob':protocol['git_blob'],'source_spans':spans,'rows':results,'passes':sum(row['pass']for row in results),'cases':len(results),'owned_unapproved_native_shape_inputs':inputs,'trainer_sort_branch_source_only':{'first_line':sort_branch.lineno,'last_line':sort_branch.end_lineno,'quote':ast.get_source_segment(ts,sort_branch),'source_sha256':hashlib.sha256(trainer.read_bytes()).hexdigest(),'trainer_executed':False},'selected_pure_adapter_classes_and_create_function_executed':True,'upstream_module_imported':False,'real_tokenizer_or_template_loaded':False,'owned_method_sink_only':True,'MLX_Transformers_NumPy_YAML_imported':False,'model_tensor_or_optimizer_created':False,'training_steps':0,'neural_or_mask_quality_measured':False,'frozen305_read_or_written_by_probe':False,'owner_approved':False,'training_gold':False,'launch_allowed':False,'new_modules':sorted(new),'limits':protocol['interpretation_limits'],'followup':'Owner/gold/privacy/rights/family/content admission must be enforced before converting records. Do not treat native dataset shape or supplied metadata flags as upstream approval enforcement. This is not proof the current305records are directly training-ready.'}
with(P/'pilot-data-adapter-results-v1.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'passes':r['passes'],'cases':len(results),'pure_source_classes_executed':5,'framework_imports':0,'training_steps':0,'frozen305_changed':False})
