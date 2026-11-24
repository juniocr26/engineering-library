"""Check every preserved root-report preimage and available append receipt, without edits."""
from pathlib import Path
import json,hashlib,datetime
P=Path(__file__).resolve().parent;ROOT=P.parents[2];names=['AI_TRAINING_CAMPAIGN_REPORT.md','AI_TRAINING_FILE_INVENTORY.md','AI_FINE_TUNING_READINESS.md','AI_TRAINING_RESUME.md'];rows=[];receipts=[]
for name in names:
 current=(ROOT/name).read_bytes();snapshots=[P/(name+'.prior.bin')]
 for folder in sorted(P.glob('root-report-preimages-v*'),key=lambda f:int(f.name.rsplit('v',1)[-1])):
  candidates=[folder/name,folder/(name+'.bin')];present=[f for f in candidates if f.is_file()];assert len(present)==1;snapshots.extend(present)
 versions=[]
 for i,f in enumerate(snapshots):
  raw=f.read_bytes();versions.append({'path':str(f.relative_to(ROOT)),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'exact_prefix_of_current':current.startswith(raw),'next_preimage_starts_with_this':snapshots[i+1].read_bytes().startswith(raw) if i+1<len(snapshots) else current.startswith(raw)})
 rows.append({'report':name,'current_sha256':hashlib.sha256(current).hexdigest(),'current_bytes':len(current),'preserved_preimages':versions,'all_prefixes_preserved':all(x['exact_prefix_of_current'] for x in versions),'all_successive_versions_append_only':all(x['next_preimage_starts_with_this'] for x in versions)})
for f in sorted(P.glob('root-report-append-v*.json'),key=lambda f:int(f.stem.rsplit('v',1)[-1])):
 version=int(f.stem.rsplit('v',1)[-1]);data=json.loads(f.read_text())
 for r in data['preimages']:
  before=P/('root-report-preimages-v'+str(version))/r['path'];assert before.is_file();nextfile=P/('root-report-preimages-v'+str(version+1))/r['path'];post=nextfile if nextfile.is_file() else ROOT/r['path'];receipts.append({'receipt':f.name,'report':r['path'],'preimage_hash_matches':hashlib.sha256(before.read_bytes()).hexdigest()==r['pre_sha256'],'post_hash_recorded':'post_sha256' in r,'post_hash_matches_next_preimage_or_current':hashlib.sha256(post.read_bytes()).hexdigest()==r['post_sha256'] if 'post_sha256' in r else None})
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reports':rows,'append_receipt_checks':receipts,'preserved_root_preimages':sum(len(x['preserved_preimages']) for x in rows),'all_historical_bytes_are_current_prefixes':all(x['all_prefixes_preserved'] for x in rows),'all_successive_versions_append_only':all(x['all_successive_versions_append_only'] for x in rows),'available_append_receipt_hash_checks_all_match':all(x['preimage_hash_matches'] and (x['post_hash_matches_next_preimage_or_current'] is not False) for x in receipts),'scope':'Fourcanonicalrootreports andallretainedcurrentcampaignpreimages; historicalpriorcampaignversionsremainseparate. Snapshot.hash/prefixproofnotallreportclaimsemantictruth.','v1_observer_failure':'v1assumedpost_sha256present;v8/v9receiptsrecordonlyprehash. v2marksabsentposthashnull,verifiesallavailablevaluesandseparatebyteprefixchain withoutinventinghistoricalposthashes.','receipt_post_hashes_recorded':sum(x['post_hash_recorded'] for x in receipts),'receipt_pre_hashes_checked':len(receipts),'files_modified':0,'gold':0,'optimizer_updates':0}
with (P/'root-report-history-preservation-audit-v3.json').open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in r.items() if k not in ['reports','append_receipt_checks']},indent=2))
