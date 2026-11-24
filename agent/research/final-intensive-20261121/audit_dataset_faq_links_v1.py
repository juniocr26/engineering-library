import json,hashlib,re,datetime,collections
from pathlib import Path
from urllib.parse import urlsplit,unquote
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sha=lambda b:hashlib.sha256(b).hexdigest();a=json.loads((P/'dataset-faq-row-level-preflight-v1.json').read_bytes());rows=[]
for e in a['allowed_rows']:
 raw=(ROOT/e['file']).read_bytes().splitlines()[e['line']-1];assert sha(raw)==e['row_sha256'];r=json.loads(raw)
 for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',r['answer']):
  parsed=urlsplit(target);row={'id':e['id'],'target':target,'document_original_path':r['document_ref']['original_path'],'row_sha256':e['row_sha256']}
  if parsed.scheme in ['http','https']:
   row.update(kind='EXTERNAL_PRIMARY_REFERENCE_NOT_FETCHED_NOW',current_web_verification=False)
  elif not parsed.scheme and parsed.path:
   f=((ROOT/r['document_ref']['original_path']).parent/unquote(parsed.path)).resolve();inside=f.is_relative_to(ROOT)
   row.update(kind='RELATIVE_REQUIRES_ORIGINAL_DOCUMENT_BASE',resolved_inside_repository=inside,resolved_path=str(f.relative_to(ROOT)) if inside else None)
   if inside and f.is_file() and not f.is_symlink():
    row.update(current_destination_exists=True,current_destination_sha256=sha(f.read_bytes()),current_destination_is_json=f.suffix=='.json')
   else:row.update(current_destination_exists=False)
   row['destination_identity_bound_by_link_itself']=False;row['snapshot_based_consumer_can_assume_current_destination_bytes']=False
  else:row.update(kind='OTHER_OR_FRAGMENT_REQUIRES_REVIEW')
  rows.append(row)
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'role':'STATIC_FAQ_LINK_CONTEXT_AND_DESTINATION_OBSERVATION_NO_NETWORK_OR_AUTOMATIC_TARGET_APPROVAL','rows':rows,'counts':dict(collections.Counter(r['kind'] for r in rows)),'missing_relative_destinations':sum(r.get('current_destination_exists') is False for r in rows),'limitation':'Simple Markdown inline-link enumeration, not a full Markdown parser or a citation-entailment checker. Existing destination bytes are current observations, not proof of the dated destination version at dataset creation. Hash-pinned answer text does not bind linked bytes. No private row decoded, file modified, external URL fetched or model invoked.','training_eligible':False}
with (P/'dataset-faq-links-results-v1.json').open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in out.items() if k!='rows'},ensure_ascii=False))
