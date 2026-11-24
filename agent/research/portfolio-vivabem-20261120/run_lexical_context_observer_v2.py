from pathlib import Path
import json,subprocess,sys
p=Path(__file__).parent
mode=sys.argv[1]
if mode=='controls':
 files=[{'name':'owned-controls.js','source':(p/'lexical-call-context-owned-controls-v1.js').read_text()},{'name':'owned-invalid.js','source':'function invalid( {'}]
elif mode=='example':
 files=[{'name':'owned-example.js','source':(p/'fastify-route-context-example-v1.js').read_text()}]
elif mode=='fastify':
 files=[{'name':n,'source':(p/'fastify-route-context-v1'/n).read_text()} for n in ['route.js','fastify.js']]
else: raise SystemExit('unknown mode')
out=p/('lexical-call-context-'+mode+'-observation-v1.json')
assert not out.exists(),out
code='const payload = '+json.dumps({'files':files})+';\n'+(p/'lexical_call_context_observer_v1.cjs').read_text()
r=subprocess.run(['docker','exec','-i','engineering-library-frontend-1','node','-'],input=code,text=True,capture_output=True,timeout=30)
(p/('lexical-call-context-'+mode+'-stderr-v1.txt')).write_text(r.stderr)
assert r.returncode==0,r.stderr
result=json.loads(r.stdout);out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'output':str(out),'files':len(result['files']),'calls':[len(f['calls']) for f in result['files']],'parse_diagnostics':[len(f['parse_diagnostics']) for f in result['files']]}))
