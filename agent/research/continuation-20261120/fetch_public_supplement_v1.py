import importlib.util,json,datetime
from pathlib import Path
p=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('fetcher',p/'fetch_public_sources_v1.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
items=[('lukeed/totalist',v,'src/async.js') for v in ['193f6476c04804dba24f02a6e1fa0f509b205be9','4b071d3e54d466a4059de89006c752da782c8b02']]+[('jmespath/jmespath.py','6ff419a8b171d055a9bfc6904605bceb8b7a80ef','LICENSE')]
rows=[m.fetch(x)for x in items]
with (p/'new-public-source-provenance-supplement-v1.json').open('x')as f:json.dump({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'path_reason':'Totalist package modes names src/async.js; JMESPath license extension changed, checked alternative once.','rows':rows},f,indent=2)
print(json.dumps(rows))
