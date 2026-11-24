from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,time
p=Path(__file__).parent
protocol=json.loads((p/'prometheus-warning-schema-run-input-v1.json').read_text())
remote=r"""import json,sys,urllib.request
payload=json.load(sys.stdin);request=payload['request'];base='http://ollama:11434'
tags=json.load(urllib.request.urlopen(base+'/api/tags',timeout=20))
assert any(m.get('name')==request['model'] and m.get('digest')==payload['expected_digest'] for m in tags.get('models',[])), 'model digest changed'
version=json.load(urllib.request.urlopen(base+'/api/version',timeout=20))
print(json.dumps({'verified_model_digest':payload['expected_digest'],'server_version':version}),file=sys.stderr,flush=True)
call=urllib.request.Request(base+'/api/chat',data=json.dumps(request,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'},method='POST')
with urllib.request.urlopen(call,timeout=600) as response:sys.stdout.buffer.write(response.read())
"""
for item in protocol['requests']:
 folder=Path(item['path']).parent
 assert not (folder/'started.json').exists(),'no automatic retry'
 reqbytes=Path(item['path']).read_bytes();assert hashlib.sha256(reqbytes).hexdigest()==item['sha256'];request=json.loads(reqbytes)
 start=datetime.now(timezone.utc);wall=time.monotonic()
 (folder/'started.json').write_text(json.dumps({'at':start.isoformat(),'condition':item['condition'],'request_sha256':item['sha256'],'kind':'CLAIM_JUDGMENT_NOT_COMPLETE_CHAPTER','no_retry':True},indent=2)+'\n')
 timed_out=False
 with (folder/'raw-response.json').open('wb') as output,(folder/'transport.stderr').open('wb') as error:
  proc=subprocess.Popen(['docker','exec','-i','engineering-library-research-1','python3','-c',remote],stdin=subprocess.PIPE,stdout=output,stderr=error)
  (folder/'process.json').write_text(json.dumps({'at':start.isoformat(),'host_child_pid':proc.pid,'condition':item['condition']},indent=2)+'\n')
  try:proc.communicate(json.dumps({'request':request,'expected_digest':protocol['model_digest']},ensure_ascii=False).encode(),timeout=660)
  except subprocess.TimeoutExpired:
   timed_out=True;proc.kill();proc.communicate()
 end=datetime.now(timezone.utc);body=(folder/'raw-response.json').read_bytes();outcome={'at':end.isoformat(),'started_at':start.isoformat(),'method':'prometheus-warning-schema-judgment-'+item['condition'],'condition':item['condition'],'kind':'CLAIM_JUDGMENT_NOT_COMPLETE_CHAPTER','returncode':proc.returncode,'wall_seconds':time.monotonic()-wall,'raw_response_sha256':hashlib.sha256(body).hexdigest(),'training_gold':False,'owner_approved':False,'optimizer_steps':0,'status':'TRANSPORT_TIMEOUT_UNKNOWN_SERVER_COMPLETION_NO_RETRY' if timed_out else 'TRANSPORT_FAILED_NO_RETRY'}
 if proc.returncode==0:
  result=json.loads(body)
  outcome.update({key:result.get(key) for key in ['model','done','done_reason','eval_count','prompt_eval_count','prompt_eval_cached_count','total_duration','load_duration','prompt_eval_duration','eval_duration']})
  outcome['status']='TRANSPORT_FINISHED_PENDING_JUDGMENT_REVIEW' if result.get('done') and result.get('eval_count',901)<=900 else 'UNEXPECTED_STOP_REMAINING_CALLS'
  (folder/'model-content.txt').write_text(result.get('message',{}).get('content',''))
 (folder/'outcome.json').write_text(json.dumps(outcome,indent=2)+'\n');print(json.dumps({'condition':item['condition'],'status':outcome['status'],'done_reason':outcome.get('done_reason'),'generated_tokens':outcome.get('eval_count'),'wall_seconds':outcome['wall_seconds']}),flush=True)
 if outcome['status']!='TRANSPORT_FINISHED_PENDING_JUDGMENT_REVIEW':raise SystemExit(2)
