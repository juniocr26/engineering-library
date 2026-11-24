"""Research-only parsing of public evidence and candidate fragments; never import them."""
import ast
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

P=Path(__file__).resolve().parent
examples=json.loads((P/'candidate-example-inputs-v1.json').read_text())
manifest=json.loads((P/'source-freeze-v1.json').read_text())['files']
python_rows=[]
for row in examples:
    if row['repository']!='fastapi': continue
    try:
        ast.parse(row['example'])
        status='SYNTAX_PARSES'
    except SyntaxError as e:
        status='SYNTAX_ERROR:'+str(e)
    python_rows.append({'path':row['path'],'status':status,'execution':False,'scope':'Python syntax only; no imports or dependency resolution'})
inputs=[]
for row in examples:
    if row['repository']=='zod': inputs.append({'path':row['path']+'-example.mts','source':row['example'],'kind':'example'})
for row in manifest:
    if row['repository']=='zod' and row['path'].endswith('.ts'):
        inputs.append({'path':row['path'],'source':Path(row['evidence_path']).read_text(),'kind':'public-source'})
program='''const fs=require("node:fs"),ts=require("typescript");
const inputs=JSON.parse(fs.readFileSync(0,"utf8"));
const rows=inputs.map(row=>{const file=ts.createSourceFile(row.path,row.source,ts.ScriptTarget.Latest,true,ts.ScriptKind.TS);return {path:row.path,kind:row.kind,parse_diagnostics:file.parseDiagnostics.map(d=>({code:d.code,message:ts.flattenDiagnosticMessageText(d.messageText," ")})),execution:false}});
console.log(JSON.stringify({node:process.version,typescript:ts.version,rows}));'''
r=subprocess.run(['docker','exec','-i','engineering-library-frontend-1','node','-e',program],input=json.dumps(inputs).encode(),capture_output=True,timeout=30)
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':python_rows,'typescript_transport_returncode':r.returncode,'typescript':json.loads(r.stdout) if r.returncode==0 else None,'stderr':r.stderr.decode(),'go_examples':'NOT_PARSED: no native Go tool available in inspected host/backend paths','limits':'Parsing is not typechecking, module resolution, source execution, runtime correctness or general documentation acceptance. Duplicated EN/PT fragments are not independent cases.','external_project_tests_run':False}
(P/'candidate-syntax-observations-v1.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
