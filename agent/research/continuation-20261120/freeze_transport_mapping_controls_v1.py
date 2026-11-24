"""Freeze nonexecuted mapping/catch/hierarchy counterexamples before extraction."""
import ast
import datetime
import json
from pathlib import Path

P = Path(__file__).resolve().parent
freeze = json.loads((P/'httpx-source-family-freeze-v1.json').read_text())
old = next(c for c in freeze['revisions'] if c['tag']=='0.25.2')
raw = (P/'new-public-sources-v1/encode--httpx'/old['revision']/'httpx/_transports/default.py').read_text()
node = next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='map_httpcore_exceptions')
function = ast.unparse(node)+'\n'
imports = 'import contextlib\nimport typing\nimport httpcore\nfrom .._exceptions import NetworkError, ConnectError\n\n'
literal = '{httpcore.NetworkError: NetworkError, httpcore.ConnectError: ConnectError}'
transport = imports+function+'\nHTTPCORE_EXC_MAP = '+literal+'\n'
errors = 'class HTTPError(Exception):\n    pass\nclass RequestError(HTTPError):\n    pass\nclass NetworkError(RequestError):\n    pass\nclass ConnectError(NetworkError):\n    pass\n'
rows=[]

def add(identity, expected, t=transport, e=errors):
    rows.append({'id':identity,'expected':expected,'sources':{'httpx/_transports/default.py':t,'httpx/_exceptions.py':e}})

add('owned-two-pair-map','WRITTEN_MAPPING_FACTS')
add('reverse-source-target-direction','INCONCLUSIVE',t=transport.replace(literal,'{NetworkError: httpcore.NetworkError, ConnectError: httpcore.ConnectError}'))
add('unimported-target','INCONCLUSIVE',t=transport.replace('httpcore.ConnectError: ConnectError','httpcore.ConnectError: ForeignError'))
add('dictionary-unpacking','INCONCLUSIVE',t=transport.replace(literal,'{**build_map()}'))
add('duplicate-source-key','INCONCLUSIVE',t=transport.replace(literal,'{httpcore.NetworkError: NetworkError, httpcore.NetworkError: ConnectError}'))
add('second-map-binding','INCONCLUSIVE',t=transport+'HTTPCORE_EXC_MAP = {}\n')
add('target-import-shadowed','INCONCLUSIVE',t=transport+'from .._exceptions import ConnectError as NetworkError\n')
add('missing-target-class','INCONCLUSIVE',e=errors.replace('class ConnectError(NetworkError):\n    pass\n',''))
add('cyclic-target-declarations','INCONCLUSIVE',e=errors.replace('class NetworkError(RequestError):','class NetworkError(ConnectError):'))
add('mapped-cause-changed','INCONCLUSIVE',t=transport.replace('raise mapped_exc(message) from exc','raise mapped_exc(message) from None'))
add('unmapped-error-suppressed','INCONCLUSIVE',t=transport.replace('if mapped_exc is None:\n            raise','if mapped_exc is None:\n            return'))
add('specificity-condition-reversed','INCONCLUSIVE',t=transport.replace('issubclass(to_exc, mapped_exc)','issubclass(mapped_exc, to_exc)'))
add('different-catch-domain','INCONCLUSIVE',t=transport.replace('except Exception as exc:','except BaseException as exc:'))
add('decorator-not-established','INCONCLUSIVE',t=transport.replace('@contextlib.contextmanager','@unresolved_decorator'))
add('contextlib-import-rebound','INCONCLUSIVE',t=transport+'contextlib = other_contextlib\n')
add('decorated-target-class','INCONCLUSIVE',e=errors.replace('class ConnectError(NetworkError):','@transform\nclass ConnectError(NetworkError):'))
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_before_predictions':True,'rows':rows,'scope':'Owned minimal mapping, direct handler and declared cross-file target hierarchy only; real HTTPX source is development-exposed.','source_executed':False,'model_calls':0,'permanent_tests_changed':False,'production_component_changed':False}
with(P/'transport-mapping-control-oracle-v1.json').open('x')as stream:
    stream.write(json.dumps(record,indent=2)+'\n')
print({'controls':len(rows),'inspected_source_execution':False})
