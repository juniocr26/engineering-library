"""Create immutable local research checkpoints and actually restore/replay them."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import stat
import subprocess
import tarfile
import tempfile
from checkpoint_paths_v1 import resolve_relative_regular

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--number', required=True, type=int)
args = parser.parse_args()
sha = lambda raw: hashlib.sha256(raw).hexdigest()
reports = [ROOT/name for name in ['AI_TRAINING_CAMPAIGN_REPORT.md', 'AI_TRAINING_FILE_INVENTORY.md', 'AI_FINE_TUNING_READINESS.md', 'AI_TRAINING_RESUME.md']]
sources = [x for x in P.rglob('*') if x.is_file() and not x.is_symlink() and '__pycache__' not in x.parts]
# Preserve the actual dependency closure of the finite binding profile, not just its manifest.
anchor = json.loads((P/'trusted-binding-anchor-v1.json').read_text())
sources += [ROOT/edge['path'] for bundle in anchor.values() for edge in bundle['dependencies']]
sources += reports
helper_protocol = json.loads((P/'helper-admission-protocol-v1.json').read_text())
sources += [ROOT/item['path'] for item in helper_protocol['dependencies']]
recorded_dependency_aliases=[]
for dependency_manifest in sorted(P.glob('remaining-chapters-recovery-dependencies-v*.json')):
    for item in json.loads(dependency_manifest.read_text())['dependencies']:
        dependency = resolve_relative_regular(ROOT,item['path'])
        canonical=str(dependency.relative_to(ROOT))
        if canonical!=item['path']:recorded_dependency_aliases.append({'manifest':str(dependency_manifest.relative_to(ROOT)),'recorded_path':item['path'],'canonical_path':canonical})
        assert sha(dependency.read_bytes()) == item['sha256'], str(dependency)
        sources.append(dependency)
canonical_aliases=list(recorded_dependency_aliases)
normalized_sources=[]
for original in sources:
    recorded=str(original.relative_to(ROOT))
    resolved=resolve_relative_regular(ROOT,recorded)
    normalized_sources.append(resolved)
    canonical=str(resolved.relative_to(ROOT))
    if canonical!=recorded:canonical_aliases.append({'recorded_path':recorded,'canonical_path':canonical})
sources=sorted(set(normalized_sources))
folder = ROOT/'.local-backups/final-intensive-20261121'/f'checkpoint-{args.number:03d}'
folder.mkdir(parents=True, mode=0o700, exist_ok=False)
os.chmod(folder, 0o700)
manifest = []
for path in sources:
    assert not path.is_symlink()
    manifest.append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes()), 'bytes': path.stat().st_size,
                     'mode': stat.S_IMODE(path.stat().st_mode)})
archive = folder/'research-reports-and-selected-dependencies.tar.gz'
with tarfile.open(archive, 'x:gz') as tar:
    for entry in manifest:
        tar.add(ROOT/entry['path'], arcname=entry['path'], recursive=False)
os.chmod(archive, 0o600)
with (folder/'input-manifest.json').open('x') as stream:
    json.dump(manifest, stream, indent=2)
    stream.write('\n')
os.chmod(folder/'input-manifest.json', 0o600)
restored = Path(tempfile.mkdtemp(prefix=f'el-final-{args.number:03d}-', dir='/private/tmp'))
with tarfile.open(archive) as tar:
    # All members originate from the exact trusted regular-file list above.
    assert all(member.isfile() and not Path(member.name).is_absolute() and '..' not in Path(member.name).parts for member in tar.getmembers())
    tar.extractall(restored, filter='data')
for entry in manifest:
    target = restored/entry['path']
    assert sha(target.read_bytes()) == entry['sha256']
    assert stat.S_IMODE(target.stat().st_mode) == entry['mode']
relative_research = P.relative_to(ROOT)
command = [os.sys.executable, '-B', '-c',
           'from pathlib import Path;import json,sys; p=Path(sys.argv[1]);sys.path.insert(0,str(p));import binding_envelope_v1 as v; a=json.loads((p/"trusted-binding-anchor-v1.json").read_text());root=p.parents[2];out={k:v.validate(v.canonical(x),x,root) for k,x in a.items()};print(json.dumps(out));assert all(not r for r in out.values())',
           str(restored/relative_research)]
replay = subprocess.run(command, capture_output=True, text=True, timeout=30, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
ast_command = [os.sys.executable, '-B', '-c',
               'from pathlib import Path;import json,sys; p=Path(sys.argv[1]);sys.path.insert(0,str(p));import observe_exception_scope_v2 as v; protocol=json.loads((p/"exception-scope-protocol-v2.json").read_text());rows=[v.flags((p/c["helper"]).read_text(),(p/c["job"]).read_text())[0]==c["expected"] for c in protocol["cases"]];print(json.dumps({"matched":sum(rows),"cases":len(rows)}));assert all(rows)',
               str(restored/relative_research)]
ast_replay = subprocess.run(ast_command, capture_output=True, text=True, timeout=30, env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'})
assert ast_replay.returncode == 0, ast_replay.stderr
helper_command = [os.sys.executable, '-B', '-c',
                  'from pathlib import Path;import json,sys; p=Path(sys.argv[1]);root=p.parents[2];sys.path.insert(0,str(root/"agent/tools"));import documentation_retrieval as h; protocol=json.loads((p/"helper-admission-protocol-v1.json").read_text());observations=[]\nfor c in protocol["tasks"]:\n raw=(p/"reacquired-public-sources"/c["task"]/c["path"]).read_bytes()\n try:\n  unit=h.extract(raw.decode(),c["selector"],c["language"]);h.validate_unit(unit,raw,c["selector"],c["language"]);status="ADMITTED_LEXICAL_UNIT"\n except Exception as error: status="REFUSED"\n observations.append(status==c["expected"])\nprint(json.dumps({"matched":sum(observations),"cases":len(observations)}));assert all(observations)',
                  str(restored/relative_research)]
helper_replay = subprocess.run(helper_command, capture_output=True, text=True, timeout=60, env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'})
assert helper_replay.returncode == 0, helper_replay.stderr
jsc_command = [os.sys.executable, '-B', str(restored/relative_research/'observe_zod_jsc_syntax_v1.py'), '--root', str(restored), '--stdout-only']
jsc_replay = subprocess.run(jsc_command, capture_output=True, text=True, timeout=30, env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'})
assert jsc_replay.returncode == 0, jsc_replay.stderr
jsc_observations = json.loads(jsc_replay.stdout)
assert all(row['matched'] for row in jsc_observations['observations']['cases'])
c_protocol = json.loads((restored/relative_research/'raylib-owned-example-syntax-protocol-v1.json').read_text())
c_replays = []
for case in c_protocol['cases']:
    c_command = [c_protocol['compiler'], *c_protocol['flags'], '-I', str((restored/c_protocol['header']).parent), str(restored/case['path'])]
    c_run = subprocess.run(c_command, capture_output=True, text=True, timeout=20)
    assert (c_run.returncode == 0) == case['expected_syntax_pass'], c_run.stderr
    c_replays.append({'id':case['id'],'command':c_command,'exit_code':c_run.returncode,'stdout':c_run.stdout,'stderr':c_run.stderr,'matched':True})
priority_command = [os.sys.executable, '-B', str(restored/relative_research/'observe_priority_pair_examples_v1.py'), '--root', str(restored), '--stdout-only']
priority_replay = subprocess.run(priority_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert priority_replay.returncode == 0, priority_replay.stderr
faq_command = [os.sys.executable,'-B','-c',
    'from pathlib import Path;import json,sys; p=Path(sys.argv[1]);sys.path.insert(0,str(p));import faq_question_binding_v1 as v; registry=json.loads((p/"faq-question-binding-registry-v1.json").read_text())["registry"];cases=json.loads((p/"faq-question-binding-controls-v1.json").read_text())["cases"];rows=[(v.diagnose(c["raw"],registry)["status"]=="LITERAL_BINDINGS_VALID")==c["expected_binding_valid"] for c in cases];print(json.dumps({"matched":sum(rows),"cases":len(rows),"semantic_acceptance":False}));assert all(rows)',
    str(restored/relative_research)]
faq_replay = subprocess.run(faq_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert faq_replay.returncode == 0, faq_replay.stderr
cpp_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_cpp_dispatch_ast_v3.py'),'--root',str(restored),'--stdout-only']
cpp_replay=subprocess.run(cpp_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert cpp_replay.returncode==0,cpp_replay.stderr
exposure_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_exposure_evidence_v1.py'),'--root',str(restored)]
exposure_replay=subprocess.run(exposure_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert exposure_replay.returncode==0,exposure_replay.stderr
chi_command=[os.sys.executable,'-B',str(restored/relative_research/'review_chi_revision_context_v1.py'),'--root',str(restored),'--replay-native','--stdout-only']
chi_replay=subprocess.run(chi_command,capture_output=True,text=True,timeout=45,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert chi_replay.returncode==0,chi_replay.stderr
openshot_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_openshot_path_case_v1.py'),'--root',str(restored)]
openshot_replay=subprocess.run(openshot_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert openshot_replay.returncode==0,openshot_replay.stderr
tokenizer_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_gguf_metadata_prefix_v1.py'),'--root',str(restored)]
tokenizer_replay=subprocess.run(tokenizer_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert tokenizer_replay.returncode==0,tokenizer_replay.stderr
esp_js_command=[os.sys.executable,'-B',str(restored/relative_research/'observe_esp_hal_js_syntax_v1.py'),'--root',str(restored),'--stdout-only']
esp_js_replay=subprocess.run(esp_js_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert esp_js_replay.returncode==0,esp_js_replay.stderr
helper_delivery_command=[os.sys.executable,'-B',str(restored/relative_research/'observe_helper_subprocess_delivery_v2.py'),'--root',str(restored),'--output-root',str(restored/'isolated-helper-delivery-replay')]
helper_delivery_replay=subprocess.run(helper_delivery_command,capture_output=True,text=True,timeout=45,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert helper_delivery_replay.returncode==0,helper_delivery_replay.stderr
job_delivery_command=[os.sys.executable,'-B',str(restored/relative_research/'observe_helper_job_delivery_v1.py'),'--root',str(restored),'--output-root',str(restored/'isolated-helper-job-delivery-replay')]
job_delivery_replay=subprocess.run(job_delivery_command,capture_output=True,text=True,timeout=45,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert job_delivery_replay.returncode==0,job_delivery_replay.stderr
report_bundle_command=[os.sys.executable,'-B',str(restored/relative_research/'observe_report_bundle_recovery_v2.py'),'--root',str(restored),'--output-root',str(restored/'isolated-report-bundle-replay')]
report_bundle_replay=subprocess.run(report_bundle_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert report_bundle_replay.returncode==0,report_bundle_replay.stderr
go_types_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_owned_go_type_relations_v1.py'),'--root',str(restored)]
go_types_replay=subprocess.run(go_types_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert go_types_replay.returncode==0,go_types_replay.stderr
stdlib_types_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_go_stdlib_type_relations_v1.py'),'--root',str(restored)]
stdlib_types_replay=subprocess.run(stdlib_types_command,capture_output=True,text=True,timeout=45,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert stdlib_types_replay.returncode==0,stdlib_types_replay.stderr
shellwords_scope_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_shellwords_version_scope_v1.py'),'--root',str(restored)]
shellwords_scope_replay=subprocess.run(shellwords_scope_command,capture_output=True,text=True,timeout=45,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert shellwords_scope_replay.returncode==0,shellwords_scope_replay.stderr
directory_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_gguf_tensor_directory_v1.py'),'--root',str(restored)]
directory_replay=subprocess.run(directory_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert directory_replay.returncode==0,directory_replay.stderr
bilingual_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_bilingual_guard_study_v1.py'),'--root',str(restored)]
bilingual_replay=subprocess.run(bilingual_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert bilingual_replay.returncode==0,bilingual_replay.stderr
go_image_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_go_image_animation_candidate_v1.py'),'--root',str(restored)]
go_image_replay=subprocess.run(go_image_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert go_image_replay.returncode==0,go_image_replay.stderr
compression_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_go_image_compression_candidate_v1.py'),'--root',str(restored)]
compression_replay=subprocess.run(compression_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert compression_replay.returncode==0,compression_replay.stderr
graph_types_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_go_source_graph_types_v1.py'),'--root',str(restored)]
graph_types_replay=subprocess.run(graph_types_command,capture_output=True,text=True,timeout=45,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert graph_types_replay.returncode==0,graph_types_replay.stderr
config_target_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_go_image_configuration_target_v1.py'),'--root',str(restored)]
config_target_replay=subprocess.run(config_target_command,capture_output=True,text=True,timeout=45,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert config_target_replay.returncode==0,config_target_replay.stderr
inline_faq_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_config_inline_faqs_v1.py'),'--root',str(restored)]
inline_faq_replay=subprocess.run(inline_faq_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert inline_faq_replay.returncode==0,inline_faq_replay.stderr
starlette_target_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_starlette_server_error_target_v1.py'),'--root',str(restored)]
starlette_target_replay=subprocess.run(starlette_target_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert starlette_target_replay.returncode==0,starlette_target_replay.stderr
frontend_target_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_frontend_dimensions_target_v1.py'),'--root',str(restored)]
frontend_target_replay=subprocess.run(frontend_target_command,capture_output=True,text=True,timeout=60,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert frontend_target_replay.returncode==0,frontend_target_replay.stderr
httpguts_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_httpguts_snapshot_v1.py'),'--root',str(restored)]
httpguts_replay=subprocess.run(httpguts_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert httpguts_replay.returncode==0,httpguts_replay.stderr
task_iteration_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_starlette_task_iteration_target_v1.py'),'--root',str(restored)]
task_iteration_replay=subprocess.run(task_iteration_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert task_iteration_replay.returncode==0,task_iteration_replay.stderr
quality_target_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_go_image_quality_target_v1.py'),'--root',str(restored)]
quality_target_replay=subprocess.run(quality_target_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert quality_target_replay.returncode==0,quality_target_replay.stderr
dimensions_target_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_go_image_dimensions_target_v1.py'),'--root',str(restored)]
dimensions_target_replay=subprocess.run(dimensions_target_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert dimensions_target_replay.returncode==0,dimensions_target_replay.stderr
checkpoint_paths_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_checkpoint_paths_v1.py'),'--root',str(restored)]
checkpoint_paths_replay=subprocess.run(checkpoint_paths_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert checkpoint_paths_replay.returncode==0,checkpoint_paths_replay.stderr
rails_request_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_rails_request_target_v1.py'),'--root',str(restored)]
rails_request_replay=subprocess.run(rails_request_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert rails_request_replay.returncode==0,rails_request_replay.stderr
redis_targets_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_redis_targets_v1.py'),'--root',str(restored)]
redis_targets_replay=subprocess.run(redis_targets_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert redis_targets_replay.returncode==0,redis_targets_replay.stderr
ruff_target_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_ruff_target_v1.py'),'--root',str(restored)]
ruff_target_replay=subprocess.run(ruff_target_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert ruff_target_replay.returncode==0,ruff_target_replay.stderr
opencv_target_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_opencv_targets_v1.py'),'--root',str(restored)]
opencv_target_replay=subprocess.run(opencv_target_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert opencv_target_replay.returncode==0,opencv_target_replay.stderr
duckdb_target_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_duckdb_target_v1.py'),'--root',str(restored)]
duckdb_target_replay=subprocess.run(duckdb_target_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert duckdb_target_replay.returncode==0,duckdb_target_replay.stderr
prometheus_target_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_prometheus_targets_v1.py'),'--root',str(restored)]
prometheus_target_replay=subprocess.run(prometheus_target_command,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert prometheus_target_replay.returncode==0,prometheus_target_replay.stderr
fastify_target_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_fastify_target_v1.py'),'--root',str(restored)]
fastify_target_replay=subprocess.run(fastify_target_command,capture_output=True,text=True,timeout=45,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert fastify_target_replay.returncode==0,fastify_target_replay.stderr
sqlx_target_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_sqlx_targets_v1.py'),'--root',str(restored)]
sqlx_target_replay=subprocess.run(sqlx_target_command,capture_output=True,text=True,timeout=45,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert sqlx_target_replay.returncode==0,sqlx_target_replay.stderr
sdk_retry_target_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_sdk_retry_target_v1.py'),'--root',str(restored)]
sdk_retry_target_replay=subprocess.run(sdk_retry_target_command,capture_output=True,text=True,timeout=45,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert sdk_retry_target_replay.returncode==0,sdk_retry_target_replay.stderr
chi_targets_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_chi_targets_v1.py'),'--root',str(restored)]
chi_targets_replay=subprocess.run(chi_targets_command,capture_output=True,text=True,timeout=45,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert chi_targets_replay.returncode==0,chi_targets_replay.stderr
agent_contracts_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_agent_contracts_dated_clarification_v1.py'),'--root',str(restored)]
agent_contracts_replay=subprocess.run(agent_contracts_command,capture_output=True,text=True,timeout=45,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert agent_contracts_replay.returncode==0,agent_contracts_replay.stderr
agent_contracts_v2_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_agent_contracts_dated_clarification_v2.py'),'--root',str(restored)]
agent_contracts_v2_replay=subprocess.run(agent_contracts_v2_command,capture_output=True,text=True,timeout=45,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert agent_contracts_v2_replay.returncode==0,agent_contracts_v2_replay.stderr
next_trial_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_next_neural_matched_dimensions_v1.py'),'--root',str(restored)]
next_trial_replay=subprocess.run(next_trial_command,capture_output=True,text=True,timeout=45,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert next_trial_replay.returncode==0,next_trial_replay.stderr
scope_pilot_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_scope_and_first_pilot_review_v1.py'),'--root',str(restored)]
scope_pilot_replay=subprocess.run(scope_pilot_command,capture_output=True,text=True,timeout=45,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert scope_pilot_replay.returncode==0,scope_pilot_replay.stderr
faq_rows_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_dataset_faq_row_bindings_v1.py'),'--root',str(restored)]
faq_rows_replay=subprocess.run(faq_rows_command,capture_output=True,text=True,timeout=45,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert faq_rows_replay.returncode==0,faq_rows_replay.stderr
mask_state_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_h71_h72_mask_state_v1.py'),'--root',str(restored)]
mask_state_replay=subprocess.run(mask_state_command,capture_output=True,text=True,timeout=45,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert mask_state_replay.returncode==0,mask_state_replay.stderr
weekend_command=[os.sys.executable,'-B',str(restored/relative_research/'consume_weekend_recovery_receipts_v4.py'),'--root',str(restored)]
weekend_replay=subprocess.run(weekend_command,capture_output=True,text=True,timeout=90,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert weekend_replay.returncode==0,weekend_replay.stderr
result = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'checkpoint': args.number,
          'archive': str(archive.relative_to(ROOT)), 'archive_sha256': sha(archive.read_bytes()), 'archive_bytes': archive.stat().st_size,
          'input_manifest': str((folder/'input-manifest.json').relative_to(ROOT)), 'input_manifest_sha256': sha((folder/'input-manifest.json').read_bytes()),
          'regular_files_restored_and_hash_verified': len(manifest), 'file_modes_verified': True,
          'restored_root': str(restored), 'standalone_weekend_receipt_consumer_replay':{'command':weekend_command,'exit_code':weekend_replay.returncode,'stdout':weekend_replay.stdout,'stderr':weekend_replay.stderr}, 'mask_state_static_review_consumer_replay':{'command':mask_state_command,'exit_code':mask_state_replay.returncode,'stdout':mask_state_replay.stdout,'stderr':mask_state_replay.stderr}, 'dataset_faq_row_bindings_consumer_replay':{'command':faq_rows_command,'exit_code':faq_rows_replay.returncode,'stdout':faq_rows_replay.stdout,'stderr':faq_rows_replay.stderr}, 'scope_and_first_pilot_review_consumer_replay':{'command':scope_pilot_command,'exit_code':scope_pilot_replay.returncode,'stdout':scope_pilot_replay.stdout,'stderr':scope_pilot_replay.stderr}, 'next_neural_request_preparation_consumer_replay':{'command':next_trial_command,'exit_code':next_trial_replay.returncode,'stdout':next_trial_replay.stdout,'stderr':next_trial_replay.stderr}, 'agent_contracts_internal_v2_consumer_replay':{'command':agent_contracts_v2_command,'exit_code':agent_contracts_v2_replay.returncode,'stdout':agent_contracts_v2_replay.stdout,'stderr':agent_contracts_v2_replay.stderr}, 'agent_contracts_internal_consumer_replay':{'command':agent_contracts_command,'exit_code':agent_contracts_replay.returncode,'stdout':agent_contracts_replay.stdout,'stderr':agent_contracts_replay.stderr}, 'chi_targets_consumer_replay':{'command':chi_targets_command,'exit_code':chi_targets_replay.returncode,'stdout':chi_targets_replay.stdout,'stderr':chi_targets_replay.stderr}, 'sdk_retry_target_consumer_replay':{'command':sdk_retry_target_command,'exit_code':sdk_retry_target_replay.returncode,'stdout':sdk_retry_target_replay.stdout,'stderr':sdk_retry_target_replay.stderr}, 'sqlx_targets_consumer_replay':{'command':sqlx_target_command,'exit_code':sqlx_target_replay.returncode,'stdout':sqlx_target_replay.stdout,'stderr':sqlx_target_replay.stderr}, 'fastify_target_consumer_replay':{'command':fastify_target_command,'exit_code':fastify_target_replay.returncode,'stdout':fastify_target_replay.stdout,'stderr':fastify_target_replay.stderr}, 'prometheus_targets_consumer_replay':{'command':prometheus_target_command,'exit_code':prometheus_target_replay.returncode,'stdout':prometheus_target_replay.stdout,'stderr':prometheus_target_replay.stderr}, 'duckdb_target_consumer_replay':{'command':duckdb_target_command,'exit_code':duckdb_target_replay.returncode,'stdout':duckdb_target_replay.stdout,'stderr':duckdb_target_replay.stderr}, 'opencv_targets_consumer_replay':{'command':opencv_target_command,'exit_code':opencv_target_replay.returncode,'stdout':opencv_target_replay.stdout,'stderr':opencv_target_replay.stderr}, 'gguf_tensor_directory_consumer_replay':{'command':directory_command,'exit_code':directory_replay.returncode,'stdout':directory_replay.stdout,'stderr':directory_replay.stderr}, 'bilingual_screen_metric_consumer_replay':{'command':bilingual_command,'exit_code':bilingual_replay.returncode,'stdout':bilingual_replay.stdout,'stderr':bilingual_replay.stderr}, 'go_image_original_target_consumer_replay':{'command':go_image_command,'exit_code':go_image_replay.returncode,'stdout':go_image_replay.stdout,'stderr':go_image_replay.stderr}, 'go_image_compression_consumer_replay':{'command':compression_command,'exit_code':compression_replay.returncode,'stdout':compression_replay.stdout,'stderr':compression_replay.stderr}, 'go_source_graph_consumer_replay':{'command':graph_types_command,'exit_code':graph_types_replay.returncode,'stdout':graph_types_replay.stdout,'stderr':graph_types_replay.stderr}, 'go_image_configuration_consumer_replay':{'command':config_target_command,'exit_code':config_target_replay.returncode,'stdout':config_target_replay.stdout,'stderr':config_target_replay.stderr}, 'config_inline_faq_consumer_replay':{'command':inline_faq_command,'exit_code':inline_faq_replay.returncode,'stdout':inline_faq_replay.stdout,'stderr':inline_faq_replay.stderr}, 'starlette_server_error_consumer_replay':{'command':starlette_target_command,'exit_code':starlette_target_replay.returncode,'stdout':starlette_target_replay.stdout,'stderr':starlette_target_replay.stderr}, 'ruff_target_consumer_replay':{'command':ruff_target_command,'exit_code':ruff_target_replay.returncode,'stdout':ruff_target_replay.stdout,'stderr':ruff_target_replay.stderr}, 'redis_targets_consumer_replay':{'command':redis_targets_command,'exit_code':redis_targets_replay.returncode,'stdout':redis_targets_replay.stdout,'stderr':redis_targets_replay.stderr}, 'rails_request_consumer_replay':{'command':rails_request_command,'exit_code':rails_request_replay.returncode,'stdout':rails_request_replay.stdout,'stderr':rails_request_replay.stderr}, 'checkpoint_paths_consumer_replay':{'command':checkpoint_paths_command,'exit_code':checkpoint_paths_replay.returncode,'stdout':checkpoint_paths_replay.stdout,'stderr':checkpoint_paths_replay.stderr}, 'canonical_dependency_aliases':canonical_aliases, 'go_image_dimensions_consumer_replay':{'command':dimensions_target_command,'exit_code':dimensions_target_replay.returncode,'stdout':dimensions_target_replay.stdout,'stderr':dimensions_target_replay.stderr}, 'go_image_quality_consumer_replay':{'command':quality_target_command,'exit_code':quality_target_replay.returncode,'stdout':quality_target_replay.stdout,'stderr':quality_target_replay.stderr}, 'starlette_task_iteration_consumer_replay':{'command':task_iteration_command,'exit_code':task_iteration_replay.returncode,'stdout':task_iteration_replay.stdout,'stderr':task_iteration_replay.stderr}, 'httpguts_snapshot_consumer_replay':{'command':httpguts_command,'exit_code':httpguts_replay.returncode,'stdout':httpguts_replay.stdout,'stderr':httpguts_replay.stderr}, 'frontend_dimensions_consumer_replay':{'command':frontend_target_command,'exit_code':frontend_target_replay.returncode,'stdout':frontend_target_replay.stdout,'stderr':frontend_target_replay.stderr}, 'consumer_replay': {'command': command, 'exit_code': replay.returncode, 'stdout': replay.stdout, 'stderr': replay.stderr},
          'exception_scope_consumer_replay': {'command': ast_command, 'exit_code': ast_replay.returncode, 'stdout': ast_replay.stdout, 'stderr': ast_replay.stderr},
          'helper_admission_consumer_replay': {'command': helper_command, 'exit_code': helper_replay.returncode, 'stdout': helper_replay.stdout, 'stderr': helper_replay.stderr},
          'zod_jsc_parser_consumer_replay': {'command':jsc_command,'exit_code':jsc_replay.returncode,'stdout':jsc_replay.stdout,'stderr':jsc_replay.stderr},
          'raylib_owned_fragment_replays':c_replays,
          'priority_pair_syntax_consumer_replay':{'command':priority_command,'exit_code':priority_replay.returncode,'stdout':priority_replay.stdout,'stderr':priority_replay.stderr},
          'faq_binding_consumer_replay':{'command':faq_command,'exit_code':faq_replay.returncode,'stdout':faq_replay.stdout,'stderr':faq_replay.stderr},
          'cpp_AST_IR_consumer_replay':{'command':cpp_command,'exit_code':cpp_replay.returncode,'stdout':cpp_replay.stdout,'stderr':cpp_replay.stderr},
          'public_exposure_consumer_replay':{'command':exposure_command,'exit_code':exposure_replay.returncode,'stdout':exposure_replay.stdout,'stderr':exposure_replay.stderr},
          'shellwords_version_scope_consumer_replay':{'command':shellwords_scope_command,'exit_code':shellwords_scope_replay.returncode,'stdout':shellwords_scope_replay.stdout,'stderr':shellwords_scope_replay.stderr},
          'stdlib_go_type_relations_consumer_replay':{'command':stdlib_types_command,'exit_code':stdlib_types_replay.returncode,'stdout':stdlib_types_replay.stdout,'stderr':stdlib_types_replay.stderr},
          'owned_go_type_relations_consumer_replay':{'command':go_types_command,'exit_code':go_types_replay.returncode,'stdout':go_types_replay.stdout,'stderr':go_types_replay.stderr},
          'report_bundle_recovery_consumer_replay':{'command':report_bundle_command,'exit_code':report_bundle_replay.returncode,'stdout':report_bundle_replay.stdout,'stderr':report_bundle_replay.stderr},
          'helper_job_delivery_consumer_replay':{'command':job_delivery_command,'exit_code':job_delivery_replay.returncode,'stdout':job_delivery_replay.stdout,'stderr':job_delivery_replay.stderr},
          'esp_hal_js_syntax_consumer_replay':{'command':esp_js_command,'exit_code':esp_js_replay.returncode,'stdout':esp_js_replay.stdout,'stderr':esp_js_replay.stderr},
          'helper_dynamic_delivery_consumer_replay':{'command':helper_delivery_command,'exit_code':helper_delivery_replay.returncode,'stdout':helper_delivery_replay.stdout,'stderr':helper_delivery_replay.stderr},
          'tokenizer_metadata_consumer_replay':{'command':tokenizer_command,'exit_code':tokenizer_replay.returncode,'stdout':tokenizer_replay.stdout,'stderr':tokenizer_replay.stderr},
          'openshot_case_binding_consumer_replay':{'command':openshot_command,'exit_code':openshot_replay.returncode,'stdout':openshot_replay.stdout,'stderr':openshot_replay.stderr},
          'chi_revision_consumer_replay':{'command':chi_command,'exit_code':chi_replay.returncode,'stdout':chi_replay.stdout,'stderr':chi_replay.stderr},
          'scope': 'Local checkpoint and finite binding/syntax/static-data consumer replay only. Not clean clone, model/optimizer, remote backup, Windows, crash durability or semantic correctness.',
          'self_cut': 'This receipt and manifest are outside own archive; later checkpoint can include earlier receipt. No infinite self-hash closure.',
          'active_campaign': True, 'neural_calls': 0, 'optimizer_updates': 0, 'gold': 0}
assert replay.returncode == 0, replay.stderr
name = f'checkpoint-{args.number:03d}.json'
for destination in [P/name, folder/'receipt.json']:
    with destination.open('x') as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
print(json.dumps({'checkpoint':args.number,'files':len(manifest),'archive_bytes':archive.stat().st_size,'all_replay_exits_zero':all(x.returncode==0 for x in [replay,ast_replay,helper_replay,jsc_replay,priority_replay,faq_replay,cpp_replay,exposure_replay,chi_replay,openshot_replay,tokenizer_replay,esp_js_replay,helper_delivery_replay,job_delivery_replay,report_bundle_replay,go_types_replay,stdlib_types_replay,shellwords_scope_replay,directory_replay,bilingual_replay,go_image_replay,compression_replay,graph_types_replay,config_target_replay,inline_faq_replay,starlette_target_replay,frontend_target_replay,httpguts_replay,task_iteration_replay,quality_target_replay,dimensions_target_replay,checkpoint_paths_replay,rails_request_replay,redis_targets_replay,ruff_target_replay,opencv_target_replay,duckdb_target_replay,prometheus_target_replay,fastify_target_replay,sqlx_target_replay,sdk_retry_target_replay,chi_targets_replay,agent_contracts_replay,agent_contracts_v2_replay,next_trial_replay,scope_pilot_replay,faq_rows_replay,mask_state_replay,weekend_replay]),'c_syntax_outcomes_matched':len(c_replays)}))
