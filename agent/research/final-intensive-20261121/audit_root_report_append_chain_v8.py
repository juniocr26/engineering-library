"""Audit report history as byte prefixes and receipt edges; never rewrite reports."""
from pathlib import Path
import argparse,datetime,hashlib,json,tarfile
parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3]);args=parser.parse_args();ROOT=args.root.resolve();P=ROOT/'agent/research/final-intensive-20261121';sha=lambda b:hashlib.sha256(b).hexdigest();names=['AI_TRAINING_CAMPAIGN_REPORT.md','AI_TRAINING_FILE_INVENTORY.md','AI_FINE_TUNING_READINESS.md','AI_TRAINING_RESUME.md']
protocol={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hypothesis':'Recovered roots, every preserved campaign preimage and checkpoint report copy are byte prefixes of current canonical reports; append receipts bind available before/after prefix states.','reports':names,'scope':'Local byte lineage and append-only preservation. Does not prove semantic correctness, approved publication, remote/crash backup or immutable human signatures.','extends':'root-report-chain-audit-results-v5.json; v8 refreshes through progress076/checkpoint053, includes canonical late-note bundle and exactCP040extra-sidecar reconstruction; failed031 is byte-history only; no live archives treated as complete','missing_policy':'Unresolved receipt states remain INCONCLUSIVE, never infer bytes merely from matching metadata labels.','corpus_refinement':'Canonical recovered files, named root-preimages directories, actual-root report-bundle preimages and checkpoint report entries. Synthetic owned control report copies remain excluded by declared provenance, never treated as actual report history.'}
with (P/'root-report-chain-audit-protocol-v8.json').open('x') as f:json.dump(protocol,f,indent=2);f.write('\n')
current={name:(ROOT/name).read_bytes() for name in names};nodes={name:{} for name in names};failures=[]
def add(name,raw,location):
 ident=sha(raw);entry=nodes[name].setdefault(ident,{'sha256':ident,'bytes':len(raw),'locations':[],'prefix_of_current':current[name].startswith(raw)});entry['locations'].append(location)
 if not entry['prefix_of_current']:failures.append({'report':name,'location':location,'type':'PRESERVED_STATE_NOT_PREFIX'})
for name in names:
 add(name,current[name],str(ROOT/name))
 for f in sorted(P.rglob('*')):
  if not f.is_file() or f.is_symlink():continue
  rel=f.relative_to(P)
  recovered=len(rel.parts)==1 and f.name==name+'.recovered.bin'
  legacy=rel.parts[0].startswith('root-preimages-') and f.name in [name,name+'.bin']
  bundle=rel.parts[0].startswith('root-report-bundle-') and f.name==name+'.before.bin'
  if bundle:
   plan_path=P/rel.parts[0]/'plan.json'
   bundle=plan_path.is_file() and json.loads(plan_path.read_text()).get('original_root')==str(ROOT)
   if rel.parts[0].startswith('root-report-bundle-progress-'):assert bundle
  if recovered or legacy or bundle:add(name,f.read_bytes(),str(f.relative_to(ROOT)))
backup=ROOT/'.local-backups/final-intensive-20261121'
for archive in sorted(backup.glob('checkpoint-*/research-reports-and-selected-dependencies.tar.gz')):
 if not (archive.parent/'receipt.json').is_file() and archive.parent.name!='checkpoint-031':continue
 with tarfile.open(archive,'r:gz') as tar:
  for name in names:
   member=tar.getmember(name);assert member.isfile();add(name,tar.extractfile(member).read(),str(archive.relative_to(ROOT))+'::'+name)
receipts=[]
for f in sorted(P.glob('root-report-*.json')):
 if f.name.startswith(('root-report-append-cut-','root-report-append-receipt-','root-report-checkpoint-')):
  d=json.loads(f.read_text())
  if isinstance(d.get('reports'),list):receipts.append((f,d))
# Later write-ahead bundles use an outcome envelope rather than the legacy reports list.
# Bind exact before+payload bytes and successful durable attempt hashes; do not omit these edges.
for folder in sorted(P.glob('root-report-bundle-*')):
 plan_path=folder/'plan.json'
 if not folder.is_dir() or not plan_path.is_file():continue
 plan=json.loads(plan_path.read_text())
 if plan.get('original_root')!=str(ROOT):
  assert not folder.name.startswith('root-report-bundle-progress-');continue
 successful=[]
 for attempt in sorted(folder.glob('attempt-*.json')):
  outcome=json.loads(attempt.read_text())
  if outcome['status']=='APPLIED_OR_ALREADY_APPLIED':
   assert outcome['plan_sha256']==sha(plan_path.read_bytes())
   assert {r['path'] for r in outcome['reports']}==set(names)
   successful.append(outcome)
 if not successful:
  failures.append({'location':str(folder.relative_to(ROOT)),'type':'NO_SUCCESSFUL_CANONICAL_BUNDLE_ATTEMPT'});continue
 for edge in plan['reports']:
  name=edge['path'];before=(folder/(name+'.before.bin')).read_bytes();payload=(folder/(name+'.append.bin')).read_bytes();after=before+payload
  assert sha(before)==edge['before_sha256'] and sha(payload)==edge['payload_sha256'] and sha(after)==edge['after_sha256']
  assert all(next(r for r in attempt['reports'] if r['path']==name)['final_sha256']==edge['after_sha256'] for attempt in successful)
  add(name,after,str(plan_path.relative_to(ROOT))+'::bound-before-plus-payload')
 receipts.append((plan_path,plan))
# Independently rebuild note edges from actual archived prefixes when their preimage is available.
for f,d in receipts:
 note=d.get('note_utf8')
 if note is not None:
  assert sha(note.encode())==d['note_sha256']
  for edge in d['reports']:
   name=edge['path'];before=nodes[name].get(edge['before_sha256'])
   if before:
    raw=current[name][:before['bytes']]+note.encode();assert sha(raw)==edge['after_sha256'];add(name,raw,str(f.relative_to(ROOT))+'::derived-postnote')
rows=[]
for f,d in receipts:
 for edge in d['reports']:
  name=edge['path'];before=nodes[name].get(edge['before_sha256']);after=nodes[name].get(edge['after_sha256']);resolved=before is not None and after is not None
  row={'receipt':str(f.relative_to(ROOT)),'report':name,'before_sha256':edge['before_sha256'],'after_sha256':edge['after_sha256'],'before_available':before is not None,'after_available':after is not None,'status':'INCONCLUSIVE_MISSING_PREFIX_STATE'}
  if resolved:
   assert before['bytes']<=after['bytes'];assert sha(current[name][:before['bytes']])==edge['before_sha256'];assert sha(current[name][:after['bytes']])==edge['after_sha256'];row.update(status='VERIFIED_APPEND_EDGE',appended_bytes=after['bytes']-before['bytes'])
  rows.append(row)
# CP040 requires the explicitly preserved late append closure, not archive+receipt alone.
late_path=P/'root-report-checkpoint-040-postnote-v1.json';late=json.loads(late_path.read_text());sidecars=late['late_append_sidecar']
for item in sidecars:assert sha((ROOT/item['path']).read_bytes())==item['sha256']
plan_item=next(item for item in sidecars if item['path'].endswith('/plan.json'));late_plan_path=ROOT/plan_item['path'];late_plan=json.loads(late_plan_path.read_text());assert sha(late_plan_path.read_bytes())==late['late_plan_sha256']
producer=P/'append_checkpoint040_late_bundle_note_v2.py';assert sha(producer.read_bytes())==late['supplemental_producer_sha256']
cp040=backup/'checkpoint-040';assert sha((P/'checkpoint-040.json').read_bytes())==late['source_receipt_sha256'];bound=[]
with tarfile.open(cp040/'research-reports-and-selected-dependencies.tar.gz','r:gz') as tar:
 script=tar.extractfile('agent/research/final-intensive-20261121/append_checkpoint_report_note_v22.py').read();assert sha(script)==late['archived_script_sha256']
 for name in names:
  prefix=tar.extractfile(name).read();before=(late_plan_path.parent/(name+'.before.bin')).read_bytes();payload=(late_plan_path.parent/(name+'.append.bin')).read_bytes();assert prefix==before
  edge=next(e for e in late_plan['reports'] if e['path']==name);assert sha(prefix)==edge['before_sha256'] and sha(payload)==edge['payload_sha256'] and sha(prefix+payload)==edge['after_sha256']
  final=prefix+payload+late['note_utf8'].encode();receipt_edge=next(e for e in late['reports'] if e['path']==name);assert sha(prefix+payload)==receipt_edge['before_sha256'] and sha(final)==receipt_edge['after_sha256'] and current[name].startswith(final)
  bound.append({'report':name,'archived_prefix_sha256':sha(prefix),'after_late_payload_sha256':sha(prefix+payload),'after_note_sha256':sha(final)})
assert all((ROOT/name).read_bytes()==raw for name,raw in current.items())
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':sha((P/'root-report-chain-audit-protocol-v8.json').read_bytes()),'report_states':{n:sorted(v.values(),key=lambda x:x['bytes']) for n,v in nodes.items()},'current_report_hashes':{n:sha(raw) for n,raw in current.items()},'receipt_edges':rows,'receipt_edge_count':len(rows),'resolved_append_edges':sum(r['status']=='VERIFIED_APPEND_EDGE' for r in rows),'unresolved_edges':[r for r in rows if r['status']!='VERIFIED_APPEND_EDGE'],'preserved_nonprefix_failures':failures,'all_preserved_states_prefix':not failures,'all_receipt_edges_resolved':all(r['status']=='VERIFIED_APPEND_EDGE' for r in rows),'checkpoint040_extra_sidecar_closure':{'sidecar_files_verified':len(sidecars),'report_reconstructions':bound,'archive_plus_receipt_alone_sufficient':False},'unique_before_after_report_edges':len({(r['report'],r['before_sha256'],r['after_sha256']) for r in rows}),'receipt_edge_count_is_not_unique_append_event_count':True,'semantic_acceptance_inferred':False,'new_model_calls':0,'reports_modified':False}
with (P/'root-report-chain-audit-results-v8.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['report_states','receipt_edges','current_report_hashes']}))
