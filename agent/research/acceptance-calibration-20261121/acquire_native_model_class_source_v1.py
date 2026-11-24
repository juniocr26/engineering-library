"""Pinned public framework source only; never import or execute fetched code."""
from pathlib import Path
import urllib.request,json,hashlib,datetime
P=Path(__file__).resolve().parent;revision='1bf8da05a1ef30a3eb2e8a634180be6557fd3ca0';paths=['mlx_lm/models/llama.py','mlx_lm/tokenizer_utils.py','mlx_lm/LORA.md'];out=P/'native-framework-model-class-source-v1';out.mkdir(exist_ok=False);records=[]
for name in paths:
 url='https://raw.githubusercontent.com/ml-explore/mlx-lm/'+revision+'/'+name
 with urllib.request.urlopen(url,timeout=45) as response:raw=response.read(1000001);assert len(raw)<=1000000
 f=out/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(raw);records.append({'path':name,'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
(P/'native-framework-model-class-source-freeze-v1.json').write_text(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'revision':revision,'files':records,'fetched_source_imported_or_executed':False,'weight_downloads':0,'optimizer_updates':0},indent=2)+'\n');print(json.dumps(records,indent=2))
