import json,hashlib,datetime
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[2]
needles=['HeaderValuesContainsToken','ValidHeaderFieldName','ValidHeaderFieldValue','ValidHostHeader','PunycodeHostPort','IsTokenRune','ValidTrailerHeader','headerValueContainsToken','tokenEqual','trimOWS']
records=[];count=0;size=0
for f in sorted((root/'agent/research').rglob('*')):
 if not f.is_file() or f.is_symlink() or '__pycache__' in f.parts or f.suffix not in {'.json','.jsonl','.md','.txt','.py','.rb','.go','.js','.mjs','.cjs','.ts','.tsx'} or f.stat().st_size>12000000:continue
 if f.is_relative_to(p) and any(('httpguts' in s or s.startswith('go-vendored-httpguts-')) for s in f.relative_to(p).parts):continue
 b=f.read_bytes()
 try:t=b.decode()
 except UnicodeDecodeError:continue
 count+=1;size+=len(b);matches={n:[i for i,line in enumerate(t.splitlines(),1) if n in line] for n in needles if n in t}
 if matches:records.append({'path':str(f.relative_to(root)),'sha256':hashlib.sha256(b).hexdigest(),'matches':matches})
x={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'extends':'go-vendored-httpguts-exposure-results-v1.json','needles':needles,'scanned_files':count,'scanned_bytes':size,'records':records,'scope':'Existing research UTF8 text files ≤12MB; excludes new candidate-family artifacts and own audit. No archive/external/model-pretraining coverage. Identifier hits require context adjudication, not automatic source exposure.','independence_certified':False,'training_eligible':False,'model_calls':0}
with (p/'go-vendored-httpguts-api-exposure-results-v1.json').open('x') as f:json.dump(x,f,indent=2);f.write('\n')
print(json.dumps({'files':count,'matches':len(records),'records':records},indent=2)[:16000])
