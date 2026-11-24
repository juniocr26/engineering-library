import sys,json,hashlib,platform
x=json.load(sys.stdin);ns={"__name__":"owned_scope_replay"};exec(compile(x["source"],"observe_owned_scope_v3.py","exec"),ns);out={"python":platform.python_version(),"platform":platform.platform(),"source_sha256":hashlib.sha256(x["source"].encode()).hexdigest(),"original":[],"conflicts":[]}
for r in x["inputs"]["cases"]:
 actual=ns["observe"](r["packet"],r["trusted_acquisition"]);out["original"].append({"id":r["id"],"expected":r["expected"],"actual":actual,"match":actual==r["expected"]})
before={"old.py":"def answer():\n    return 7\n"}
for r in x["conflicts"]["cases"]:
 trusted={"complete_acquisition":True,"before_digest":ns["digest"](before),"after_digest":ns["digest"](r["after"]),"retirement":r["retirement"]};actual=ns["observe"]({"before":before,"after":r["after"],"selector":"old.py:answer"},trusted);out["conflicts"].append({"id":r["id"],"expected":r["expected"],"actual":actual,"match":actual==r["expected"]})
print(json.dumps(out,sort_keys=True))
