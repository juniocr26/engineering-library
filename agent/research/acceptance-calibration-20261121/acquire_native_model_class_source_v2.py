"""Pinned public framework source only; never import or execute fetched code."""
from pathlib import Path
import urllib.request,json,hashlib,datetime
P=Path(__file__).resolve().parent;revision='1bf8da05a1ef30a3eb2e8a634180be6557fd3ca0';paths=['mlx_lm/models/llama/__init__.py','mlx_lm/models/llama/config.py','mlx_lm/models/llama/layers.py','mlx_lm/models/llama/model.py','mlx_lm/models/llama/checkpoint.py','mlx_lm/tokenizer_utils.py','mlx_lm/LORA.md'];out=P/'native-framework-model-class-source-v2';out.mkdir(exist_ok=False);records=[]
for name in paths:
 url='https://raw.githubusercontent.com/ml-explore/mlx-lm/'+revision+'/'+name
 with urllib.request.urlopen(url,timeout=45) as response:raw=response.read(1000001);assert len(raw)<=1000000
 tree=json.loads((P/'native-framework-pinned-tree-v1.json').read_text());entry=next(e for e in tree['tree'] if e['path']==name);assert hashlib.sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest()==entry['sha'];f=out/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(raw);records.append({'path':name,'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
(P/'native-framework-model-class-source-freeze-v2.json').write_text(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'revision':revision,'files':records,'fetched_source_imported_or_executed':False,'weight_downloads':0,'optimizer_updates':0},indent=2)+'\n');print(json.dumps(records,indent=2))
