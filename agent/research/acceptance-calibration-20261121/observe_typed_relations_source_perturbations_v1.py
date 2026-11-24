"""Owned source-text perturbation observations; frozen existing parsers, no program execution."""
from pathlib import Path
import json,subprocess,hashlib,datetime
P=Path(__file__).resolve().parent;protocol_path=P/'typed-relations-source-perturbation-protocol-v2.json';r=json.loads(protocol_path.read_text())
for f in r['observer_files']:assert hashlib.sha256(Path(f['path']).read_bytes()).hexdigest()==f['sha256']
rows=[]
for c in r['cases']:
 src=Path(c['path']);data=src.read_bytes();assert hashlib.sha256(data).hexdigest()==c['sha256'];folder=src.parent;stem=c['id'].replace(':','-');receipt=folder/(stem+'-observation-v1.json');assert not receipt.exists()
 if c['task']=='cobra':cmd=[str((P/'cobra-typed-relations-observer-v1').resolve()),str(src.resolve())];stdin=None
 else:cmd=['/usr/local/bin/docker','exec','-i','-w','/app/frontend','engineering-library-frontend-1','node','-e',(P/'observe_zod_typed_relations_v1.cjs').read_text()];stdin=data
 observed=subprocess.run(cmd,input=stdin,capture_output=True,timeout=25);rawpath=folder/(stem+'-stdout-v1.json');errpath=folder/(stem+'-stderr-v1.txt')
 with rawpath.open('xb') as f:f.write(observed.stdout)
 with errpath.open('xb') as f:f.write(observed.stderr)
 extracted=None;comparison=None
 if observed.returncode==0:
  body=json.loads(observed.stdout);assert body['source_sha256']==c['sha256'];extracted={x['id']:x for x in body['relations']}
  expected=c['expected_changed_relation'];comparison=extracted.get(expected['id'],{}).get('normalized_relation')==expected['normalized_relation'] if expected else False
 matched=(observed.returncode!=0) if c['expected_observer_refusal'] else (observed.returncode==0 and comparison)
 row={'id':c['id'],'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':observed.returncode,'source_sha256':c['sha256'],'expected_refusal':c['expected_observer_refusal'],'expected_relation':c['expected_changed_relation'],'observed_relation':extracted.get(c['expected_changed_relation']['id']) if extracted and c['expected_changed_relation'] else None,'matches_frozen_reference':matched,'original_pinned_source_hash_gate_accepts':c['sha256']==c['original_source_sha256'],'stdout_sha256':hashlib.sha256(observed.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(observed.stderr).hexdigest(),'source_program_executed':False}
 with receipt.open('x') as f:json.dump(row,f,indent=2);f.write('\n')
 rows.append(row);print(json.dumps({'id':c['id'],'exit_code':observed.returncode,'matches':matched}),flush=True)
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':protocol_path.name,'protocol_sha256':hashlib.sha256(protocol_path.read_bytes()).hexdigest(),'records':rows,'cases':len(rows),'matches':sum(x['matches_frozen_reference'] for x in rows),'expected_refusals':sum(x['expected_refusal'] for x in rows),'original_hash_gate_rejections':sum(not x['original_pinned_source_hash_gate_accepts'] for x in rows),'no_source_program_execution_or_typecheck':True,'scope':'24owned source perturbations, including4neighbor-owner isolation controls, over2development-exposed upstream snapshots. Source changes and physical owner corrections frozen before predictions; finite AST profile only. No neural calls or complete-document outcomes.','gold':0,'optimizer_updates':0}
with (P/'typed-relations-source-perturbation-results-v1.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'cases':len(rows),'matches':result['matches'],'expected_refusals':result['expected_refusals'],'original_hash_gate_rejections':result['original_hash_gate_rejections']}))
