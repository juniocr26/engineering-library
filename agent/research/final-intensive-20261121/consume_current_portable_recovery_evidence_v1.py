import argparse,json,hashlib,base64,stat
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True,type=Path);ROOT=ap.parse_args().root.resolve();P=ROOT/'agent/research/final-intensive-20261121';sha=lambda b:hashlib.sha256(b).hexdigest();original=Path(json.loads((P/'root-report-bundle-consolidation-067/plan.json').read_bytes())['original_root'])
def mapped(value):
 path=Path(value);relative=path.relative_to(original) if path.is_absolute() else path;actual=(ROOT/relative).resolve()
 if not actual.is_relative_to(ROOT):raise ValueError('EVIDENCE_PATH_OUTSIDE_SELECTED_ROOT')
 return actual
for e in json.loads((P/'remaining-chapters-recovery-dependencies-v43.json').read_bytes())['dependencies']:assert sha((ROOT/e['path']).read_bytes())==e['sha256']
package=json.loads((P/'first-lora-owner-authorization-package-v2.json').read_bytes());oldpackage=json.loads((P/'first-lora-owner-authorization-package-v1.json').read_bytes());assert package['do_not_pass_to_training_cli'] and not package['launch_allowed'] and not package['training_authorized'] and not package['ready_for_execution'];assert package['historical_unvalidated_parameters_not_config']==oldpackage['historical_unvalidated_parameters_not_config'] and package['unchanged_time_budget']==oldpackage['unchanged_time_budget'] and all(v==0 for v in package['current_actions'].values())
gate=package['current_gate_assessment'];assert sha((ROOT/gate['path']).read_bytes())==gate['sha256'];gates=json.loads((ROOT/gate['path']).read_bytes());assert len(gates['gates'])==9 and all(x['launch_decision']=='NO_GO' for x in gates['gates'])
proof=json.loads((P/'weekend-capsule-consumption-results-v4.json').read_bytes());assert proof['status']=='PASS_EXISTING_CAPSULE_STANDALONE_RECOVERY' and proof['regular_files_restored_and_hash_verified']==5875 and proof['actual_data_consumer_count']==len(proof['consumers'])==7 and proof['exact_postnote_reports_reconstructed']==4
for c in proof['consumers']:
 assert c['status']=='EXIT_ZERO' and c['exit_code']==0
 for field in ['stdout','stderr']:
  raw=base64.b64decode(c[field+'_base64']);assert sha(raw)==c[field+'_sha256'] and len(raw)==c[field+'_bytes']
inputs=proof['inputs'];manifest_path=mapped(inputs['manifest']);receipt_path=mapped(inputs['receipt']);post_path=mapped(inputs['postnote']);assert sha(manifest_path.read_bytes())==inputs['manifest_sha256'] and sha(receipt_path.read_bytes())==inputs['receipt_sha256'] and sha(post_path.read_bytes())==inputs['postnote_sha256'];receipt=json.loads(receipt_path.read_bytes());assert receipt['archive_sha256']==inputs['archive_sha256'];entries=json.loads(manifest_path.read_bytes());post=json.loads(post_path.read_bytes());reports={e['path']:e for e in post['reports']};bound=0;prefixes=0
for e in entries:
 if e['path'] in reports:
  before=(P/'root-report-bundle-progress-073'/(e['path']+'.before.bin')).read_bytes();raw=before[:e['bytes']];assert before[e['bytes']:]==post['note_utf8'].encode() and sha(before)==reports[e['path']]['after_sha256'] and sha(raw)==e['sha256']==reports[e['path']]['before_sha256'];prefixes+=1
 else:
  f=ROOT/e['path'];assert f.resolve().is_relative_to(ROOT);raw=f.read_bytes();assert len(raw)==e['bytes'] and sha(raw)==e['sha256'] and stat.S_IMODE(f.stat().st_mode)==e['mode'];bound+=1
assert bound==5871 and prefixes==4
recipe=json.loads((P/'weekend-capsule-exact-recipe-v3.json').read_bytes());assert recipe['bootstrap_sha256']==proof['consumer_source_sha256']==sha((P/'consume_weekend_capsule_v4.py').read_bytes());assert sha(mapped(str(Path(inputs['receipt']).parent/'bootstrap-weekend-consumer-v4.py')).read_bytes())==recipe['bootstrap_sha256']
audit=json.loads((P/'weekend-seven-readers-open-audit-results-v1.json').read_bytes());protocol=json.loads((P/'weekend-seven-readers-open-audit-protocol-v1.json').read_bytes());assert sha((P/'weekend-seven-readers-open-audit-protocol-v1.json').read_bytes())==audit['protocol_sha256'];selected_at_observation=Path(protocol['selected_root']);assert selected_at_observation==Path(proof['restored_root']) and Path(protocol['original_workspace'])==original;events=0;outside=set()
for e in audit['scripts']:
 f=mapped(e['observation']);assert sha(f.read_bytes())==e['observation_sha256'];obs=json.loads(f.read_bytes());assert e['exit_code']==0 and obs['status']=='EXIT_ZERO'
 for event in obs['events']:
  events+=1
  if 'path' in event:
   path=Path(event['path']);assert path.is_absolute() and not path.is_relative_to(original) and not event['write_intent']
   if not path.is_relative_to(selected_at_observation):outside.add(str(path))
assert events==audit['total_observed_open_events']==4654
classification=json.loads((P/'weekend-seven-readers-open-audit-runtime-classification-v1.json').read_bytes());assert outside==set(classification['outside_selected_root_unique_paths']) and all(Path(x).is_relative_to(Path(classification['runtime_prefix'])) for x in outside)
weak=json.loads((P/'weekend-reader-open-audit-known-weak-results-v1.json').read_bytes());obs=json.loads((P/'weekend-reader-open-audit-known-weak-observation-v1.json').read_bytes());assert sha((P/'weekend-reader-open-audit-known-weak-observation-v1.json').read_bytes())==weak['observation_sha256'];detected=[e for e in obs['events'] if 'path' in e and Path(e['path']).is_relative_to(original)];assert len(detected)==3==weak['actual_count'] and weak['observer_detected_known_flaw']
print(json.dumps({'status':'PASS_CURRENT_PORTABLE_RECOVERY_AND_BOUNDED_OPEN_AUDIT_EVIDENCE','historic_CP051_immutable_inputs_bound':bound,'historic_CP051_report_prefixes_bound':prefixes,'CP051_archive_not_reextracted_or_required_by_this_reader':True,'recorded_standalone_data_readers':7,'recorded_open_events':events,'recorded_original_workspace_opens':0,'known_weak_control_original_opens_detected':3,'recorded_outside_paths_all_under_Python_runtime':len(outside),'LoRA_launch_gates_NO_GO':9,'current_model_or_framework_calls':0,'current_optimizer_updates':0,'OS_security_or_independent_human_certification_inferred':False}))
