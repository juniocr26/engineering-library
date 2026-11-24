"""Read-only diagnosis of existing catalog inputs; no private application data."""
import datetime,hashlib,json,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent
program=r'''
import fs from 'node:fs';import crypto from 'node:crypto';import path from 'node:path';
import {documentationEntries,documentationSource}from '/app/frontend/lib/documentation.ts';
import {markdownUnits}from '/app/frontend/lib/markdown.ts';
import {integrateSources}from '/app/frontend/lib/source-references.ts';
import {sourceTarget}from '/app/frontend/lib/source-links.ts';
const project='go-image-optimizer';const root=process.env.DOCUMENTATION_ROOT;const catalog=JSON.parse(fs.readFileSync(root+'/'+project+'/en/links/catalog.json','utf8'));const rows=[];
for(const entry of(await documentationEntries(project,'en')).filter(e=>e.href&&!e.documentId)){
 const text=await documentationSource(project,entry.id,'en');const units=markdownUnits(text);const integrated=await integrateSources(project,entry.id,'en',units);const refs=integrated.flatMap(u=>u.references||[]);const counts={};for(const ref of refs)counts[ref.status]=(counts[ref.status]||0)+1;
 const sample=refs.slice(0,3).map(r=>({path:r.path,revision:r.revision,status:r.status,catalog_revision:catalog.files[r.path]?.revision,catalog_sha256:catalog.files[r.path]?.sha256}));
 rows.push({document:entry.id,link_count:units.flatMap(u=>u.links||[]).length,reference_count:refs.length,status_counts:counts,sample});
}
const snapshots=Object.entries(catalog.files).filter(([name,r])=>r.status==='available').map(([name,r])=>{const p=root+'/'+project+'/en/links/'+r.snapshot;let raw;try{raw=fs.readFileSync(p)}catch{return {path:name,snapshot:r.snapshot,missing:true}}return {path:name,snapshot:r.snapshot,bytes:raw.length,hash_matches:crypto.createHash('sha256').update(raw).digest('hex')===r.sha256}});
console.log(JSON.stringify({documentationRoot:root,project,rows,snapshots,private_application_data_read:false,published_files_changed:false}));
'''
r=subprocess.run(['docker','exec','-w','/app/frontend','engineering-library-frontend-1','node','--experimental-strip-types','--input-type=module','-e',program],capture_output=True,text=True,timeout=40)
(P/'frontend-catalog-input-diagnosis-v1.stdout').write_text(r.stdout);(P/'frontend-catalog-input-diagnosis-v1.stderr').write_text(r.stderr);record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':r.returncode}
if r.returncode==0:record.update(json.loads(r.stdout))
with(P/'frontend-catalog-input-diagnosis-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
assert r.returncode==0,r.stderr;counts={}
for row in record['rows']:
 for key,value in row['status_counts'].items():counts[key]=counts.get(key,0)+value
print({'documents':len(record['rows']),'reference_status_counts':counts,'available_catalog_snapshots':len(record['snapshots']),'missing_snapshots':sum(r.get('missing',False)for r in record['snapshots']),'wrong_snapshot_hashes':sum(r.get('hash_matches')is False for r in record['snapshots'])})
