from pathlib import Path
import json,hashlib,datetime,collections
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sha=lambda b:hashlib.sha256(b).hexdigest();pre=P/'neural-failure-taxonomy-row-preflight-v1.json';pr=json.loads(pre.read_bytes());rows=[];deps={};statuses=collections.Counter();shapes=collections.Counter();done=collections.Counter()
def bind(ref):
 f=(ROOT/ref['path']).resolve();assert f.is_relative_to(ROOT/'agent/research') or f.is_relative_to(ROOT/'.local-backups');raw=f.read_bytes();assert sha(raw)==ref['sha256'];deps[ref['path']]=ref['sha256'];return raw
for e in pr['allowed_rows']:
 raw=(ROOT/e['file']).read_bytes().splitlines()[e['line']-1];assert sha(raw)==e['row_sha256'];r=json.loads(raw);assert r['source_family']=='source-repository:codex-owned-synthetic-contracts' and r['observed_output_is_not_a_corrected_target'] is True
 assert all(r[k] is False for k in ['owner_approved','training_gold','training_use_approved','automatic_trainer_consumer','automatic_inference_consumer'])
 refs={}
 for k,v in r.items():
  if isinstance(v,dict) and 'path' in v and 'sha256' in v:bind(v);refs[k]=v
 req=json.loads(bind(r['request_ref']));response=json.loads(bind(r['response_ref']));content=response['message']['content'];parsed=None;parseerror=None
 try:parsed=json.loads(content)
 except json.JSONDecodeError as error:parseerror=str(error)
 if 'observed_model_content' in r:match='EXACT_RAW_CONTENT' if r['observed_model_content']==content else 'MISMATCH_REVIEW_REQUIRED'
 elif r.get('observed_model_output')==parsed:match='EXACT_PARSED_RESPONSE'
 elif isinstance(parsed,dict) and parsed.get('claims')==r.get('observed_model_output'):match='EXACT_CLAIMS_ARRAY_PROJECTION'
 else:match='MISMATCH_REVIEW_REQUIRED'
 shapes[match]+=1;status=r.get('source_review',{}).get('status','OTHER_DIAGNOSTIC_SCHEMA_NO_INLINE_STATUS');statuses[status]+=1;done[str(response.get('done_reason'))]+=1
 rows.append({**e,'category':r['category'],'lineage_group':r['lineage_group'],'experiment_group':r.get('experiment_group'),'inline_review_status':status,'manual_review_observation':r.get('manual_source_review',r.get('source_review',{}).get('finding')),'request_response_refs':refs,'model_name_matches_request_response':r['model']==req.get('model')==response.get('model'),'model_digest_is_retained_historical_metadata_not_new_runtime_attestation':r['model_digest'],'request_options':req.get('options'),'raw_response_done':response.get('done'),'raw_response_done_reason':response.get('done_reason'),'raw_response_json_parse_error':parseerror,'row_observation_to_raw_response_binding':match,'generated_token_count_matches_raw':r.get('generated_tokens')==response.get('eval_count'),'raw_response_tokens':response.get('eval_count'),'historical_server_seconds':response.get('total_duration',0)/1e9,'current_model_calls':0,'training_target':False})
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'preflight_sha256':sha(pre.read_bytes()),'rows':rows,'row_count':len(rows),'observation_binding_counts':dict(shapes),'inline_review_status_counts':dict(statuses),'done_reason_counts':dict(done),'raw_response_JSON_parse_failures':sum(r['raw_response_json_parse_error'] is not None for r in rows),'request_response_model_name_mismatches':sum(not r['model_name_matches_request_response'] for r in rows),'token_count_metadata_mismatches':sum(not r['generated_token_count_matches_raw'] for r in rows),'dependencies':[{'path':k,'sha256':v} for k,v in sorted(deps.items())],'dataset_role_is_not_failure_verdict':True,'full_chapter_acceptance_denominator_inferred':False,'new_model_calls':0,'private_rows_decoded':0,'original_rows_modified':0,'training_approval':False,'scope':'56selected historicalowned-development diagnostics, onefamily, multiple task/schema/budgettypes. Otherrefbytes hashed only; ledgerrefsnotdecoded as broadprivate/publicsemanticcorpus. Not newinference, modelgeneralaccuracy, fullchapterrate or causalweightsanalysis.'}
with (P/'historical-diagnostic-row-binding-results-v1.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['rows','dependencies','scope']}))
