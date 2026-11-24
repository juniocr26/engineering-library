"""Operational attempt ledger from terminal current-campaign workers; never model accuracy."""
from pathlib import Path
import json,hashlib,datetime,collections
P=Path(__file__).resolve().parent;rows=[];groups=collections.defaultdict(list);requests=[]
for request in sorted(P.rglob('request.json')):
 group=request.relative_to(P).parts[0]
 if group=='original-faq-provenance-resolution-v2':requests.append({'path':str(request),'kind':'HISTORICAL_REQUEST_CANONICAL_COPY_NOT_CURRENT_PLANNED_INFERENCE'});continue
 folder=request.parent;outcome=folder/'outcome.json'
 state='TERMINAL' if outcome.exists() else 'STARTED_WITHOUT_TERMINAL' if (folder/'started.json').exists() else 'NOT_STARTED'
 if group=='semantic-verifier-label-only-v1' and state=='NOT_STARTED':state='SUPERSEDED_BEFORE_PREDICTIONS'
 requestrow={'path':str(request),'sha256':hashlib.sha256(request.read_bytes()).hexdigest(),'group':group,'state':state};requests.append(requestrow)
 if not outcome.exists():continue
 r=json.loads(outcome.read_text());raw=folder/'raw-response.json';content=folder/'model-content.txt';requestdata=json.loads(request.read_text());rawsha=hashlib.sha256(raw.read_bytes()).hexdigest() if raw.exists() else None
 if r.get('request_sha256'):assert requestrow['sha256']==r['request_sha256']
 if r.get('raw_response_sha256'):assert rawsha==r['raw_response_sha256']
 valid=None;duplicates=None
 if content.exists():
  try:
   json.loads(content.read_text());valid=True
  except (ValueError,TypeError):valid=False
 row={'folder':str(folder),'group':group,'task':r.get('task'),'recorded_batch_method':r.get('method'),'request_sha256':requestrow['sha256'],'outcome_sha256':hashlib.sha256(outcome.read_bytes()).hexdigest(),'raw_response_sha256':rawsha,'content_sha256':hashlib.sha256(content.read_bytes()).hexdigest() if content.exists() else None,'exit_code':r.get('exit_code'),'done_reason':r.get('done_reason'),'syntactic_json_only':valid,'reported_generated_tokens':r.get('eval_count'),'reported_server_seconds':r.get('total_duration',0)/1e9 if r.get('total_duration') is not None else None,'reported_request_wall_seconds':r.get('wall_seconds'),'requested_options':requestdata.get('options'),'request_model':requestdata.get('model'),'source_program_executed':False}
 if row['reported_generated_tokens'] is None and raw.exists():
  try:
   rr=json.loads(raw.read_text());row['reported_generated_tokens']=rr.get('eval_count');row['reported_server_seconds']=rr.get('total_duration',0)/1e9 if rr.get('total_duration') is not None else None
  except (ValueError,TypeError):pass
 rows.append(row);groups[group].append(row)
summary=[]
for group,items in sorted(groups.items()):summary.append({'group':group,'attempts':len(items),'transport_returned':sum(x['exit_code']==0 for x in items),'normal_stops':sum(x['done_reason']=='stop' for x in items),'length_stops':sum(x['done_reason']=='length' for x in items),'transport_failures':sum(x['exit_code']!=0 for x in items),'syntactic_json_outputs':sum(x['syntactic_json_only'] is True for x in items),'reported_generated_tokens':sum(x['reported_generated_tokens'] or 0 for x in items),'sum_reported_server_seconds':sum(x['reported_server_seconds'] or 0 for x in items),'sum_request_wall_seconds':sum(x['reported_request_wall_seconds'] or 0 for x in items)})
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'current_campaign_attempts':len(rows),'groups':summary,'attempts':rows,'request_census':requests,'request_states':dict(collections.Counter(x.get('state',x.get('kind')) for x in requests)),'operational_totals_only':{'transport_returned':sum(x['exit_code']==0 for x in rows),'normal_stops':sum(x['done_reason']=='stop' for x in rows),'length_stops':sum(x['done_reason']=='length' for x in rows),'transport_failures':sum(x['exit_code']!=0 for x in rows),'reported_generated_tokens':sum(x['reported_generated_tokens'] or 0 for x in rows),'sum_reported_server_seconds':sum(x['reported_server_seconds'] or 0 for x in rows),'sum_reported_request_wall_seconds':sum(x['reported_request_wall_seconds'] or 0 for x in rows)},'limits':['Operational counts are not general model accuracy, complete documents, semantic support or independent trials.','Current heterogeneous attempts include generators, critics, relation selectors and copy diagnostics; do not pool acceptance fractions.','Old0/9and0/13not included or changed. F reusesDandTusesno neural inference.','BatchmethodALL in someworkeroutcomes is runner CLI label; protocol/folder defines actual experimental condition.','Syntacticjson is standardJSONparse only, not unique-key/strictschema/semantic admission. Duplicate-key reviews remain separate.','InitialAHTTP500 body was not preserved by old first runner; do not invent it from emptyfile. H/VHTTP500 bodies retained separately.','Sumserver/requestseconds is not campaign elapsed/productivehuman time and is not measured native training performance.'],'active_started_without_terminal':sum(x.get('state')=='STARTED_WITHOUT_TERMINAL' for x in requests),'model_weights_changed':False,'optimizer_updates':0,'gold':0}
with (P/'current-campaign-inference-ledger-v2.json').open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print(json.dumps({'attempts':len(rows),'states':r['request_states'],'operational_totals':r['operational_totals_only']},indent=2))
