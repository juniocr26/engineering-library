import sys,json,types,platform,hashlib
payload=json.load(sys.stdin)
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(payload['module_source'].encode())==payload['module_sha256']
fact_bytes=payload['fact_text'].encode()
assert sha(payload['primary_contract_text'].encode())==json.loads(fact_bytes)['evidence_sha256']
module=types.ModuleType('recovered_owned_guard_domain')
exec(compile(payload['module_source'],'<archived-owned-guard-domain>','exec'),module.__dict__)
math=[]
for case in payload['math_controls']:
 result=module.compare_thresholds(case['old_threshold'],case['new_threshold'],case['intervals'],case['complete'])
 math.append({'id':case['id'],'actual':result})
source=[]
for recipe in payload['source_recipes']:
 before=payload['before_source'];after=payload['after_source'];facts=fact_bytes
 for op in recipe['operations']:
  if op['kind']=='replace_once':
   assert op['target']=='after_source' and after.count(op['old'])==1
   after=after.replace(op['old'],op['new'],1)
  elif op['kind']=='append_utf8':
   assert op['target']=='fact_bytes'
   facts+=op['text'].encode()
  else:raise ValueError('unknown operation')
 hashes={'before_sha256':sha(before.encode()),'after_sha256':sha(after.encode()),'fact_sha256':sha(facts)}
 assert hashes==payload['original_input_hashes'][recipe['id']]
 result=module.observe_source_pair(before,after,facts,payload['config'])
 source.append({'id':recipe['id'],'actual':result,**hashes})
projection={'math':math,'source':source}
canonical=json.dumps(projection,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
print(json.dumps({'runtime':{'python':platform.python_version(),'system':platform.system(),'machine':platform.machine(),'isolated':sys.flags.isolated,'dont_write_bytecode':sys.dont_write_bytecode},'module_sha256':payload['module_sha256'],'math_cases':len(math),'source_cases':len(source),'projection':projection,'canonical_fingerprint':sha(canonical),'execution':'OwnedPythonprototypeonly;SQLXGosourceinerttext,nodatabase/model/network/appimports.'},indent=2,ensure_ascii=False))
