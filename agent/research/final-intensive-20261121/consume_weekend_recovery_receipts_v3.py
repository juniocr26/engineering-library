import argparse,json,hashlib,base64,tarfile,ast
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True,type=Path);ROOT=ap.parse_args().root.resolve();P=ROOT/'agent/research/final-intensive-20261121';sha=lambda b:hashlib.sha256(b).hexdigest()
for e in json.loads((P/'remaining-chapters-recovery-dependencies-v41.json').read_bytes())['dependencies']:assert sha((ROOT/e['path']).read_bytes())==e['sha256']
recipe=json.loads((P/'weekend-capsule-exact-recipe-v2.json').read_bytes());assert sha((P/'consume_weekend_capsule_v2.py').read_bytes())==recipe['consumer_sha256'];proof=json.loads((P/'weekend-capsule-consumption-results-v2.json').read_bytes());assert proof['status']=='PASS_EXISTING_CAPSULE_STANDALONE_RECOVERY' and proof['regular_files_restored_and_hash_verified']==5710 and proof['exact_postnote_reports_reconstructed']==4 and len(proof['consumers'])==4
for c in proof['consumers']:
 assert c['status']=='EXIT_ZERO' and c['exit_code']==0
 for stream in ['stdout','stderr']:
  raw=base64.b64decode(c[stream+'_base64']);assert sha(raw)==c[stream+'_sha256'] and len(raw)==c[stream+'_bytes'] and raw.decode('utf-8',errors='replace')==c[stream]
inputs=proof['inputs'];archive=ROOT/inputs['archive'];mf=ROOT/inputs['manifest'];receipt=ROOT/inputs['receipt'];post=ROOT/inputs['postnote'];assert sha(archive.read_bytes())==inputs['archive_sha256'] and sha(mf.read_bytes())==inputs['manifest_sha256'] and sha(receipt.read_bytes())==inputs['receipt_sha256'] and sha(post.read_bytes())==inputs['postnote_sha256'];note=json.loads(post.read_bytes());manifest={x['path']:x for x in json.loads(mf.read_bytes())}
with tarfile.open(archive,'r:gz') as tar:
 for e in note['reports']:
  raw=tar.extractfile(e['path']).read();assert sha(raw)==e['before_sha256'] and sha(raw+note['note_utf8'].encode())==e['after_sha256']
summary=json.loads((P/'weekend-capsule-restored-file-inventory-summary-v3.json').read_bytes());stream=P/Path(summary['record_stream']).name;assert sha(stream.read_bytes())==summary['record_stream_sha256'];rows=[json.loads(x) for x in stream.read_bytes().splitlines()];assert len(rows)==5710 and summary['all_file_hash_size_and_modes_verified']
assert len({row['relative_path'] for row in rows})==len(rows) and {row['relative_path'] for row in rows}==set(manifest)
afterhashes={e['path']:e['after_sha256'] for e in note['reports']}
for row in rows:
 e=manifest[row['relative_path']];expected_hash=afterhashes.get(row['relative_path'],e['sha256']);expected_bytes=e['bytes']+(len(note['note_utf8'].encode()) if row['relative_path'] in afterhashes else 0)
 assert row['mode']==row['expected_mode']==e['mode'] and row['bytes']==row['expected_bytes']==expected_bytes and row['sha256']==row['expected_sha256']==expected_hash
 assert row['kind']==('MATCH_POSTNOTE_FINAL_REPORT' if row['relative_path'] in afterhashes else 'MATCH_ARCHIVED_INPUT')
controls=json.loads((P/'weekend-subprocess-delivery-results-v1.json').read_bytes());assert controls['matched_controls']==4 and controls['consumer_sha256']==recipe['consumer_sha256'] and all(x['matched'] for x in controls['cases'])
cli=json.loads((P/'weekend-capsule-cli-refusal-results-v1.json').read_bytes());assert cli['matched_controls']==4 and cli['extraction_roots_created']==0 and all(x['matched'] for x in cli['cases'])
mapped_failure_receipts=[]
for x in cli['cases']:
 if x['failure_receipt']:
  recorded=Path(x['failure_receipt']);original_root=Path(recipe['working_directory'])
  relative=recorded.relative_to(original_root) if recorded.is_absolute() else recorded
  if relative.is_absolute() or '..' in relative.parts:raise ValueError('UNSAFE_FAILURE_RECEIPT_PATH')
  restored_ref=(ROOT/relative).resolve();assert restored_ref.is_relative_to(ROOT) and restored_ref.is_file()
  mapped_failure_receipts.append({'recorded':str(recorded),'restored':str(restored_ref),'relative':str(relative)})
  failure=json.loads(restored_ref.read_bytes());assert failure['restored_root'] is None and failure['consumers']==[] and failure['status']=='FAILED_PRESERVED_NO_RETRY'
correspondence=json.loads((P/'weekend-capsule-v1-v2-admission-correspondence-v1.json').read_bytes());assert correspondence['AST_equal']
print(json.dumps({'status':'PASS_STANDALONE_WEEKEND_RECIPE_AND_RAW_DELIVERY_RECEIPT_RECOVERY','original_capsule_files':5710,'report_prefix_plus_note_reconstructions':4,'recorded_data_consumers':4,'recorded_subprocess_controls':4,'recorded_CLI_refusal_controls':4,'current_model_or_framework_calls':0,'new_nested_full_restore_or_synthetic_controls_executed':False,'failure_receipts_mapped_to_selected_root':mapped_failure_receipts,'independent_human_or_semantic_approval_inferred':False}))
