"""New local binder and loader-import ownership cases, no source execution."""
import ast
import datetime
import json
from pathlib import Path

P=Path(__file__).resolve().parent
base=json.loads((P/'transport-mapping-control-oracle-v1.json').read_text())['rows'][0]['sources']
transport=base['httpx/_transports/default.py'];errors=base['httpx/_exceptions.py']
rows=[]


def rename(source,names):
    class Rename(ast.NodeTransformer):
        def visit_Name(self,node):
            node.id=names.get(node.id,node.id)
            return node
        def visit_ExceptHandler(self,node):
            if node.name:
                node.name=names.get(node.name,node.name)
            return self.generic_visit(node)
    tree=Rename().visit(ast.parse(source));ast.fix_missing_locations(tree);compile(tree,'owned-binding-scope','exec')
    return ast.unparse(tree)+'\n'


def add(identity,expected,t):
    rows.append({'id':identity,'expected':expected,'sources':{'httpx/_transports/default.py':t,'httpx/_exceptions.py':errors}})

add('scope-original','WRITTEN_MAPPING_FACTS',transport)
add('caught-binding-shadows-str','INCONCLUSIVE',rename(transport,{'exc':'str'}))
add('loop-target-shadows-issubclass','INCONCLUSIVE',rename(transport,{'to_exc':'issubclass'}))
add('loop-source-shadows-isinstance','INCONCLUSIVE',rename(transport,{'from_exc':'isinstance'}))
add('accumulator-shadows-caught-exception-type','INCONCLUSIVE',rename(transport,{'mapped_exc':'Exception'}))
add('message-binding-shadows-str','INCONCLUSIVE',rename(transport,{'message':'str'}))
add('loop-target-shadows-module-map','INCONCLUSIVE',rename(transport,{'to_exc':'HTTPCORE_EXC_MAP'}))
function=next(n for n in ast.parse(transport).body if isinstance(n,ast.FunctionDef)and n.name=='map_httpcore_exceptions')
handler_source=ast.unparse(function)+'\n'
lazy_prefix="import contextlib\nimport typing\nfrom .._exceptions import NetworkError, ConnectError\nHTTPCORE_EXC_MAP = {}\n\ndef _load_httpcore_exceptions():\n    import httpcore\n    return {httpcore.NetworkError: NetworkError, httpcore.ConnectError: ConnectError}\n\n"
lazy_function=handler_source.replace('def map_httpcore_exceptions() -> typing.Iterator[None]:\n','def map_httpcore_exceptions() -> typing.Iterator[None]:\n    global HTTPCORE_EXC_MAP\n    if len(HTTPCORE_EXC_MAP) == 0:\n        HTTPCORE_EXC_MAP = _load_httpcore_exceptions()\n')
lazy=lazy_prefix+lazy_function
shadowed=lazy.replace('import httpcore\n','import httpcore as NetworkError\n').replace('httpcore.NetworkError:','NetworkError.NetworkError:').replace('httpcore.ConnectError:','NetworkError.ConnectError:')
add('loader-local-import-shadows-target-class','INCONCLUSIVE',shadowed)
add('lazy-message-binding-shadows-loader','INCONCLUSIVE',rename(lazy,{'message':'_load_httpcore_exceptions'}))
add('unambiguous-renamed-local-bindings','WRITTEN_MAPPING_FACTS',rename(transport,{'exc':'caught_err','from_exc':'source_cls','to_exc':'target_cls','mapped_exc':'selected_cls','message':'error_message'}))
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_before_predictions':True,'rows':rows,'scope':'Owned scope-binding follow-up after16structural controls; targets lexical local shadowing, not actual HTTPX defects.','source_executed':False,'model_calls':0,'permanent_tests_changed':False,'new_public_family_or_independent_holdout':False}
with(P/'transport-scope-control-oracle-v1.json').open('x')as stream:stream.write(json.dumps(record,indent=2)+'\n')
print({'controls':len(rows)})
