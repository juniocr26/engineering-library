"""Read-only Linux execution of the same two registered source-binding cases."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
protocol=json.loads((P/'registered-slugify-real-protocol-v1.json').read_text())
for source in protocol['registration']['sources'].values():
    source['root']='/sources/engineering-library/'+str(Path(source['root']).relative_to(ROOT))
program='''import datetime,hashlib,importlib.util,json,platform,sys
from pathlib import Path
p=Path("/sources/engineering-library/agent/research/continuation-20261120")
protocol=json.load(sys.stdin)
source=p/"registered_declaration_binding_v2.py"
if hashlib.sha256(source.read_bytes()).hexdigest()!=protocol["producer_sha256"]:raise ValueError("producerdrift")
s=importlib.util.spec_from_file_location("bound_linux",source);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
tool=m.RegisteredDeclaration(protocol["registration"]);rows=[]
for case in protocol["cases"]:
 result=tool.decide(case["packet"])
 rows.append({"id":case["id"],"expected":case["expected"],"matches":result["action"]==case["expected"]and result["physical_source_bytes_and_registered_paths_verified"]is True,"result":result})
print(json.dumps({"at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"platform":platform.platform(),"python":sys.version,"rows":rows,"correct":sum(x["matches"]for x in rows),"n":len(rows),"source_executed":False,"physical_documentation_certified":False,"upstream_git_revision_authenticated":False,"new_independent_case_count":0}))
'''
command=['docker','exec','-i','-w','/app/backend','engineering-library-backend-1','python3','-c',program]
result=subprocess.run(command,input=json.dumps(protocol).encode(),capture_output=True,timeout=30)
(P/'registered-slugify-real-linux-v1.stdout').write_bytes(result.stdout);(P/'registered-slugify-real-linux-v1.stderr').write_bytes(result.stderr)
if result.returncode:raise ValueError('Linuxread-onlybindingprobe failed;rawoutputs retained')
body=json.loads(result.stdout)
with(P/'registered-slugify-real-linux-v1.json').open('x')as stream:json.dump(body,stream,indent=2)
print(json.dumps({'correct':body['correct'],'n':body['n'],'python':body['python'].split()[0],'actions':[r['result']['action']for r in body['rows']]}))
