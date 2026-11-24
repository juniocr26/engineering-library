"""Freeze selected adapter/model implementation paths; no framework install or model download."""
import datetime,hashlib,json,urllib.request
from pathlib import Path
P=Path(__file__).resolve().parent;revision='2d4df8d94a80c0f9f8794e54fafee08728b04fc6';url='https://api.github.com/repos/ml-explore/mlx-lm/git/trees/'+revision+'?recursive=1'
with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EngineeringLibrarySourceResearch/1.0'}),timeout=35)as response:raw=response.read(1048577)
assert len(raw)<=1048576;tree=json.loads(raw);assert tree['truncated']is False
with(P/'mlx-lm-pinned-adapter-tree-v1.json').open('xb')as f:f.write(raw)
paths=['mlx_lm/tuner/utils.py','mlx_lm/tuner/lora.py','mlx_lm/models/llama.py','LICENSE'];entries=[e for e in tree['tree']if e['path']in paths];assert len(entries)==len(paths)and all(e['type']=='blob'and e['mode']=='100644'and e['size']<=131072 for e in entries)
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository':'ml-explore/mlx-lm','revision':revision,'tree_sha256':hashlib.sha256(raw).hexdigest(),'selected_blobs':entries,'hypothesis':'Pinned default LoRA module selection,adapter matrix shapes and Llama configuration may permit exact element-count arithmetic for the future two-layer/rank4 proposal. This cannot measure activation/allocator/optimizer memory or certify an unacquired trainable checkpoint.','source_bodies_fetched_in_this_supplement':False,'source_execution_allowed':False,'framework_installed':False,'weights_or_tokenizer_downloads_allowed':False,'training_steps':0,'owner_approved':False,'training_excluded':True}
with(P/'mlx-adapter-source-scope-freeze-v1.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'selected_public_source_files':len(entries),'weights_requested':False})
