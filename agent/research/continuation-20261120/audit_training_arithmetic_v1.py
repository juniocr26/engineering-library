"""Owned index arithmetic linked to exact pinned trainer AST expressions."""
import ast,datetime,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;protocol=json.loads((P/'training-arithmetic-protocol-v1.json').read_text());source=P/protocol['source_path'];raw=source.read_bytes();assert hashlib.sha256(raw).hexdigest()==protocol['source_sha256'];tree=ast.parse(raw.decode())
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
def value_of(function,target):
 return [ast.unparse(n.value)for n in ast.walk(funcs[function])if isinstance(n,ast.Assign)and len(n.targets)==1 and ast.unparse(n.targets[0])==target]
expected={'loss_steps':('default_loss','steps',['mx.arange(1, targets.shape[1] + 1)']),'loss_mask':('default_loss','mask',['mx.logical_and(steps >= lengths[:, 0:1], steps <= lengths[:, 1:])']),'original_lengths':('iterate_batches','lengths',['[len(x) for x in batch]']),'padded_width':('iterate_batches','max_length_in_batch',['1 + pad_to * ((max(lengths) + pad_to - 1) // pad_to)','min(max_length_in_batch, max_seq_length)']),'truncated_length':('iterate_batches','truncated_length',['min(lengths[j], max_seq_length)']),'reported_length':('iterate_batches','lengths[j]',['truncated_length'])}
checks={}
for name,(func,target,values)in expected.items():
 actual=value_of(func,target);assert actual==values,(name,actual);checks[name]={'verified':True,'expressions':actual}
loops=[n for n in ast.walk(funcs['train'])if isinstance(n,ast.For)and ast.unparse(n.target)=='(it, batch)'];assert len(loops)==1;loop=loops[0]
validation=next(i for i,n in enumerate(loop.body)if isinstance(n,ast.If)and'args.steps_per_eval'in ast.unparse(n.test))
step=next(i for i,n in enumerate(loop.body)if isinstance(n,ast.Assign)and isinstance(n.value,ast.Call)and ast.unparse(n.value.func)=='step')
assert validation<step
call=loop.body[step].value;assert ast.unparse(call.args[2])=='it % grad_accum_steps == 0'
checks['validation_before_step']={'verified':True,'validation_statement_index':validation,'step_statement_index':step,'update_condition':ast.unparse(call.args[2])}
rows=[]
for case in protocol['token_cases']:
 n=case['token_count'];offset=case['prompt_offset'];cap=case['max_seq_length'];width=min(1+32*((n+31)//32),cap);truncated=min(n,cap)
 written=[i for i in range(1,width)if i>=offset and i<=truncated]
 legal=[i for i in range(1,truncated)if i>=offset]
 padding=[i for i in written if i>=truncated]
 original_assistant=[i for i in range(max(1,offset),n)]
 lost=[i for i in original_assistant if i>=truncated]
 rows.append({**case,'padded_batch_width':width,'retained_sequence_tokens':truncated,'written_supervised_target_indices':written,'legal_original_target_indices':legal,'padding_indices_selected_by_written_formula':padding,'written_ntoks':len(written),'legal_ntoks':len(legal),'zero_denominator_on_written_formula':not written,'assistant_original_target_count':len(original_assistant),'assistant_targets_truncated':len(lost),'formula_matches_original_target_domain':written==legal,'runtime_framework_observation':False})
schedules=[]
for case in protocol['schedule_cases']:
 iters=case['iterations'];accum=case['gradient_accumulation'];every=case['validation_every']
 validations=[{'iteration':it,'updates_already_completed':(it-1)//accum,'current_iteration_will_update':it%accum==0}for it in range(1,iters+1)if it==1 or it%every==0 or it==iters]
 schedules.append({**case,'written_update_iterations':[i for i in range(1,iters+1)if i%accum==0],'update_count':iters//accum,'unapplied_accumulation_remainder_batches':iters%accum,'validations':validations,'last_validation_matches_final_update_count':validations[-1]['updates_already_completed']==iters//accum,'note':'Counts follow written loop/guard only. No execution or callback behavior is simulated; final weights do not encode partial accumulated gradients.'})
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'framework_revision':protocol['framework_revision'],'source_sha256':protocol['source_sha256'],'source_ast_checks':checks,'token_cases':rows,'schedule_cases':schedules,'findings':{'padding_target_cases':sum(bool(r['padding_indices_selected_by_written_formula'])for r in rows),'zero_supervised_target_cases':sum(r['zero_denominator_on_written_formula']for r in rows),'scope':'The pinned written formula includes a padded target at index n when batch width exceeds n. This is a static arithmetic counterexample, not a runtime-verified upstream defect or a claim about all MLX versions.','future_gate':'Do not accept this pinned trainer for a pilot until actual tokenizer/mask/batch behavior is validated and padding/zero-target conditions are resolved in a separately authorized environment.'},'source_executed':False,'mlx_or_numpy_imported':False,'model_or_optimizer_run':False,'training_steps':0,'upstream_modified':False,'automatic_upstream_issue_filed':False}
with(P/'training-arithmetic-audit-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print(json.dumps({'ast_checks':len(checks),'token_cases':len(rows),'schedule_cases':len(schedules),'padding_target_cases':record['findings']['padding_target_cases'],'zero_target_cases':record['findings']['zero_supervised_target_cases']}))
