"""Research-only AST relation checker; typed claims only, never source execution."""
import ast,copy,datetime,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
protocol=json.loads((HERE/'typed-python-source-relation-protocol-v1.json').read_text());inputs=json.loads((HERE/'typed-python-source-relation-claims-v1.json').read_text())
def normalized(node):
 node=copy.deepcopy(node)
 for child in ast.walk(node):
  if hasattr(child,'ctx'):child.ctx=ast.Load()
 return ast.dump(node,include_attributes=False)
def owned_walk(node):
 yield node
 for child in ast.iter_child_nodes(node):
  if isinstance(child,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef,ast.Lambda)):continue
  yield from owned_walk(child)
def observe(claim):
 ref=claim['source_ref'];f=HERE/'frozen-public-sources'/'fastapi'/ref['source_path'];raw=f.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=ref['source_file_sha256']:return {'verdict':'INSUFFICIENT','reason':'SOURCE_HASH_MISMATCH'}
 if claim['typed_claim']['kind']=='universal_runtime':return {'verdict':'INSUFFICIENT','reason':'RUNTIME_UNIVERSAL_OUTSIDE_TYPED_SOURCE_PROFILE'}
 tree=ast.parse(raw.decode());anchor=claim['anchor'];owners=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==anchor['owner']]
 if len(owners)!=1:return {'verdict':'INSUFFICIENT','reason':'MISSING_OR_AMBIGUOUS_TOP_LEVEL_OWNER'}
 nodes=[n for n in owned_walk(owners[0]) if getattr(n,'lineno',None)==anchor['line'] and type(n).__name__==anchor['ast_kind']]
 if len(nodes)!=1:return {'verdict':'INSUFFICIENT','reason':'MISSING_OR_AMBIGUOUS_OWNED_ANCHOR'}
 n=nodes[0];kind=claim['typed_claim']['kind'];actual=None
 if kind=='declared_default' and isinstance(n,ast.AnnAssign) and isinstance(n.target,ast.Name) and n.value is not None:actual={'kind':kind,'field':n.target.id,'value':normalized(n.value)}
 elif kind=='guarded_assignment' and isinstance(n,ast.If) and n.body and isinstance(n.body[0],ast.Assign) and len(n.body[0].targets)==1:
  a=n.body[0];actual={'kind':kind,'guard':normalized(n.test),'target':normalized(a.targets[0]),'value':normalized(a.value)}
 elif kind=='awaited_call_keyword' and isinstance(n,ast.Assign) and isinstance(n.value,ast.Await) and isinstance(n.value.value,ast.Call):
  call=n.value.value;k=claim['typed_claim']['keyword'];keywords=[kw for kw in call.keywords if kw.arg==k]
  if len(keywords)==1:actual={'kind':kind,'function':normalized(call.func),'keyword':k,'value':normalized(keywords[0].value)}
 elif kind=='guard_identifier_absence' and isinstance(n,ast.If):
  ident=claim['typed_claim']['identifier'];present=any(isinstance(c,ast.Name) and c.id==ident or isinstance(c,ast.Attribute) and c.attr==ident for c in ast.walk(n.test));actual={'kind':kind,'identifier':ident,'absent':not present}
 elif kind=='asserted_expression' and isinstance(n,ast.Assert):actual={'kind':kind,'expression':normalized(n.test)}
 if actual is None:return {'verdict':'INSUFFICIENT','reason':'UNADMITTED_ROLE_OR_AST_SHAPE'}
 return {'verdict':'SUPPORTED' if actual==claim['typed_claim'] else 'CONTRADICTED','actual_typed_relation':actual,'source_sha256':hashlib.sha256(raw).hexdigest(),'source_revision':ref['source_revision'],'source_path':ref['source_path'],'owner':anchor['owner'],'source_lines':[n.lineno,n.end_lineno],'exact_source':ast.get_source_segment(raw.decode(),n),'proof_limit':'Exact syntax relation only. No dynamic binding, runtime guarantee, natural-language parsing or full-note acceptance.'}
records=[]
for request in inputs['claims']:records.append({'request':request,'observation':observe(request)})
labels=['SUPPORTED','CONTRADICTED','INSUFFICIENT'];matrix={r:{c:0 for c in labels} for r in labels}
for row in records:matrix[row['request']['expected']][row['observation']['verdict']]+=1
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':'typed-python-source-relation-protocol-v1.json','inputs_sha256':hashlib.sha256((HERE/'typed-python-source-relation-claims-v1.json').read_bytes()).hexdigest(),'records':records,'matrix_reference_rows_observed_columns':matrix,'matches':sum(r['request']['expected']==r['observation']['verdict'] for r in records),'cases':len(records),'scope':'27controlled typed propositions from nine already exposed related static source facts; not arbitrary prose accuracy, model-weight gain or independent evaluation.','natural_language_mapping':'Manually specified and source-reviewed, outside machine proof. Exact source membership alone not sufficient.','no_complete_note_acceptance_from_this_observer':True,'source_execution':False,'model_calls':0,'optimizer_updates':0,'gold':0,'production_changes':False,'permanent_tests_added':False}
with (HERE/'typed-python-source-relation-results-v1.json').open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({k:result[k] for k in ['at','matrix_reference_rows_observed_columns','matches','cases']},indent=2))
print('Disagreements',[(r['request']['id'],r['observation']) for r in records if r['request']['expected']!=r['observation']['verdict']])
