"""Public source-only supplement; verify Git identities, never import implementation."""
import datetime,hashlib,json,urllib.request
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];freeze=json.loads((P/'mlx-adapter-source-scope-freeze-v2.json').read_text());revision=freeze['revision'];rows=[]
for entry in freeze['selected_blobs']:
 url='https://raw.githubusercontent.com/ml-explore/mlx-lm/'+revision+'/'+entry['path']
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EngineeringLibrarySourceResearch/1.0'}),timeout=35)as response:raw=response.read(131073)
 assert len(raw)<=131072 and len(raw)==entry['size']and hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==entry['sha'];file=P/'new-public-sources-v1/ml-explore--mlx-lm'/revision/entry['path'];file.parent.mkdir(parents=True,exist_ok=True)
 with file.open('xb')as f:f.write(raw)
 rows.append({'path':str(file.relative_to(P)),'upstream_path':entry['path'],'revision':revision,'git_blob':entry['sha'],'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
# Existing four source-review files are checked against the same immutable tree, without rewriting them.
tree=json.loads((P/'mlx-lm-pinned-adapter-tree-v1.json').read_text());tree_files={e['path']:e for e in tree['tree']if e['type']=='blob'};old=ROOT/'agent/research/documentation-intelligence-20261120/readiness-primary-sources/mlx-lm';existing=[]
for f in sorted(old.rglob('*')):
 if not f.is_file():continue
 name=str(f.relative_to(old));raw=f.read_bytes();entry=tree_files[name];ok=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==entry['sha'];existing.append({'path':str(f.relative_to(ROOT)),'git_blob':entry['sha'],'matches':ok});assert ok
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':rows,'existing_four_files_git_blob_checks':existing,'all_git_blobs_verified':True,'source_executed':False,'framework_imported':False,'weights_or_tokenizer_requested':False,'packages_installed':False,'training_steps':0,'owner_approved':False,'training_excluded':True}
with(P/'mlx-adapter-source-fetch-v1.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'new_source_files':len(rows),'existing_source_files_reverified':len(existing),'bytes':sum(e['bytes']for e in rows)})
