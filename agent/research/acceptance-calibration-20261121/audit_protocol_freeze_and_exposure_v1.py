"""Bind every terminal request to its preprediction design and development family."""
from pathlib import Path
from collections import Counter
import datetime,hashlib,json
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
ledger=json.loads((P/'current-campaign-inference-ledger-v2.json').read_text())
protocol_names=[
 'generation-comparison-protocol-v1.json','schema-comparison-protocol-v1.json',
 'semantic-verifier-comparison-protocol-v1.json','semantic-verifier-resource-protocol-v2.json',
 'semantic-verifier-label-only-protocol-v2.json','actual-generated-claim-verifier-protocol-v2.json',
 'source-only-fact-render-protocol-v1.json','source-question-repair-protocol-v1.json',
 'mechanical-source-prose-protocol-v1.json','multiple-choice-source-relations-protocol-v1.json',
 'relation-option-order-protocol-v1.json','verified-fact-render-protocol-v1.json',
 'line-addressed-source-copy-protocol-v1.json','provided-source-line-copy-protocol-v1.json']
by_request={};protocols=[]
for name in protocol_names:
 path=P/name;raw=path.read_bytes();d=json.loads(raw)
 at=d.get('frozen_at',d.get('at'))
 calls=d.get('calls',d.get('conditions',[]))
 record={'path':name,'sha256':hashlib.sha256(raw).hexdigest(),'declared_freeze_at':at,
         'frozen_request_count':len(calls),'terminal_count':0,'unstarted_count':0}
 protocols.append(record)
 for call in calls:
  path=(ROOT/call['request']).resolve()
  assert path not in by_request,(name,path)
  by_request[path]=(record,call)
families={'fastapi':'source-repository:fastapi','cobra':'source-repository:cobra','zod':'source-repository:zod'}
rows=[]
for attempt in ledger['attempts']:
 folder=Path(attempt['folder']);request=folder/'request.json';started=json.loads((folder/'started.json').read_text())
 protocol,call=by_request[request.resolve()]
 source_family=next((families[t]for t in families if attempt['task'].startswith(t)),None)
 assert source_family is not None,attempt['task']
 start=started.get('at',started.get('started_at'));assert start is not None
 freeze_time=datetime.datetime.fromisoformat(protocol['declared_freeze_at'].replace('Z','+00:00'))
 start_time=datetime.datetime.fromisoformat(start.replace('Z','+00:00'))
 actual=hashlib.sha256(request.read_bytes()).hexdigest()
 matches=actual==call['request_sha256']==attempt['request_sha256']
 rows.append({'request':str(request.relative_to(ROOT)),'group':attempt['group'],'task':attempt['task'],
              'source_family':source_family,'source_role':'DEVELOPMENT_EXPOSED_TRAINING_EXCLUDED',
              'protocol':protocol['path'],'protocol_sha256':protocol['sha256'],
              'declared_frozen_at':protocol['declared_freeze_at'],'request_started_at':start,
              'freeze_precedes_start':freeze_time<start_time,'frozen_request_hash_matches':matches,
              'request_sha256':actual,'owner_approved':False,'gold':False,
              'independent_evaluation_eligible':False,'neural_optimization_use_authorized':False})
 protocol['terminal_count']+=1
for protocol in protocols:protocol['unstarted_count']=protocol['frozen_request_count']-protocol['terminal_count']
metadata=json.loads((P/'dataset-quality-audit-v1.json').read_text())['records_metadata']
components=json.loads((P/'dataset-provenance-graph-results-v2.json').read_text())['components']
row_component={id:component['id']for component in components for id in component['rows']}
links=[]
for family in families.values():
 selected=[r for r in metadata if r['family']==family]
 links.append({'family':family,'original_record_ids':[r['id']for r in selected],
               'original_strong_components':sorted({row_component[r['id']]for r in selected}),
               'original_roles_unchanged':True,'all_current_requests_training_excluded':True,
               'request_count':sum(r['source_family']==family for r in rows),
               'related_family_review_required':['source-repository:starlette']if family.endswith(':fastapi')else[]})
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocols':protocols,'requests':rows,
 'terminal_requests':len(rows),'all_terminal_requests_bound_to_exactly_one_protocol':len(rows)==98,
 'all_recorded_freezes_precede_request_starts':all(r['freeze_precedes_start']for r in rows),
 'all_frozen_request_hashes_match':all(r['frozen_request_hash_matches']for r in rows),
 'development_family_counts':dict(Counter(r['source_family']for r in rows)),
 'original_dataset_family_links':links,
 'not_an_independent_holdout':'Everycurrentrequestisdevelopmentexposed. No same/revised/translated/chapter-FAQderivative becomesholdoutbyfilenameornewrevision. FastAPI/Starlettedependencyrequiresfamilyadjudication; original17strongcomponentsarenotcompleteindependenceproof.',
 'protected_reserves':'No request assignedtoesp-halorcachetools. Thisisrequest/protocolprovenance,notcryptographicproofthatnoarbitrarysubstringcouldoverlapothercode. Cachetools12originalrowsretainstructuralevalrole; oldcachetoolsdiagnosticexposuremeansnotfreshsemanticfamilyholdout.',
 'temporal_evidence_limit':'DeclaredISOtimestampsplusrequesthashesarelocalprovenance,notexternaltrustedtimestampattestation. Currentprotocolhashesdonotcryptographicallyproveeveryearlierreferencefilewasneveredited; preservedfreezes/checkpoints/providerawhistory. No inference rerun.',
 'current_request_promotion_to_training':0,'original_record_mutations':0,'model_calls':0,'gold':0,'optimizer_updates':0}
with(P/'protocol-freeze-and-exposure-audit-v1.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps({k:v for k,v in result.items()if k not in ['protocols','requests','original_dataset_family_links']},indent=2))
