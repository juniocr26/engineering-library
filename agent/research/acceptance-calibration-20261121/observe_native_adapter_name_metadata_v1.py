"""Owned JSON-only projection of frozen adapter-name source logic; no native imports."""
import datetime,hashlib,json,re
from pathlib import Path
P=Path(__file__).resolve().parent
protocol_path=P/'native-adapter-name-metadata-protocol-v1.json'
r=json.loads(protocol_path.read_text())
assert hashlib.sha256(Path(r['source']).read_bytes()).hexdigest()==r['source_sha256']
def place(name):
 m=re.search(r'(?:^|\.)layers\.(\d+)\.(.+)$',name)
 return (int(m.group(1)),m.group(2)) if m else None
def project(case):
 allowed=case['allowed_shape_metadata']; original={w['name']:w for w in case['ordered_input']}; byplace={}
 for name in allowed:
  loc=place(name)
  if loc is not None:byplace.setdefault(loc,[]).append(name)
 matched={};events=[]
 for old,w in original.items():
  name=old;loc=place(name)
  assert loc is not None,'non-layer layout helper deliberately outside projection'
  if name not in allowed:
   candidates=byplace.get(loc,[])
   if len(candidates)==1 and candidates[0] not in original:name=candidates[0]
  events.append({'original':old,'mapped':name,'overwrites_prior':name in matched,'retained_label':w['inert_payload_label']})
  matched[name]=w
 errors=[]
 for name,w in matched.items():
  if name not in allowed:errors.append({'name':name,'error':'unknown_parameter'})
  elif w['shape']!=allowed[name]:errors.append({'name':name,'error':'shape_mismatch'})
 return {'id':case['id'],'ordered_mapping_events':events,'retained_metadata':matched,'projected_provided_key_validation_errors':errors,'missing_allowed_keys_not_checked_by_source':sorted(set(allowed)-set(matched)),'source_projected_accepts_provided_metadata':not errors,'preregistered_source_projection':case['preregistered_source_projection']}
rows=[project(c) for c in r['cases']]
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':hashlib.sha256(protocol_path.read_bytes()).hexdigest(),'observer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'observations':rows,'interpretation':'Two distinct legacy prefixes with the same layer/place map onto one current key; dictionary assignment silently retains the later metadata label. Same-shaped duplicates pass the subsequent provided-key/shape loop in this source projection. The loop also does not require every allowed key. This is a static source-derived metadata risk, not a native MLX adapter-load observation.','exact_version_limit':r['version_limit'],'native_packages_imported':0,'upstream_code_executed':0,'tensors_or_adapter_files_created':0,'optimizer_updates':0,'gold':0}
with (P/'native-adapter-name-metadata-results-v1.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps([{'id':x['id'],'accepts_provided_metadata':x['source_projected_accepts_provided_metadata'],'mapped_entries':len(x['retained_metadata']),'overwrites':sum(e['overwrites_prior'] for e in x['ordered_mapping_events'])} for x in rows],indent=2))
