"""Observe Python open events for the actual CP054 nine-reader profile."""
from pathlib import Path
import json,hashlib,datetime,subprocess,sys,os
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
receipt=P/'weekend-capsule-consumption-results-v5-core.json';r=json.loads(receipt.read_bytes());assert r['status']=='PASS_EXISTING_CAPSULE_STANDALONE_RECOVERY' and r['actual_data_consumer_count']==9
selected=Path(r['restored_root']);wrapper=P/'weekend_reader_open_audit_wrapper_v1.py';restored_wrapper=selected/wrapper.relative_to(ROOT);assert sha(wrapper)==sha(restored_wrapper);code=restored_wrapper.read_text()
pr={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'selected_root':str(selected),'original_workspace':str(ROOT),'capsule_receipt':str(receipt.relative_to(ROOT)),'capsule_receipt_sha256':sha(receipt),'wrapper_sha256':sha(restored_wrapper),'scripts':[{'name':x['script'],'sha256':sha(selected/'agent/research/final-intensive-20261121'/x['script'])} for x in r['consumers']],'scope':'Nine reader Python open events after hook; no OS/native/startup/all-branch or clean-machine guarantee.'}
protocol=P/'weekend-nine-readers-open-audit-protocol-v1.json'
with protocol.open('x') as f:json.dump(pr,f,indent=2);f.write('\n')
folder=P/'weekend-nine-readers-open-audit-v1';folder.mkdir(mode=0o700);rows=[]
for e in pr['scripts']:
 script=selected/'agent/research/final-intensive-20261121'/e['name'];assert sha(script)==e['sha256'];result=folder/(e['name']+'.json');command=[sys.executable,'-B','-c',code,str(script),str(selected),str(ROOT),str(result)]
 run=subprocess.run(command,cwd=selected,capture_output=True,timeout=90,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});data=json.loads(result.read_bytes())
 rows.append({'script':e['name'],'exit_code':run.returncode,'stdout_sha256':hashlib.sha256(run.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(run.stderr).hexdigest(),'stdout':run.stdout.decode(errors='replace'),'stderr':run.stderr.decode(errors='replace'),'observation':str(result.relative_to(ROOT)),'observation_sha256':sha(result),'event_count':len(data['events']),'original_workspace_opens':data['opens_under_original_workspace'],'write_intents':data['observed_write_intents'],'outside_selected_root_paths':data['outside_selected_root_paths']})
 assert run.returncode==0 and data['status']=='EXIT_ZERO' and data['opens_under_original_workspace']==data['observed_write_intents']==0
outside=sorted({x for row in rows for x in row['outside_selected_root_paths']});prefix=Path(sys.base_prefix).resolve();outside_runtime=[x for x in outside if not Path(x).is_relative_to(prefix)]
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':sha(protocol),'reader_count':len(rows),'scripts':rows,'total_observed_open_events':sum(x['event_count'] for x in rows),'original_workspace_opens':sum(x['original_workspace_opens'] for x in rows),'observed_target_write_intents':sum(x['write_intents'] for x in rows),'all_reader_exits_zero':True,'runtime_prefix':str(prefix),'unique_outside_selected_root_paths':outside,'outside_runtime_prefix_paths':outside_runtime,'scope':pr['scope'],'model_calls':0,'framework_imports':0,'optimizer_updates':0,'known_weak_control_reference':'weekend-reader-open-audit-known-weak-results-v1.json: old v2 reader exits0 but observer detects3 original reads; unchanged observer calibration, not rerun.'}
with (P/'weekend-nine-readers-open-audit-results-v1.json').open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in out.items() if k not in ('scripts','unique_outside_selected_root_paths')}));assert not outside_runtime
