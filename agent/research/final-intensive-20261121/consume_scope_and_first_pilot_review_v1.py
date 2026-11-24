import argparse,json,hashlib,tarfile
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True,type=Path);root=ap.parse_args().root.resolve();p=root/'agent/research/final-intensive-20261121';sha=lambda b:hashlib.sha256(b).hexdigest()
audit=json.loads((p/'source-scope-retirement-h68-h81-current-audit-v4.json').read_bytes())
for e in audit['external_dependency_edges']:assert sha((root/e['path']).read_bytes())==e['sha256']
assert audit['current_planner_exactly_matches_historical_H68'] and sha((root/'agent/tools/documentation_lifecycle.py').read_bytes())==audit['current_planner_sha256']
legacy=root/'agent/research/portfolio-vivabem-20261120';folder=legacy/'declared-scope-retirement-canary-v1';mf=json.loads((folder/'frozen-input-manifest.json').read_bytes());terminal=json.loads((folder/'observations/terminal.json').read_bytes());mapping=json.loads((folder/'independent-context-filemap.json').read_bytes());assert mapping['files']['before']['owned/old.py']['source']==mapping['files']['after']['owned/new.py']['source']
for case in mf['cases']:
 assert sha((folder/case['input']).read_bytes())==case['input_sha256'];row=next(x for x in terminal['conditions'] if x['id']==case['id']);raw=(folder/'observations'/(case['id']+'-stdout.json')).read_bytes();assert sha(raw)==row['stdout_sha256'];result=json.loads(raw);assert result['action']==row['action'] and result['writes']==0 and result['candidate_application']=='HUMAN_ALIGNMENT_REQUIRED'
assert next(x for x in terminal['conditions'] if x['id']=='misleading-complete')['action']=='REMOVE'
freeze=json.loads((legacy/'declared-scope-retirement-canary-input-freeze-v1.json').read_bytes());archive=root/freeze['archive'];assert sha(archive.read_bytes())==freeze['archive_sha256'];am=json.loads((root/freeze['manifest']).read_bytes())
with tarfile.open(archive,'r:gz') as tf:
 for e in am['files']:assert sha(tf.extractfile(e['path']).read())==e['sha256']
for n in ['owned-scope-python-host-observation-v2.json','owned-scope-python-linux-observation-v2.json','owned-scope-python-linux-observation-v1.json']:
 r=json.loads((legacy/n).read_bytes());assert sha((json.dumps(r['result'],sort_keys=True)+'\n').encode())==r['stdout_sha256']
host=json.loads((legacy/'owned-scope-python-host-observation-v2.json').read_bytes())['result'];linux=json.loads((legacy/'owned-scope-python-linux-observation-v2.json').read_bytes())['result'];assert host['original']==linux['original'] and host['conflicts']==linux['conflicts'];assert sum(x['expected']==x['actual'] for x in host['original'])==11 and all(x['expected']==x['actual'] for x in host['conflicts'])
gates=json.loads((p/'fine-tuning-current-nine-gates-assessment-v2.json').read_bytes());assert len(gates['gates'])==9 and all(x['launch_decision']=='NO_GO' for x in gates['gates']) and gates['passed_launch_gates']==0
for gate in gates['gates']:
 for e in gate['current_references']:assert sha((root/e['path']).read_bytes())==e['sha256']
package=json.loads((p/'first-lora-owner-authorization-package-v1.json').read_bytes());assert package['do_not_pass_to_training_cli'] is True and package['ready_for_execution'] is False and package['launch_allowed'] is False and package['training_authorized'] is False
assert sha((root/package['current_gate_assessment']['path']).read_bytes())==package['current_gate_assessment']['sha256']
assert package['supervised_data_contract']['approved_records_current']==0 and package['historical_unvalidated_parameters_not_config']['updates_max']==16 and package['historical_unvalidated_parameters_not_config']['sequence_max']==512
assert gates['conditional_geometry_scope_comparison']['historical_last2_layers_QV_rank4_coefficients']==81920 and gates['conditional_geometry_scope_comparison']['all_28_layers_QV_rank4_coefficients']==1146880
assert all(value==0 for value in package['current_actions'].values())
for e in json.loads((p/'remaining-chapters-recovery-dependencies-v38.json').read_bytes())['dependencies']:assert sha((root/e['path']).read_bytes())==e['sha256']
print(json.dumps({'status':'PASS_HISTORICAL_SCOPE_AND_NONEXECUTABLE_PILOT_PACKAGE_RECOVERY','H68_conditions':3,'H68_frozen_archive_inputs':len(am['files']),'H81_historical_stdout_reconstructions':3,'H75_original_frozen_label_agreement':'11/12','H75_conflict_agreement':'4/4','LoRA_launch_gates_NO_GO':9,'approved_training_records':0,'new_old_observer_or_planner_runs':0,'new_model_calls':0,'optimizer_updates':0,'semantic_or_independent_human_approval_inferred':False}))
