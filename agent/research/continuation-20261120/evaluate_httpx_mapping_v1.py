"""Run the frozen registry cuts through a post-exposure mapping profile."""
import datetime,hashlib,importlib.util,json
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('public_mapping_observer',P/'transport_mapping_observer_v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
oracle=json.loads((P/'httpx-cross-file-oracle-v1.json').read_text());rows=[]
for cut in oracle['revisions']:
 base=P/'new-public-sources-v1/encode--httpx'/cut['revision'];registry={}
 for name,digest in cut['source_sha256'].items():
  source=(base/name).read_text();assert hashlib.sha256(source.encode()).hexdigest()==digest;registry[name]={'source':source,'sha256':digest,'revision':cut['revision']}
 result=m.observe(registry)
 checks={'admitted':result['status']=='WRITTEN_MAPPING_FACTS'}
 if checks['admitted']:
  expected=cut['expected'];checks.update(mapping_pair_count=result['mapping_pair_count']==expected['mapping_pairs'],initialization=result['initialization']==expected['initialization'],loader=result['loader_function']==expected['loader_function'],handler_type=result['handler']['caught_type_expression']==expected['handler_type'],unmapped_bare_raise=result['handler']['unmapped']==expected['unmapped_path'],mapped_cause=result['handler']['translated_raise']==expected['mapped_path'],specificity=result['handler']['specificity_condition']=='mapped_exc is None or '+expected['specificity_condition'],declared_requesterror_ancestry=result['all_mapped_targets_have_declared_requesterror_ancestor']is True)
 rows.append({'tag':cut['tag'],'revision':cut['revision'],'checks':checks,'all_match':all(checks.values()),'result':result})
pairs=[[(p['source_expression'],p['target_declared_class'])for p in r['result'].get('mapping_pairs',[])]for r in rows]
joint={'same_nonempty_ordered_mapping_pairs':bool(pairs[0])and pairs[0]==pairs[1],'initialization_changed':rows[0]['result'].get('initialization')!=rows[1]['result'].get('initialization')}
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'classification':'POST_EXPOSURE_CROSS_FILE_SOURCE_PROFILE_DEVELOPMENT_NOT_GENERAL_ARCHITECTURE_ACCURACY','rows':rows,'joint_checks':joint,'all_checks_match':all(r['all_match']for r in rows)and all(joint.values()),'checks_count':sum(len(r['checks'])for r in rows)+len(joint),'source_executed':False,'http_application_requests':0,'packages_installed':False,'model_calls':0,'producer_sha256':hashlib.sha256((P/'transport_mapping_observer_v1.py').read_bytes()).hexdigest(),'unimplemented_oracle_fields':'Request-context sibling hierarchy and caller/close with-boundaries will be separately observed; not silently credited to this extractor.'}
with(P/'httpx-mapping-results-v1.json').open('x')as stream:stream.write(json.dumps(record,indent=2)+'\n')
print(json.dumps({'all_checks_match':record['all_checks_match'],'checks':record['checks_count'],'statuses':[r['result']['status']for r in rows],'reasons':[r['result'].get('reason')for r in rows]}))
