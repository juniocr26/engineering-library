"""New owned semantic/static controls; not independent documentation or neural benchmark."""
from pathlib import Path
import datetime,json,hashlib,subprocess
P=Path(__file__).resolve().parent;folder=P/'owned-go-type-relations-v1';folder.mkdir(mode=0o700);binary=P/'offline-go-type-observer-v1/observer';sha=lambda b:hashlib.sha256(b).hexdigest()
base='package owned\ntype Base struct{}\nfunc (Base) Value() int { return 7 }\n'
cases=[
 {'id':'promoted-method','source':base+'type Child struct{ Base }\nfunc Read(c Child) int { return c.Value() }\n','expected_status':'TYPECHECKED_CLOSED_PACKAGE','expected_kind':'MethodVal','expected_name':'Value','expected_index':[0,0]},
 {'id':'field-shadows-method','source':base+'type Child struct{ Base; Value int }\nfunc Read(c Child) int { return c.Value() }\n','expected_status':'INCONCLUSIVE_TYPE_ERRORS','diagnostic_contains':'cannot call'},
 {'id':'pointer-value-not-interface','source':'package owned\ntype Base struct{}\nfunc (*Base) Value() int { return 7 }\ntype Reader interface { Value() int }\nvar _ Reader = Base{}\n','expected_status':'INCONCLUSIVE_TYPE_ERRORS','diagnostic_contains':'pointer receiver'},
 {'id':'addressable-pointer-method','source':'package owned\ntype Base struct{}\nfunc (*Base) Value() int { return 7 }\nfunc Read(b Base) int { return b.Value() }\n','expected_status':'TYPECHECKED_CLOSED_PACKAGE','expected_kind':'MethodVal','expected_name':'Value'},
 {'id':'interface-method-not-concrete','source':'package owned\ntype Reader interface { Value() int }\nfunc Read(r Reader) int { return r.Value() }\n','expected_status':'TYPECHECKED_CLOSED_PACKAGE','expected_kind':'MethodVal','expected_name':'Value','receiver_contains':'Reader'},
 {'id':'ambiguous-promotion','source':'package owned\ntype A struct{}\nfunc(A) Value()int{return 1}\ntype B struct{}\nfunc(B) Value()int{return 2}\ntype Child struct{A;B}\nfunc Read(c Child)int{return c.Value()}\n','expected_status':'INCONCLUSIVE_TYPE_ERRORS','diagnostic_contains':'ambiguous selector'},
 {'id':'method-expression-vs-value','source':base+'var methodExpression = Base.Value\nvar boundMethod = Base{}.Value\n','expected_status':'TYPECHECKED_CLOSED_PACKAGE','expected_kinds':['MethodExpr','MethodVal']},
 {'id':'imports-outside-v1-profile','source':'package owned\nimport "context"\nfunc Keep(c context.Context) context.Context{return c}\n','expected_status':'REFUSED','diagnostic_contains':'Imports are unsupported'},
]
protocol={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hypothesis':'Owned syntax-valid selector forms can denote promoted methods, fields, interface methods or ambiguous/invalid calls. Actual go/types for a closed package adds bounded static relation evidence but cannot prove dynamic dispatch or imports.','binary_sha256':sha(binary.read_bytes()),'cases':cases,'package_language_version':'go1.24','host_compiler':'Go1.27.1 darwin/arm64','scope':'Eight related owned DEVELOPMENT controls. No actual target application/functions/tests executed, imports/network, independent documentation performance or universal semantic verification.'}
(folder/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');rows=[]
for c in cases:
 raw=json.dumps({'package_path':'owned/type-observation','files':[{'path':'owned.go','source':c['source']}]}).encode();(folder/(c['id']+'.request.json')).write_bytes(raw);(folder/(c['id']+'.source.go')).write_text(c['source']);command=[str(binary)];r=subprocess.run(command,input=raw,capture_output=True,timeout=20);(folder/(c['id']+'.response.json')).write_bytes(r.stdout);(folder/(c['id']+'.stderr.txt')).write_bytes(r.stderr);packet=json.loads(r.stdout);matched=r.returncode==0 and packet['status']==c['expected_status'] and packet['source_executed'] is False and packet['runtime_bindings_verified'] is False
 if 'diagnostic_contains' in c:matched=matched and any(c['diagnostic_contains'] in x for x in packet['diagnostics']) and not packet['selections']
 if 'expected_kind' in c:matched=matched and any(s['kind']==c['expected_kind'] and s['name']==c['expected_name'] for s in packet['selections'])
 if 'expected_index' in c:matched=matched and any(s['index']==c['expected_index'] for s in packet['selections'])
 if 'receiver_contains' in c:matched=matched and any(c['receiver_contains'] in s['receiver'] for s in packet['selections'])
 if 'expected_kinds' in c:matched=matched and [s['kind'] for s in packet['selections']]==c['expected_kinds']
 rows.append({'id':c['id'],'command':command,'exit_code':r.returncode,'packet':packet,'expected_status':c['expected_status'],'matched':matched})
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':sha((folder/'protocol.json').read_bytes()),'records':rows,'matched':sum(r['matched'] for r in rows),'cases':len(rows),'partial_type_info_admitted':False,'independent_accuracy_metric':None,'target_source_executed':False,'new_model_calls':0,'production_tools_modified':False}
(folder/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='records'}));print(json.dumps([{'id':r['id'],'status':r['packet']['status'],'selections':r['packet']['selections'],'diagnostics':r['packet']['diagnostics'],'matched':r['matched']} for r in rows]));assert all(r['matched'] for r in rows)
