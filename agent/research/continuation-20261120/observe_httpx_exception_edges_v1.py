"""Six frozen owned exception-shape observations; reuse the reviewed source loader."""
import datetime,hashlib,json,platform,sys
from pathlib import Path
P=Path(__file__).resolve().parent
protocol=json.loads((P/'httpx-exception-edge-protocol-v1.json').read_text())
loader=P/'observe_httpx_exception_composition_v1.py';raw=loader.read_bytes()
assert hashlib.sha256(raw).hexdigest()==protocol['driver_sha256']
assert hashlib.sha256((P/'httpx-exception-composition-protocol-v1.json').read_bytes()).hexdigest()==protocol['source_protocol_sha256']
# Execute the already reviewed loader only, stopping before its original case loop.
prefix=raw.decode().split('\nrows=[]\n')[0]
assert prefix.endswith('return ns,calls,marker\n')
env={'__file__':str(loader),'__name__':'owned_source_loader_for_edge_observations'}
exec(compile(prefix,str(loader),'exec'),env)
rows=[]
for case in protocol['cases']:
    ns,calls,marker=env['namespace']()
    bases=tuple(env['core'][name]for name in case['bases'])
    owned_error=ValueError('owned __str__ failure')
    behavior=case.get('str_behavior')
    methods={}
    if behavior=='raise-owned-valueerror':
        def convert(self):raise owned_error
        methods['__str__']=convert
    elif behavior=='return-integer':methods['__str__']=lambda self:7
    elif behavior=='return-fixed-unicode':methods['__str__']=lambda self:'valor transformado — owned ✓'
    owned=type('OwnedExceptionShape',bases,methods)('owned input'if behavior else case['message'])
    try:
        with ns['map_httpcore_exceptions']():raise owned
    except BaseException as result:
        target=({'ValueError':ValueError,'TypeError':TypeError}.get(case['target'])or ns[case['target']])
        checks={'exact_target':type(result)is target}
        if behavior in ['raise-owned-valueerror','return-integer']:
            checks.update({'original_context':result.__context__ is owned,'no_explicit_cause':result.__cause__ is None})
            if behavior=='raise-owned-valueerror':checks['owned_valueerror_identity']=result is owned_error
        else:
            checks.update({'exact_message':str(result)==case['message'],'original_explicit_cause':result.__cause__ is owned})
        rows.append({'id':case['id'],'checks':checks,'all_pass':all(checks.values()),'observed_class':type(result).__name__,'observed_message':str(result)})
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.version,'platform':platform.platform(),'cases':rows,'all_pass':all(r['all_pass']for r in rows),'new_distinct_cases':6,'selected_source_executed':True,'whole_packages_imported':False,'application_http_requests':0,'training_excluded':True,'owner_approved':False,'limitations':'Synthetic subclasses and message conversions inside owned namespaces; not an installed package, production transport, or upstream bug demonstration.'}
with(P/'httpx-exception-edge-results-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'cases':len(rows),'all_pass':record['all_pass']})
