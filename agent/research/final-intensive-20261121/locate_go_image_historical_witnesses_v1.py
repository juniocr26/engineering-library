import json,hashlib,datetime
from pathlib import Path
root=Path(__file__).resolve().parents[3];p=Path(__file__).resolve().parent;needles=['gio-animated-limits-caller','gio-animated-limits-helpers','ValidateAnimatedDimensions'];records=[];scanned=0;bytes_total=0
for f in sorted((root/'agent/research').rglob('*')):
 if not f.is_file() or f.is_symlink() or f.is_relative_to(p) or '__pycache__' in f.parts or f.suffix not in ('.json','.jsonl','.txt','.md','.py','.rb') or f.stat().st_size>12000000:continue
 raw=f.read_bytes()
 try:text=raw.decode('utf-8')
 except UnicodeDecodeError:continue
 scanned+=1;bytes_total+=len(raw);matches={n:[i for i,line in enumerate(text.splitlines(),1) if n in line] for n in needles if n in text}
 if matches:records.append({'path':str(f.relative_to(root)),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'matches':matches,'role_hint':'MODEL_REQUEST_OR_RESPONSE_CANDIDATE' if any(x in f.name.lower() for x in ('request','response','result','protocol')) else 'REFERENCE_OR_METADATA_ONLY_UNADJUDICATED'})
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'needles':needles,'scanned_files':scanned,'scanned_bytes':bytes_total,'records':records,'limits':'Bounded existing text corpus excludes current campaign/archives/large files; match alone does not prove request execution or exact chapter attribution. No private external source bodies acquired.','new_model_calls':0}
with (p/'go-image-historical-witness-locator-results-v1.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({'scanned':scanned,'matched_files':len(records),'candidate_paths':[r['path'] for r in records if r['role_hint']=='MODEL_REQUEST_OR_RESPONSE_CANDIDATE']},indent=2))
