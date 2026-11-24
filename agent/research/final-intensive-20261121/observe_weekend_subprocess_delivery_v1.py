from pathlib import Path
import json,hashlib,base64,datetime,importlib.util,sys
P=Path(__file__).resolve().parent;source=P/'consume_weekend_capsule_v2.py';spec=importlib.util.spec_from_file_location('owned_capsule_v2',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
cases=[{'id':'success-nonUTF8','code':"import sys;sys.stdout.buffer.write(bytes([111,107,255]));sys.stdout.flush()",'timeout':2,'status':'EXIT_ZERO','exit':0,'stdout':bytes([111,107,255]),'stderr':b''},{'id':'nonzero-stderr','code':"import sys;sys.stderr.buffer.write(b'failure');sys.exit(7)",'timeout':2,'status':'NONZERO_EXIT','exit':7,'stdout':b'','stderr':b'failure'},{'id':'timeout-partial','code':"import sys,time;sys.stdout.buffer.write(b'before');sys.stdout.flush();sys.stderr.buffer.write(b'pending');sys.stderr.flush();time.sleep(10)",'timeout':0.5,'status':'TIMEOUT_PARTIAL_CAPTURED_NO_RETRY','exit':None,'stdout':b'before','stderr':b'pending'},{'id':'missing-executable','code':None,'timeout':2,'status':'LAUNCH_FAILURE_NO_RETRY','exit':None,'stdout':b'','stderr':b''}]
protocol={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'before_outcomes':True,'consumer_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'cases':[{k:(base64.b64encode(v).decode() if isinstance(v,bytes) else v) for k,v in c.items()} for c in cases],'scope':'Four owned child-process delivery controls, no framework/model/optimizer; timeout wait is one0.5second fault control, not campaign clock padding.'}
with (P/'weekend-subprocess-delivery-protocol-v1.json').open('x') as f:json.dump(protocol,f,indent=2);f.write('\n')
rows=[]
for c in cases:
 command=[sys.executable,'-B','-c',c['code']] if c['code'] else [str(P/'INTENTIONALLY_ABSENT_CONTROL_EXECUTABLE')]
 result=m.run_finite_consumer(command,P,c['timeout']);checks={'status':result['status']==c['status'],'exit':result['exit_code']==c['exit']}
 for field in ['stdout','stderr']:
  raw=base64.b64decode(result[field+'_base64']);checks[field+'_raw_exact']=raw==c[field];checks[field+'_hash_exact']=hashlib.sha256(raw).hexdigest()==result[field+'_sha256']
 rows.append({'id':c['id'],'result':result,'checks':checks,'matched':all(checks.values())})
assert all(x['matched'] for x in rows)
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'consumer_sha256':protocol['consumer_sha256'],'cases':rows,'matched_controls':4,'model_calls':0,'optimizer_updates':0,'real_recovery_timeout_observed':False,'scope':'Owned artificial child outcomes only; original successfulv1receipt is preserved, not reclassified as a failed real restore.'}
with (P/'weekend-subprocess-delivery-results-v1.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({'matched_controls':4,'statuses':[x['result']['status'] for x in rows],'all_raw_bytes_preserved':True}))
