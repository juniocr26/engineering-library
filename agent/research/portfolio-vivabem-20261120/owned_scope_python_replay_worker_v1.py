import sys,json,hashlib,platform
x=json.load(sys.stdin);out={"python":platform.python_version(),"platform":platform.platform(),"versions":{}}
for name,source in x["observers"].items():
 ns={"__name__":"owned_scope_replay"};exec(compile(source,name,"exec"),ns);rows=[]
 for r in x["inputs"]["cases"]:
  actual=ns["observe"](r["packet"],r["trusted_acquisition"]);rows.append({"id":r["id"],"expected":r["expected"],"actual":actual,"match":actual==r["expected"]})
 out["versions"][name]={"source_sha256":hashlib.sha256(source.encode()).hexdigest(),"rows":rows}
print(json.dumps(out,sort_keys=True))
