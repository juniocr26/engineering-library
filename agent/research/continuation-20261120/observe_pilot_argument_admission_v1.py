"""Execute only the reviewed pure argument-builder; never import MLX or call main/run/train."""
import argparse,ast,contextlib,copy,datetime,hashlib,io,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];protocol=json.loads((P/'pilot-argument-admission-protocol-v1.json').read_text());file=ROOT/protocol['source_path'];raw=file.read_bytes();assert hashlib.sha256(raw).hexdigest()==protocol['source_sha256']=='341dce80747705c9363728823d3f117e96f821fc3b35d35db2f47b3151d3adc5';text=raw.decode();tree=ast.parse(text);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='build_parser')
assert not fn.decorator_list and not fn.args.args and not fn.args.kwonlyargs and fn.args.vararg is None and fn.args.kwarg is None and fn.returns is None and len(fn.body)==29
first=fn.body[0];assert isinstance(first,ast.Assign)and len(first.targets)==1 and isinstance(first.targets[0],ast.Name)and first.targets[0].id=='parser';factory=first.value;assert isinstance(factory,ast.Call)and isinstance(factory.func,ast.Attribute)and isinstance(factory.func.value,ast.Name)and factory.func.value.id=='argparse'and factory.func.attr=='ArgumentParser'and not factory.args
assert all(k.arg=='description'and type(ast.literal_eval(k.value))is str for k in factory.keywords)
metadata=[]
for statement in fn.body[1:-1]:
 assert isinstance(statement,ast.Expr)and isinstance(statement.value,ast.Call);call=statement.value;assert isinstance(call.func,ast.Attribute)and isinstance(call.func.value,ast.Name)and call.func.value.id=='parser'and call.func.attr=='add_argument';flags=[ast.literal_eval(a)for a in call.args];assert flags and all(type(f)is str and f.startswith('-')for f in flags);kwargs={}
 for keyword in call.keywords:
  assert keyword.arg in ['type','help','choices','default','action']
  if keyword.arg=='type':assert isinstance(keyword.value,ast.Name)and keyword.value.id in ['str','int','float','_parse_size'];kwargs['type_symbol']=keyword.value.id
  else:kwargs[keyword.arg]=ast.literal_eval(keyword.value)
 metadata.append({'flags':flags,'keywords':kwargs,'source_line':statement.lineno,'end_line':statement.end_lineno})
assert isinstance(fn.body[-1],ast.Return)and isinstance(fn.body[-1].value,ast.Name)and fn.body[-1].value.id=='parser'
default_assignment=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='CONFIG_DEFAULTS'for x in n.targets));defaults=ast.literal_eval(default_assignment.value);assert type(defaults)is dict
main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main');merge_spans=[]
for name in ['config','CONFIG_DEFAULTS']:
 actual=next(n for n in ast.walk(main)if isinstance(n,ast.For)and isinstance(n.iter,ast.Call)and isinstance(n.iter.func,ast.Attribute)and isinstance(n.iter.func.value,ast.Name)and n.iter.func.value.id==name)
 expected=ast.parse('for k, v in '+name+'.items():\n    if args.get(k, None) is None:\n        args[k] = v\n').body[0];assert ast.dump(actual,include_attributes=False)==ast.dump(expected,include_attributes=False);merge_spans.append({'name':name,'first_line':actual.lineno,'last_line':actual.end_lineno,'quote':ast.get_source_segment(text,actual)})
proxy_calls=[]
def unsupported_size(value):proxy_calls.append(value);raise ValueError('Unknown _parse_size implementation is outside this reviewed source subset')
namespace={'__builtins__':{'str':str,'int':int,'float':float},'argparse':argparse,'_parse_size':unsupported_size};modules_before=set(sys.modules);exec(compile(ast.Module(body=[copy.deepcopy(fn)],type_ignores=[]),str(file)+'::selected-pure-build_parser','exec'),namespace);builder=namespace['build_parser'];rows=[]
def field(data,key):
 for part in key.split('.'):data=data[part]
 return data
