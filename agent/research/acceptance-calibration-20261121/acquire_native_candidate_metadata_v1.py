"""Read public model metadata only. Weight/tensor/tokenizer-model downloads forbidden."""
import datetime,hashlib,json,urllib.request
from pathlib import Path
P=Path(__file__).resolve().parent;out=P/'native-candidate-metadata-v1';out.mkdir(exist_ok=False)
repo='mlx-community/Llama-3.2-3B-Instruct-4bit';api='https://huggingface.co/api/models/'+repo

def get(url,limit):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EngineeringLibrary-authorized-readonly-research'}),timeout=45) as response:
  raw=response.read(limit+1);assert len(raw)<=limit,'Metadata byte cap exceeded'
  return raw,response.geturl(),dict(response.headers)
raw,url,headers=get(api,2000000);(out/'model-api.json').write_bytes(raw);metadata=json.loads(raw);revision=metadata['sha'];assert len(revision)==40
allowed=['config.json','tokenizer_config.json','special_tokens_map.json','model.safetensors.index.json','README.md','LICENSE','USE_POLICY.md']
listed={s['rfilename'] for s in metadata.get('siblings',[])};records=[]
for name in allowed:
 if name not in listed:records.append({'file':name,'state':'NOT_LISTED_NOT_FETCHED'});continue
 assert not name.endswith(('.safetensors','.bin','.gguf','.pt','.model')) and name!='tokenizer.json'
 endpoint='https://huggingface.co/'+repo+'/resolve/'+revision+'/'+name
 body,final,h=get(endpoint,1500000);(out/name).write_bytes(body);records.append({'file':name,'url':endpoint,'resolved_url':final,'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body),'etag':h.get('ETag'),'state':'PUBLIC_TEXT_METADATA_ONLY'})
receipt={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repo':repo,'revision':revision,'api_url':api,'api_sha256':hashlib.sha256(raw).hexdigest(),'files':records,'weight_files_downloaded':0,'tokenizer_model_files_downloaded':0,'framework_installed':False,'no_native_load_or_training':True,'candidate_not_selected_or_approved':True,'rights_not_cleared':True,'owner_gold':0,'optimizer_updates':0}
(P/'native-candidate-metadata-freeze-v1.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
