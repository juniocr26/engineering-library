from pathlib import Path
import json,hashlib,datetime,importlib.util,tarfile
P=Path(__file__).resolve().parent;proto=P/'weekend-capsule-admission-controls-protocol-v1.json';d=json.loads(proto.read_bytes());script=P/'consume_weekend_capsule_v1.py';assert hashlib.sha256(script.read_bytes()).hexdigest()==d['consumer_source_sha256'];spec=importlib.util.spec_from_file_location('owned_capsule_consumer',script);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def member(name='a',size=1,mode=0o600,kind=tarfile.REGTYPE):
 t=tarfile.TarInfo(name);t.size=size;t.mode=mode;t.type=kind;return t
manifest={'a':{'path':'a','bytes':1,'mode':0o600,'sha256':'unused_header_only'}};rows=[]
for c in d['cases']:
 name=c['id'];members=[member()];mf=manifest;maxn=10;maxb=10
 if name=='absolute-name':members=[member('/private/tmp/escape')]
 elif name=='parent-traversal':members=[member('../escape')]
 elif name=='dot-prefix':members=[member('./a')]
 elif name=='symlink':members=[member(kind=tarfile.SYMTYPE)]
 elif name=='hardlink':members=[member(kind=tarfile.LNKTYPE)]
 elif name=='duplicate':members=[member(),member()]
 elif name=='unlisted':members=[member('b')]
 elif name=='wrong-size':members=[member(size=2)]
 elif name=='wrong-mode':members=[member(mode=0o644)]
 elif name=='missing':members=[]
 elif name=='member-bound':maxn=0
 elif name=='byte-bound':maxb=0
 actual=None
 try:m.validate_members(members,mf,maxn,maxb)
 except ValueError as e:actual=str(e)
 rows.append({'id':name,'expected_refusal':c['expected_refusal'],'actual_refusal':actual,'matched':actual==c['expected_refusal']})
assert all(r['matched'] for r in rows)
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':hashlib.sha256(proto.read_bytes()).hexdigest(),'consumer_source_sha256':d['consumer_source_sha256'],'cases':rows,'matched_controls':len(rows),'normal_controls_admitted':1,'negative_controls_refused':12,'extraction_roots_created':0,'framework_or_model_calls':0,'security_crash_or_remote_certification':False}
with (P/'weekend-capsule-admission-controls-results-v1.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in out.items() if k!='cases'}))
