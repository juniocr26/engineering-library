"""Research-only single-condition Ollama inference via the existing container."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import time

P = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--method', choices=['whole-document', 'structured-claims', 'verifier-canaries', 'section-simple', 'section-allowlist', 'section-bounds', 'section-composition', 'section-legacy', 'cache-grounded-faq', 'click-boolean', 'click-categorical'], required=True)
args = parser.parse_args()
if args.method == 'verifier-canaries':
    protocol = json.loads((P / 'verifier-canary-request-freeze-v1.json').read_text())
    item = {'request': protocol['request'], 'sha256': protocol['sha256']}
elif args.method.startswith('click-'):
    protocol = json.loads((P / 'click-encoding-comparison-protocol-v1.json').read_text())
    item = next(r for r in protocol['requests'] if r['method'] == args.method)
elif args.method == 'cache-grounded-faq':
    protocol = json.loads((P / 'cache-grounded-faq-protocol-v1.json').read_text())
    item = {'request': protocol['request'], 'sha256': protocol['sha256']}
elif args.method.startswith('section-'):
    protocol = json.loads((P / 'section-generation-protocol-v1.json').read_text())
    item = next(r for r in protocol['requests'] if r['method'] == args.method)
else:
    protocol = json.loads((P / 'model-method-comparison-protocol-v1.json').read_text())
    item = next(r for r in protocol['requests'] if r['method'] == args.method)
request_path = Path(item['request'])
assert hashlib.sha256(request_path.read_bytes()).hexdigest() == item['sha256']
request = json.loads(request_path.read_text())
assert request['model'] == 'llama3.2:3b' and request['stream'] is False
folder = request_path.parent
if (folder / 'started.json').exists():
    raise SystemExit('Refuse repeat: inspect preserved live/terminal handle before any new condition.')
start = datetime.datetime.now(datetime.timezone.utc)
(folder / 'started.json').write_text(json.dumps({'at': start.isoformat(), 'request_sha256': item['sha256'], 'method': args.method, 'state': 'STARTED_NOT_RESULT', 'no_training': True}, indent=2)+'\n')
# Source is a serialized public-data request, never evaluated as application code.
worker = '''import json,urllib.request,sys
req = json.loads(%r)
model = json.load(urllib.request.urlopen("http://ollama:11434/api/tags",timeout=10))
assert any(m.get("name")=="llama3.2:3b" and m.get("digest")==%r for m in model.get("models",[])), "model digest changed"
r=urllib.request.Request("http://ollama:11434/api/chat",data=json.dumps(req).encode(),headers={"Content-Type":"application/json"},method="POST")
with urllib.request.urlopen(r,timeout=2100) as response:
    sys.stdout.buffer.write(response.read())
''' % (json.dumps(request, ensure_ascii=False), protocol['model_digest'])
wall = time.monotonic()
with (folder / 'raw-response.json').open('xb') as output, (folder / 'transport.stderr').open('xb') as error:
    proc = subprocess.Popen(['docker','exec','-i','engineering-library-research-1','python3','-'], stdin=subprocess.PIPE, stdout=output, stderr=error)
    (folder / 'process.json').write_text(json.dumps({'at': start.isoformat(), 'host_child_pid': proc.pid, 'command': ['docker','exec','-i','engineering-library-research-1','python3','-'], 'method':args.method}, indent=2)+'\n')
    proc.communicate(worker.encode())
end = datetime.datetime.now(datetime.timezone.utc)
result = {'at':end.isoformat(),'started_at':start.isoformat(),'method':args.method,'returncode':proc.returncode,'wall_seconds':time.monotonic()-wall,'status':'TRANSPORT_FINISHED_PENDING_DOCUMENT_REVIEW' if proc.returncode==0 else 'TRANSPORT_FAILED_NO_AUTOMATIC_RETRY','owner_approved':False,'training_gold':False,'optimizer_steps':0,'raw_response_sha256':hashlib.sha256((folder/'raw-response.json').read_bytes()).hexdigest()}
if proc.returncode==0:
    raw=json.loads((folder/'raw-response.json').read_text())
    result.update({k:raw.get(k) for k in ['done','done_reason','eval_count','prompt_eval_count','total_duration','load_duration','prompt_eval_duration','eval_duration']})
    (folder/'model-content.txt').write_text(raw.get('message',{}).get('content',''))
(folder/'outcome.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2),flush=True)
