import datetime,hashlib,json,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent;packet_path=P/'go-catalog-link-paired-candidate-v1.json';packet=json.loads(packet_path.read_text())
program=r'''
import fs from 'node:fs';
import {markdownUnits}from '/app/frontend/lib/markdown.ts';
import {integrateSources}from '/app/frontend/lib/source-references.ts';
import {sourceTarget}from '/app/frontend/lib/source-links.ts';
const packet=JSON.parse(fs.readFileSync(0,'utf8'));const rows=[];
for(const [language,pair]of Object.entries(packet.pairs)){
 const apiLanguage=language==='en'?'en':'pt-BR';const before=await integrateSources(packet.project,pair.document_id,apiLanguage,markdownUnits(pair.before_source));const after=await integrateSources(packet.project,pair.document_id,apiLanguage,markdownUnits(pair.candidate_source));
 const oldRefs=before.flatMap(u=>u.references||[]),newRefs=after.flatMap(u=>u.references||[]);const metadata=newRefs.map(ref=>({id:ref.id,path:ref.path,status:ref.status,fingerprint:ref.fingerprint,line_count:ref.lines?.length||0,sourceKey:ref.sourceKey}));
 const oldTargets=pair.changes.map(c=>sourceTarget(packet.project,pair.document_id,apiLanguage,c.before_href));const newTargets=pair.changes.map(c=>sourceTarget(packet.project,pair.document_id,apiLanguage,c.after_href));
 const expected=new Map(pair.changes.map(c=>[c.source_path,c.source_fingerprint]));const correct=oldRefs.length===0&&newRefs.length===3&&oldTargets.every(x=>x===null)&&newTargets.every(x=>x&&expected.has(x.path))&&metadata.every(ref=>ref.status==='available'&&ref.fingerprint===expected.get(ref.path)&&ref.line_count>0);
 rows.push({language,before_reference_count:oldRefs.length,after_reference_count:newRefs.length,correct,old_targets:oldTargets,new_targets:newTargets,references:metadata});
}
const en=rows.find(r=>r.language==='en'),pt=rows.find(r=>r.language==='pt-br');const same=JSON.stringify(en.references.map(r=>[r.id,r.path,r.fingerprint]))===JSON.stringify(pt.references.map(r=>[r.id,r.path,r.fingerprint]));console.log(JSON.stringify({rows,all_pass:rows.every(r=>r.correct)&&same,paired_canonical_reference_ids_match:same,published_files_written:false,ui_components_changed:false,go_source_executed:false}));
'''
r=subprocess.run(['docker','exec','-i','-w','/app/frontend','engineering-library-frontend-1','node','--experimental-strip-types','--input-type=module','-e',program],input=json.dumps(packet).encode(),capture_output=True,timeout=30)
(P/'go-catalog-link-consumer-v1.stdout').write_bytes(r.stdout);(P/'go-catalog-link-consumer-v1.stderr').write_bytes(r.stderr);record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':r.returncode,'candidate_sha256':hashlib.sha256(packet_path.read_bytes()).hexdigest(),'owner_approved':False,'training_excluded':True,'model_calls':0}
if r.returncode==0:record.update(json.loads(r.stdout))
# Recheck all original docs/catalog/snapshots after actual consumer execution.
for name,expected in {**packet['input_identity_hashes'],**{name:value['sha256']for name,value in packet['source_snapshot_identities'].items()}}.items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==expected
record['all_original_input_hashes_unchanged']=True
with(P/'go-catalog-link-consumer-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
assert r.returncode==0,r.stderr.decode();print({'all_pass':record['all_pass'],'old_available':0,'candidate_available_per_language':3,'paired_ids_equal':record['paired_canonical_reference_ids_match'],'published':False})
