"""Re-derive and verify frozen P source relations without executing upstream code."""
import ast,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
protocol=json.loads((P/'typed-python-source-relation-protocol-v1.json').read_text())
refs={r['claim_id']:r for r in protocol['source_refs']}
def structured(node):
 if isinstance(node,ast.AST):return {'node':type(node).__name__,**{k:structured(v) for k,v in ast.iter_fields(node) if k not in ['ctx','type_comment']}}
 if isinstance(node,list):return [structured(v) for v in node]
 return node
def own(node):
 yield node
 for child in ast.iter_child_nodes(node):
  if not isinstance(child,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef,ast.Lambda)):yield from own(child)
relations=[]
for cid,(owner,line,kind) in protocol['anchors'].items():
 ref=refs[cid];f=P/'frozen-public-sources/fastapi'/ref['source_path'];raw=f.read_bytes();assert hashlib.sha256(raw).hexdigest()==ref['source_file_sha256'];tree=ast.parse(raw.decode());owners=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==owner];assert len(owners)==1;nodes=[n for n in own(owners[0]) if getattr(n,'lineno',None)==line and type(n).__name__==kind];assert len(nodes)==1;n=nodes[0]
 if cid in ['F01','F02']:relation={'relation':'declared_class_field_default','field':structured(n.target),'default':structured(n.value)}
 elif cid=='F04':
  assert isinstance(n.value,ast.Await) and isinstance(n.value.value,ast.Call);call=n.value.value;kw=[k for k in call.keywords if k.arg=='dependency_cache'];assert len(kw)==1;relation={'relation':'written_awaited_recursive_call_keyword','callee':structured(call.func),'keyword':kw[0].arg,'passed_value':structured(kw[0].value)}
 elif cid in ['F03','F05','F06']:
  assert isinstance(n,ast.If) and isinstance(n.body[0],ast.Assign) and len(n.body[0].targets)==1;a=n.body[0];relation={'relation':'selected_guarded_assignment','guard':structured(n.test),'assignment_target':structured(a.targets[0]),'assigned_value':structured(a.value),'qualification':'If control reaches this selected guard; no universal runtime completion statement.'}
 elif cid=='F07':relation={'relation':'selected_local_guard_identifier_absence','guard':structured(n.test),'identifier':'use_cache','present_as_name_or_attribute':any(isinstance(c,ast.Name) and c.id=='use_cache' or isinstance(c,ast.Attribute) and c.attr=='use_cache' for c in ast.walk(n.test)),'qualification':'This selected guard only; no global cache lifetime or all earlier guards assertion.'}
 else:relation={'relation':'written_assert_expression','expression':structured(n.test),'qualification':'Written assertion, not executed test/passing runtime guarantee.'}
 relations.append({'id':cid,'owner':owner,'source_path':ref['source_path'],'source_revision':ref['source_revision'],'source_file_sha256':ref['source_file_sha256'],'source_lines':[n.lineno,n.end_lineno],'mechanically_derived_relation':relation})
f=P/'mechanical-source-prose-v1/fastapi/P/mechanical-relations.json';expected=(json.dumps(relations,ensure_ascii=False,indent=2)+'\n').encode();assert f.read_bytes()==expected
print(json.dumps({'relations':len(relations),'bytes':len(expected),'sha256':hashlib.sha256(expected).hexdigest(),'exact_frozen_bytes_rederived':True,'upstream_source_executed':False}))
