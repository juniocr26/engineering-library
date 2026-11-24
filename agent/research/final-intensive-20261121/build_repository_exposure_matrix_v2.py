"""Append a conservative current exposure overlay; preserve prior registries."""
from pathlib import Path
import collections
import datetime
import hashlib
import json

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
protocol=json.loads((P/'repository-exposure-matrix-protocol-v1.json').read_text())
for reference in protocol['inputs']:
    assert sha(ROOT/reference['path'])==reference['sha256']
baseline=json.loads((P/'baseline-verification-v1.json').read_text())
archive=json.loads((P/'archived-family-exposure-integrity-results-v2.json').read_text())
graph=json.loads((ROOT/'agent/research/acceptance-calibration-20261121/dataset-provenance-graph-results-v2.json').read_text())
old=json.loads((ROOT/'agent/research/portfolio-vivabem-20261120/evaluation-role-registry-v9.json').read_text())
oldroles={r['repository']:r for r in old['roles']}
archivecounts=collections.Counter(r['repository'] for r in archive['records'] if r['status']=='MATCH')
old_root='agent/research/portfolio-vivabem-20261120/'
prior='agent/research/acceptance-calibration-20261121/'
modelpaths={
    'click':[old_root+'click-encoding-comparison-v1/click-boolean/request.json',
             old_root+'click-encoding-comparison-v1/click-categorical/request.json'],
    'axum':[old_root+'axum-reserved-judgment-v1/request.json'],
    **{name:[prior+f'generation-v1/{name}/E/request.json'] for name in ['fastapi','cobra','zod']},
}
rows=[]
for repo in baseline['repositories']:
    name=repo['repository']
    oldrole=oldroles[name]
    upstream=oldrole['upstream_identity']
    aliases={'source-repository:'+name}
    if isinstance(upstream,str):aliases.add('source-repository:'+upstream)
    components=[c for c in graph['components'] if set(c['families']) & aliases]
    dataset_rows=sum(c['record_count'] for c in components)
    requests=[{'path':n,'sha256':sha(ROOT/n)} for n in modelpaths.get(name,[])]
    catalog=ROOT/'docs'/name
    private=repo['collection']=='Projeto VivaBem' and name!='engineering-library'
    if private:current='PRIVATE_METADATA_ONLY_NO_INFERENCE_NO_TRAINING'
    elif name=='engineering-library':current='INTERNAL_DEVELOPMENT_NOT_INDEPENDENT'
    elif dataset_rows or archivecounts[name] or requests:current='CONFIRMED_PRIOR_SOURCE_OR_MODEL_EXPOSURE'
    elif name=='raylib':current='PROSPECTIVE_EVALUATION_ONLY_REFERENCE_PREPARATION_NOT_CERTIFIED'
    elif catalog.is_dir():current='CATALOG_DOCUMENTED_EXPOSURE_UNRESOLVED'
    else:current='EXPOSURE_UNRESOLVED_NOT_CERTIFIED'
    rows.append({'repository':name,'collection':repo['collection'],'upstream_identity':upstream,
                 'head_at_current_baseline':repo['head'],'older_role':oldrole['role'],'current_role':current,
                 'original_dataset_component_rows':dataset_rows,
                 'original_dataset_components':[c['id'] for c in components],
                 'verified_archived_public_snapshots':archivecounts[name],
                 'confirmed_prior_model_request_evidence':requests,
                 'local_model_request_status':'CONFIRMED_SELECTED_EXAMPLES' if requests else 'NOT_INFERRED_FROM_DATASET_OR_HASHES',
                 'existing_catalog_directory':str(catalog.relative_to(ROOT)) if catalog.is_dir() else None,
                 'catalog_metadata_only_now':True,
                 'current_private_external_source_body_read':False if private else None,
                 'source_exposure_does_not_prove_whole_file_semantic_review':True,
                 'independent_evaluation_certified':False,'pretraining_or_external_exposure_certified':False,
                 'source_rights_notice_metadata':oldrole.get('source_rights',[]),
                 'training_eligible':False,'owner_training_gold':False,'publication_approved':False,
                 'remaining_lineage_review':'Related revisions/translations/derivedFAQs and borrowed target code stay grouped. Shared standard libraries are weak envelope edges, not automatic proof of target identity.'})
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'protocol_sha256':sha(P/'repository-exposure-matrix-protocol-v1.json'),
        'repository_count':len(rows),'records':rows,
        'role_counts':dict(collections.Counter(r['current_role'] for r in rows)),
        'certified_independent_families':0,'old_registries_unchanged':True,
        'new_model_calls':0,'optimizer_updates':0,'gold':0}
with (P/'repository-exposure-matrix-v2.json').open('x') as stream:
    json.dump(result,stream,indent=2)
    stream.write('\n')
print(json.dumps(result['role_counts']))
print(json.dumps({'unresolved_public':[r['repository'] for r in rows
                                     if r['collection']!='Projeto VivaBem' and
                                     r['current_role']!='CONFIRMED_PRIOR_SOURCE_OR_MODEL_EXPOSURE']}))
