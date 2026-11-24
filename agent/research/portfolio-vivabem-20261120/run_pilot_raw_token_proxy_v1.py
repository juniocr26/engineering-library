from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,time,sys
p=Path(__file__).parent
protocol=json.loads((p/'pilot-raw-token-proxy-protocol-v1.json').read_text())
remote = r"""import sys,json,urllib.request,hashlib
payload=json.load(sys.stdin)
req=payload['request']
assert hashlib.sha256(req['prompt'].encode()).hexdigest()==payload['target_sha256']
base='http://ollama:11434'
tags=json.load(urllib.request.urlopen(base+'/api/tags',timeout=20))
assert any(m.get('name')==req['model'] and m.get('digest')==payload['expected_digest'] for m in tags.get('models',[])), 'model digest changed'
version=json.load(urllib.request.urlopen(base+'/api/version',timeout=20))
print(json.dumps({'verified_model_digest':payload['expected_digest'],'server_version':version,'target_sha256':payload['target_sha256']}),file=sys.stderr,flush=True)
call=urllib.request.Request(base+'/api/generate',data=json.dumps(req,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'},method='POST')
with urllib.request.urlopen(call,timeout=150) as response:
    sys.stdout.buffer.write(response.read())
"""
for target in protocol['targets']:
 folder=Path(target['request_path']).parent
 assert not (folder/'started.json').exists(), 'no automatic retry'
 raw_request=Path(target['request_path']).read_bytes()
 assert hashlib.sha256(raw_request).hexdigest()==target['request_sha256']
 request=json.loads(raw_request)
 assert request['raw'] and request['stream'] is False and request['options']['num_predict']==1
 start=datetime.now(timezone.utc);wall=time.monotonic()
 (folder/'started.json').write_text(json.dumps({'at':start.isoformat(),'kind':'RAW_TOKEN_BUDGET_PROXY_NOT_DOCUMENT_EVALUATION','request_sha256':target['request_sha256'],'no_retry':True},indent=2)+'\n')
 with (folder/'raw-response.json').open('wb') as output,(folder/'transport.stderr').open('wb') as error:
  proc=subprocess.Popen(['docker','exec','-i','engineering-library-research-1','python3','-c',remote],stdin=subprocess.PIPE,stdout=output,stderr=error)
  (folder/'process.json').write_text(json.dumps({'at':start.isoformat(),'host_child_pid':proc.pid,'purpose':'bounded local raw prompt token proxy'},indent=2)+'\n')
  proc.communicate(json.dumps({'request':request,'expected_digest':protocol['model_digest'],'target_sha256':target['target_sha256']},ensure_ascii=False).encode(),timeout=180)
 end=datetime.now(timezone.utc);body=(folder/'raw-response.json').read_bytes()
 outcome={'at':end.isoformat(),'started_at':start.isoformat(),'returncode':proc.returncode,'wall_seconds':time.monotonic()-wall,'kind':'RAW_TOKEN_BUDGET_PROXY_NOT_DOCUMENT_EVALUATION','raw_response_sha256':hashlib.sha256(body).hexdigest(),'training_steps':0,'gold':False,'fits_sequence512_training':None}
 if proc.returncode==0:
  result=json.loads(body)
  for key in ['model','done','done_reason','prompt_eval_count','eval_count']:assert key in result,key
  outcome.update({key:result.get(key) for key in ['model','done','done_reason','prompt_eval_count','prompt_eval_cached_count','eval_count','total_duration','load_duration','prompt_eval_duration','eval_duration']})
  outcome['status']='TERMINAL_RAW_INFERENCE_PROXY_NOT_TRAINING_FIT' if result['done'] and result['eval_count']<=1 else 'UNEXPECTED_STOP_REMAINING_CALLS'
 else:outcome['status']='TRANSPORT_FAILED_NO_RETRY_REMAINING_CALLS_ABORTED'
 (folder/'outcome.json').write_text(json.dumps(outcome,indent=2)+'\n')
 print(json.dumps({'repository':target['repository'],'status':outcome['status'],'input_tokens_reported':outcome.get('prompt_eval_count'),'output_tokens_reported':outcome.get('eval_count'),'wall_seconds':outcome['wall_seconds']}),flush=True)
 if outcome['status']!='TERMINAL_RAW_INFERENCE_PROXY_NOT_TRAINING_FIT':raise SystemExit(2)
