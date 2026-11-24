"""Freeze source-reviewed cross-file facts before a new extractor is implemented."""
import datetime
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent
freeze = json.loads((P/'httpx-source-family-freeze-v1.json').read_text())
entries = []
for cut in freeze['revisions']:
    base = P/'new-public-sources-v1/encode--httpx'/cut['revision']
    entries.append({'tag':cut['tag'],'revision':cut['revision'],'source_sha256':{name:hashlib.sha256((base/name).read_bytes()).hexdigest()for name in ['httpx/_transports/default.py','httpx/_exceptions.py']},'expected':{'mapping_pairs':14,'mapping_direction':'httpcore attribute keys -> imported local exception class names','initialization':'eager_module_literal' if cut['tag']=='0.25.2' else 'empty_module_map_then_loader_before_try_yield','loader_function':None if cut['tag']=='0.25.2' else '_load_httpcore_exceptions','handler_type':'Exception','unmapped_path':'bare raise','mapped_path':'raise mapped_exc(message) from exc','specificity_condition':'issubclass(to_exc, mapped_exc)','all_mapped_targets_have_declared_path_to':'RequestError','httpstatuserror_declared_parent':'HTTPError','request_context_handler_type':'RequestError','request_context_covers_all_httperror_types':False,'selected_sync_pool_call':'self._pool.handle_request(req)','selected_async_pool_call':'await self._pool.handle_async_request(req)','response_construction_outside_selected_map_context':True,'request_construction_outside_selected_map_context':True,'stream_iteration_has_explicit_map_context':True,'selected_close_methods_have_explicit_map_context':False}})
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'classification':'POST_SOURCE_REVIEW_CROSS_FILE_DEVELOPMENT_ORACLE_NOT_INDEPENDENT_GENERALIZATION','frozen_before_new_extractor_predictions':True,'revisions':entries,'joint_expectations':{'mapping_pairs_equal_across_revisions':True,'source_initialization_location_changed':True,'same_mapping_text_does_not_certify_old_physical_citations':True},'existing_profile_limits':['Owned five-file architecture compiler cannot ingest arbitrary two-file HTTPX registry.','Module observer deliberately refuses decorated functions, so no existing whole-function contract is relaxed.'],'source_executed':False,'model_calls':0,'runtime_import_or_http_request':False,'production_component_changed':False,'training_excluded':True,'certified_neural_holdout':False}
with(P/'httpx-cross-file-oracle-v1.json').open('x')as stream:
    stream.write(json.dumps(record,indent=2)+'\n')
print({'revision_facts_frozen':len(entries),'new_extractor_predictions_started':False,'source_execution':False})