for case in protocol['cases']:
 stderr=io.StringIO();observed={};status='PARSED_MERGED'
 if '--clear-cache-threshold'in case['argv_tokens']:status='OWN_UNSUPPORTED_CONVERTER'
 else:
  parser=builder()
  with contextlib.redirect_stderr(stderr):
   try:
    args=vars(parser.parse_args(case['argv_tokens']))
   except (SystemExit,argparse.ArgumentError):status='REFUSED_ARGUMENTS';args=None
  if args is not None:
   for k,v in copy.deepcopy(case['predecoded_owned_config']).items():
    if args.get(k,None)is None:args[k]=v
   for k,v in copy.deepcopy(defaults).items():
    if args.get(k,None)is None:args[k]=v
   observed={key:field(args,key)for key in case['expected_fields']}
 checks={key:type(observed.get(key))is type(value)and observed.get(key)==value for key,value in case['expected_fields'].items()};rows.append({'id':case['id'],'status':status,'observed_fields':observed,'field_checks':checks,'stderr':stderr.getvalue(),'pass':status==case['expected_status']and all(checks.values())})
new_modules=set(sys.modules)-modules_before;forbidden=[name for name in new_modules if name.split('.')[0]in ['mlx','mlx_lm','numpy','yaml','tqdm']];assert not forbidden and not proxy_calls
run=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='run');load_assignment=next(n for n in run.body if isinstance(n,ast.Assign)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='load');dataset_assignment=next(n for n in run.body if isinstance(n,ast.Assign)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='load_dataset');train_branch=next(n for n in run.body if isinstance(n,ast.If));assert load_assignment.lineno<dataset_assignment.lineno<train_branch.lineno
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':hashlib.sha256((P/'pilot-argument-admission-protocol-v1.json').read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(raw).hexdigest(),'selected_function':{'name':fn.name,'first_line':fn.lineno,'last_line':fn.end_lineno,'quote':ast.get_source_segment(text,fn),'quote_sha256':hashlib.sha256(ast.get_source_segment(text,fn).encode()).hexdigest()},'argument_metadata':metadata,'literal_config_defaults':defaults,'reviewed_merge_spans':merge_spans,'rows':rows,'passes':sum(row['pass']for row in rows),'cases':len(rows),'upstream_pure_build_parser_executed':True,'upstream_module_imported':False,'mlx_numpy_yaml_tqdm_imported':False,'framework_training_or_run_main_called':False,'unknown_size_converter_executed':False,'new_imported_modules':sorted(new_modules),'static_run_order':{'load_call_line':load_assignment.lineno,'load_dataset_line':dataset_assignment.lineno,'train_test_branch_line':train_branch.lineno,'finding':'Absence of --train is not a safe dry run of upstream main/run: selected source places model/data loading before branch admission. Neither main nor run was executed here.'},'important_findings':['Default model/data and budgets are not the owner pilot; model/data roots remain unresolved.','None-only merge means config trust_remote_code true and clear_cache_threshold nonzero do not override CLI False/0 defaults.','Predecoded config values bypass parser choices and scalar casts at this merge; downstream validation is separate and was not executed.','launch_allowed false is a documentary field, not an upstream launch guard: the inspected run does not check it.','LoRA rank/scale are configuration-only nested values in this CLI, not standalone --rank flags.','The unknown size converter and actual YAML syntax were not evaluated.'],'training_steps':0,'optimizer_created':False,'model_or_tokenizer_loaded':False,'weights_downloaded':False,'packages_installed':False,'training_launch_command_emitted':False,'launch_allowed':False,'owner_approved':False,'training_gold':False,'readiness':'NO-GO_UNCHANGED','limits':protocol['limits']}
with(P/'pilot-argument-admission-results-v1.json').open('x')as f:f.write(json.dumps(r,indent=2,allow_nan=False)+'\n')
print({'passes':r['passes'],'cases':r['cases'],'pure_builder_executed':True,'framework_imported':False,'optimizer_steps':0,'new_modules':r['new_imported_modules']})
