from pathlib import Path
import json,hashlib,datetime,subprocess,sys
P=Path(__file__).resolve().parent;ROOT=P.parents[2];recipe=json.loads((P/'weekend-capsule-exact-recipe-v2.json').read_bytes());argv=recipe['command_argv'];source=P/'consume_weekend_capsule_v2.py';assert hashlib.sha256(source.read_bytes()).hexdigest()==recipe['consumer_sha256'];prefix=[sys.executable,'-B']+argv[2:];base=P/'weekend-capsule-cli-refusal-controls-v1';base.mkdir(mode=0o700,exist_ok=False)
cases=[{'id':'wrong-receipt-pin','replace':'--receipt-sha256','value':'0'*64,'exception':'RECEIPT_PIN_MISMATCH'},{'id':'wrong-postnote-pin','replace':'--postnote-sha256','value':'0'*64,'exception':'POSTNOTE_PIN_MISMATCH'},{'id':'byte-bound','append':['--max-total-bytes','1'],'exception':'DECLARED_RESOURCE_BOUND_EXCEEDED'},{'id':'existing-result','exception':'RESULT_ALREADY_EXISTS'}]
protocol={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'before_outcomes':True,'consumer_sha256':recipe['consumer_sha256'],'cases':cases,'expected':'All nonzero; no extraction root. Existing result bytes unchanged. Other3failures create a failure receipt with no consumer dispatch.','scope':'Four owned CLI refusal conditions using pinned existing capsule read-only; no source mutation,framework/model/optimizer orgeneral securityclaim.'}
with (P/'weekend-capsule-cli-refusal-protocol-v1.json').open('x') as f:json.dump(protocol,f,indent=2);f.write('\n')
rows=[]
for c in cases:
 command=list(prefix);result=base/(c['id']+'.json');command[command.index('--result')+1]=str(result)
 if 'replace' in c:command[command.index(c['replace'])+1]=c['value']
 command+=c.get('append',[]);before=None
 if c['id']=='existing-result':result.write_bytes(b'OWNED_PREEXISTING_CONTROL_NO_OVERWRITE\n');before=hashlib.sha256(result.read_bytes()).hexdigest()
 run=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=30);assert run.returncode!=0 and c['exception'] in run.stderr
 if before is not None:
  preserved=hashlib.sha256(result.read_bytes()).hexdigest()==before;assert preserved;receipt=None
 else:
  receipt=json.loads(result.read_bytes());assert receipt['status']=='FAILED_PRESERVED_NO_RETRY' and receipt['restored_root'] is None and receipt['consumers']==[] and receipt['exception']==c['exception'];preserved=True
 rows.append({'id':c['id'],'command':command,'exit_code':run.returncode,'stdout':run.stdout,'stderr':run.stderr,'existing_result_hash_unchanged':preserved if before is not None else None,'failure_receipt':str(result) if receipt else None,'no_extraction_root':True,'matched':True})
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'consumer_sha256':recipe['consumer_sha256'],'cases':rows,'matched_controls':4,'source_capsule_modified':False,'extraction_roots_created':0,'model_calls':0,'optimizer_updates':0,'scope':'Integration refusal receipts, not general crash or attacker certification.'}
with (P/'weekend-capsule-cli-refusal-results-v1.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({'matched_controls':4,'failure_receipts':3,'existing_result_unchanged':True,'extraction_roots_created':0}))
