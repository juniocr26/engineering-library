"""Bounded research inference; frozen public requests, existing local container only."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--method', required=True, choices=list('L'))
args = parser.parse_args()
protocol_path = HERE / 'source-only-fact-render-protocol-v1.json'
protocol = json.loads(protocol_path.read_text())
calls = protocol.get('calls', protocol.get('conditions', []))
transport_timeout = protocol.get('transport_timeout_seconds', 900)

def write_new(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')

for item in calls:
    if item['method'] != args.method:
        continue
    request_path = ROOT / item['request']
    raw_request = request_path.read_bytes()
    if hashlib.sha256(raw_request).hexdigest() != item['request_sha256']:
        raise RuntimeError('Frozen request hash mismatch')
    folder = request_path.parent
    if (folder / 'started.json').exists():
        raise RuntimeError('Refuse repeated request; inspect preserved state')
    request = json.loads(raw_request)
    if request['model'] != protocol['model'] or request['stream'] is not False:
        raise RuntimeError('Unexpected model or streaming configuration')
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    write_new(folder / 'started.json', {
        'at': started, 'request_sha256': item['request_sha256'],
        'state': 'STARTED_NOT_ACCEPTED', 'method': args.method,
        'task': item['task'], 'optimizer_updates': 0,
    })
    worker = '''import json,sys,urllib.request
request=json.loads(sys.stdin.buffer.read())
tags=json.load(urllib.request.urlopen('http://ollama:11434/api/tags',timeout=10))
if not any(m.get('name')==%r and m.get('digest')==%r for m in tags.get('models',[])):
    raise RuntimeError('Frozen model digest unavailable')
req=urllib.request.Request('http://ollama:11434/api/chat',data=json.dumps(request).encode(),headers={'Content-Type':'application/json'},method='POST')
try:
    with urllib.request.urlopen(req,timeout=%d) as response:
        sys.stdout.buffer.write(response.read())
except urllib.error.HTTPError as error:
    sys.stdout.buffer.write(error.read())
    print('HTTP_ERROR_STATUS=' + str(error.code), file=sys.stderr)
    raise SystemExit(17)
''' % (protocol['model'], protocol['model_digest'], transport_timeout)
    # Script is fixed code, request remains JSON data on stdin; no source is executed.
    command = ['/usr/local/bin/docker', 'exec', '-i',
               'engineering-library-backend-1', 'python3', '-c', worker]
    monotonic = time.monotonic()
    timed_out = False
    with (folder / 'raw-response.json').open('xb') as output, (folder / 'transport.stderr').open('xb') as error:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=output, stderr=error)
        write_new(folder / 'process.json', {'pid': process.pid, 'started_at': started,
                                          'container': 'engineering-library-backend-1'})
        try:
            process.communicate(raw_request, timeout=transport_timeout + 30)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    outcome = {'started_at': started, 'ended_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'wall_seconds': time.monotonic() - monotonic, 'exit_code': process.returncode,
               'host_timeout': timed_out, 'task': item['task'], 'method': args.method,
               'request_sha256': item['request_sha256'],
               'raw_response_sha256': hashlib.sha256((folder / 'raw-response.json').read_bytes()).hexdigest(),
               'complete_document_accepted': None, 'owner_approved': False,
               'training_gold': False, 'optimizer_updates': 0,
               'state': 'TRANSPORT_FAILED_NO_RETRY' if process.returncode else 'PENDING_SEMANTIC_REVIEW'}
    if process.returncode == 0:
        try:
            response = json.loads((folder / 'raw-response.json').read_text())
            outcome.update({k: response.get(k) for k in ['done', 'done_reason', 'eval_count',
                            'prompt_eval_count', 'total_duration', 'eval_duration', 'prompt_eval_duration']})
            content = response.get('message', {}).get('content', '')
            with (folder / 'model-content.txt').open('x') as stream:
                stream.write(content)
            try:
                json.loads(content)
                outcome['content_json_valid'] = True
            except (ValueError, TypeError):
                outcome['content_json_valid'] = False
        except (ValueError, KeyError, TypeError) as exc:
            outcome['response_parse_error'] = type(exc).__name__
    write_new(folder / 'outcome.json', outcome)
    print(json.dumps(outcome), flush=True)
    if process.returncode != 0 and not timed_out:
        raise SystemExit('Stop this batch after transport failure; preserve remaining requests as NOT_STARTED pending resource observation. No retry.')
    if timed_out:
        raise SystemExit('Local worker terminated; backend inference status uncertain. No further requests until observation.')
