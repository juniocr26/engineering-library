"""New scope-field counterexamples missed by ast.Name Store scans."""
import ast,datetime,hashlib,importlib.util,json
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('scope_observer',P/'architecture_fact_observer_v3.py');observer=importlib.util.module_from_spec(spec);spec.loader.exec_module(observer)
base={n:(observer.SOURCE/n).read_bytes()for n in observer.FILES};rows=[]
def add(id,statement,expected,reason):
 sources=dict(base)
 if statement:
  tree=ast.parse(sources['adapter.py']);read=next(n for n in ast.walk(tree)if isinstance(n,ast.FunctionDef)and n.name=='read');read.body[0].body.insert(0,ast.parse(statement).body[0]);ast.fix_missing_locations(tree);compile(tree,'owned-scope-mutation','exec');sources['adapter.py']=(ast.unparse(tree)+'\n').encode()
 rows.append({'id':id,'expected':expected,'reason':reason,'sources':{n:b.decode()for n,b in sources.items()},'sha256':{n:hashlib.sha256(b).hexdigest()for n,b in sources.items()}})
add('scope-original',None,'DERIVED','Original closed owned source remains supported.')
add('local-function-shadows-catch','def GatewayUnavailable():\n    pass','REFUSED','FunctionDef.name binds a function local even though no ast.Name Store represents its declaration.')
add('local-class-shadows-raised-type','class BalanceUnavailable:\n    pass','REFUSED','ClassDef.name binds an imported exception spelling in function scope.')
add('local-import-shadows-mapper','from mapping import balance_from_payload','REFUSED','ImportFrom alias binds a local imported spelling without ast.Name Store.')
add('match-capture-shadows-catch','match None:\n    case GatewayUnavailable:\n        pass','REFUSED','MatchAs.name is a binding field outside ast.Name Store.')
add('globals-write-changes-catch',"globals()['GatewayUnavailable'] = ValueError",'REFUSED','Dynamic namespace access is outside a closed imported-identity claim profile.')
add('exec-can-change-namespace',"exec('GatewayUnavailable = ValueError')",'REFUSED','Dynamic code execution is outside this no-resolution syntax profile, although inspected source is never executed here.')
add('unrelated-local-definition','def unrelated_local():\n    pass','DERIVED','A local declaration with an unrelated name does not shadow a selected imported identity or alter the direct protected call/raise shape.')
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_before_predictions':True,'rows':rows,'source_executed':False,'permanent_test_files_modified':False,'model_calls':0,'scope':'Owned mutation development follow-up after V3 twelve-case repair; not independent public evaluation.'}
with(P/'architecture-scope-oracle-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'cases':len(rows)})
