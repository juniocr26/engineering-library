"""Pure dataset interface observations and static special-token metadata; no tokenizer or renderer."""
import ast,builtins,copy,datetime,hashlib,json,typing
from pathlib import Path
P=Path(__file__).resolve().parent
protocol=json.loads((P/'pilot-template-interface-protocol-v1.json').read_text())
source=P/'training-primary-sources-v1/mlx-lm--mlx_lm--tuner--datasets.py'
raw=source.read_bytes()
assert hashlib.sha256(raw).hexdigest()==protocol['source_sha256']
tree=ast.parse(raw)
node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ChatDataset')
assert not node.bases and not node.decorator_list
for item in ast.walk(node):
    assert not isinstance(item,(ast.Import,ast.ImportFrom,ast.With,ast.Global,ast.Nonlocal))
    if isinstance(item,ast.Name):
        assert item.id not in ['open','eval','exec','compile','__import__','load_dataset']
namespace={
    '__name__':'owned_selected_chat_interface',
    '__builtins__':{'__build_class__':builtins.__build_class__,'object':object,'len':len,'str':str,'int':int,'bool':bool},
    'List':typing.List,'Dict':typing.Dict,'PreTrainedTokenizer':object,
}
exec(compile(ast.Module(body=[copy.deepcopy(node)],type_ignores=[]),str(source)+'::ChatDatasetOnly','exec'),namespace)
Chat=namespace['ChatDataset']
class OwnedPairResults:
    def __init__(self,full,prefix):
        self.full=full
        self.prefix=prefix
        self.calls=[]
    def apply_chat_template(self,messages,**kwargs):
        self.calls.append({'messages':copy.deepcopy(messages),'kwargs':kwargs})
        return list(self.full if len(messages)==2 else self.prefix)
rows=[]
for case in protocol['cases']:
    content='' if case['empty_assistant_content'] else 'owned assistant target'
    datum={'messages':[{'role':'user','content':'owned user input'},{'role':'assistant','content':content}]}
    sink=OwnedPairResults(case['owned_full_result'],case['owned_prefix_result'])
    dataset=Chat([datum],sink,mask_prompt=True)
    tokens,offset=dataset.process(dataset[0])
    observed={
        'offset':offset,'full_length':len(tokens),
        'prefix_equal':tokens[:offset]==case['owned_prefix_result'],
        'offset_within_full':0<=offset<=len(tokens),
        'raw_target_interval_length':max(0,len(tokens)-offset),
    }
    checks={key:type(observed[key])is type(value) and observed[key]==value for key,value in case['expected_fields'].items()}
    rows.append({'id':case['id'],'observed':observed,'checks':checks,'pass':all(checks.values()),'source_process_returned_without_admission_error':True,'owned_method_calls':sink.calls})
config_path=P/protocol['metadata_files'][0]
tokenizer_path=P/protocol['metadata_files'][1]
config=json.loads(config_path.read_text())
metadata=json.loads(tokenizer_path.read_text())
added=metadata['added_tokens_decoder']
ids=sorted(map(int,added))
by_content={value['content']:int(key) for key,value in added.items()}
bos_id=by_content[metadata['bos_token']]
eos_id=by_content[metadata['eos_token']]
model_eos=config['eos_token_id'] if isinstance(config['eos_token_id'],list) else [config['eos_token_id']]
metadata_result={
    'config_sha256':hashlib.sha256(config_path.read_bytes()).hexdigest(),
    'tokenizer_config_sha256':hashlib.sha256(tokenizer_path.read_bytes()).hexdigest(),
    'added_token_count':len(ids),'minimum_added_id':min(ids),'maximum_added_id':max(ids),
    'configured_vocab_size':config['vocab_size'],
    'all_added_ids_within_configured_vocab':all(0<=i<config['vocab_size'] for i in ids),
    'bos_content':metadata['bos_token'],'bos_metadata_id':bos_id,'model_bos_id':config['bos_token_id'],
    'bos_ids_agree':bos_id==config['bos_token_id'],
    'tokenizer_eos_content':metadata['eos_token'],'tokenizer_eos_metadata_id':eos_id,
    'model_eos_ids':model_eos,'tokenizer_eos_is_in_model_eos_set':eos_id in model_eos,
    'all_model_eos_metadata_labels':{str(i):added.get(str(i),{}).get('content') for i in model_eos},
    'tokenizer_class_metadata':metadata['tokenizer_class'],
    'template_contains_conditional_date_branch':'strftime_now' in metadata['chat_template'],
    'date_branch_is_potential_not_executed_cause':True,
    'template_sha256':hashlib.sha256(metadata['chat_template'].encode()).hexdigest(),
    'template_rendered':False,'actual_tokenizer_loaded':False,
    'full_BPE_vocabulary_or_weights_acquired':False,
}
r={
    'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'protocol_sha256':hashlib.sha256((P/'pilot-template-interface-protocol-v1.json').read_bytes()).hexdigest(),
    'rows':rows,'passes':sum(row['pass']for row in rows),'cases':len(rows),
    'metadata':metadata_result,
    'selected_pure_ChatDataset_source_executed':True,
    'real_tokenizer_or_Jinja_or_MLX_Transformers_imported':False,
    'renderer_status':protocol['metadata_only_template_execution_status'],
    'training_steps':0,'loss_or_actual_supervision_measured':False,
    'frozen305_modified':False,'owner_gold':0,'launch_allowed':False,'readiness':'NO-GO_UNCHANGED',
    'findings':[
        'The source adapter accepted all four owned interface results,including nonprefix,offsetlargerthanfull andemptyassistantcontent. This establishes unchecked interface assumptions,not a real tokenizer defect.',
        'Static specialtoken metadata alignment is necessary bookkeeping,not actual tokenization/template/checkpoint compatibility.',
        'Jinja2/MarkupSafe were absent;no template renderer was installed or manually substituted. Optional rendering remains unexecuted.',
        'A conditional date branch is visible in template metadata but was not executed or identified as any observed failure cause.',
    ],
    'limits':protocol['limits'],
}
with(P/'pilot-template-interface-results-v1.json').open('x')as stream:
    json.dump(r,stream,indent=2)
    stream.write('\n')
print({'owned_interface_cases':len(rows),'passes':r['passes'],'added_tokens':len(ids),'bos_agrees':metadata_result['bos_ids_agree'],'eos_member':metadata_result['tokenizer_eos_is_in_model_eos_set'],'real_tokenizer':False})
