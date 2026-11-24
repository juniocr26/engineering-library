"""Freeze the source dependency closure before fetching selected class bodies."""
import datetime
import hashlib
import json
from pathlib import Path
import urllib.request

P=Path(__file__).resolve().parent
repo='encode/httpcore';tag='1.0.9'

def get(url,limit):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EngineeringLibrarySourceResearch/1.0'}),timeout=35)as response:raw=response.read(limit+1)
 if len(raw)>limit:raise ValueError('public metadata size bound')
 return raw

url='https://api.github.com/repos/'+repo+'/git/ref/tags/'+tag
raw=get(url,65536)
with(P/'httpcore-1.0.9-ref-v1.json').open('xb')as f:f.write(raw)
obj=json.loads(raw)['object']
if obj['type']=='tag':
 raw=get(obj['url'],65536)
 with(P/'httpcore-1.0.9-tag-v1.json').open('xb')as f:f.write(raw)
 obj=json.loads(raw)['object']
assert obj['type']=='commit'
revision=obj['sha'];url='https://api.github.com/repos/'+repo+'/git/trees/'+revision+'?recursive=1';raw=get(url,1048576);tree=json.loads(raw);assert tree['truncated']is False
with(P/'httpcore-1.0.9-tree-v1.json').open('xb')as f:f.write(raw)
paths={'httpcore/__init__.py','httpcore/_exceptions.py','pyproject.toml','LICENSE.md'}
entries=[e for e in tree['tree']if e['type']=='blob'and e['path']in paths];assert len(entries)==4
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository':repo,'tag':tag,'revision':revision,'tree_sha256':hashlib.sha256(raw).hexdigest(),'selected_blobs':entries,'target_bodies_fetched':False,'reason':'HTTPXsource explicitly depends onhttpcore1.* and uses14qualifiedclassreferences. Inspect the pure exception definitions and package reexport statements before claiming a source dependency closure.','not_an_installed_dependency_version_assertion':True,'related_dependency_of_already_exposed_httpx':True,'certified_neural_holdout':False,'training_excluded':True,'source_execution_allowed_at_this_metadata_stage':False,'packages_installed':False,'http_application_requests':0,'model_calls':0}
with(P/'httpcore-dependency-freeze-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'revision':revision,'blobs':len(entries),'source_bodies_fetched':False})
