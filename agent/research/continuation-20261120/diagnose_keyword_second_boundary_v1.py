"""Expose the typed keyword predicate boundary after whole-unit admission succeeds."""
import datetime,hashlib,importlib.util,json
from pathlib import Path
P=Path(__file__).resolve().parent
before="def remap(root, **kwargs):\n    flag = kwargs.pop('flag', True)\n    if kwargs:\n        raise TypeError('unexpected keyword arguments: %r' % kwargs.keys())\n    return root\n"
after="def remap(root, **kwargs):\n    flag = kwargs.pop('flag', True)\n    trace = kwargs.pop('trace', ())\n    if kwargs:\n        raise TypeError('unexpected keyword arguments: %r' % kwargs.keys())\n    return root\n"
protocol={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hypothesis':'The rejects-keyword typed claim is listed in validate_claim but has no recommendation branch, so solving the remap quote boundary alone cannot produce the expected action.','before':before,'after':after,'paired_claim':{k:{'kind':'rejects-keyword','keyword':'trace'}for k in ['en','pt-br']},'expected_action':'MODIFY','frozen_before_recommendation':True,'scope':'Owned minimal code, no execution. Not a rerun or alteration of the original frozen public oracle.'}
with(P/'keyword-second-boundary-protocol-v1.json').open('x')as f:f.write(json.dumps(protocol,indent=2)+'\n')
spec=importlib.util.spec_from_file_location('keyword_boundary_engine',P/'typed_module_lifecycle_v5.py');engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
def card(s):return{'source':s,'path':'owned_keyword.py','revision':'owned-sha256:'+hashlib.sha256(s.encode()).hexdigest(),'sha256':hashlib.sha256(s.encode()).hexdigest()}
result=engine.recommend(card(before),card(after),'remap',protocol['paired_claim']);assert all(e['status']=='WRITTEN_CALLABLE_FACTS'for e in result['evidence'].values());assert result['action']=='INCONCLUSIVE'and result['reason']=='typed predicate outside admitted profile'
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'result':result,'expected_action':protocol['expected_action'],'first_quote_boundary_avoided':True,'second_boundary_observed':'Recognized typed predicate schema has no implementation branch.','engine_sha256':hashlib.sha256((P/'typed_module_lifecycle_v5.py').read_bytes()).hexdigest(),'source_executed':False,'original_frozen_oracle_or_core_changed':False}
with(P/'keyword-second-boundary-results-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print(json.dumps({'action':result['action'],'reason':result['reason'],'both_source_fact_statuses':'WRITTEN_CALLABLE_FACTS'}))
