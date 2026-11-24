"""Metadata-only hypothetical partition diagnostics; no training split/export or record mutation."""
import collections,datetime,hashlib,json,re
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
protocol=json.loads((P/'dataset-partition-diagnostic-protocol-v1.json').read_text())
manifest_path=ROOT/'agent/research/documentation-intelligence-20261119/datasets/v10/manifest.json'
manifest_raw=manifest_path.read_bytes()
assert hashlib.sha256(manifest_raw).hexdigest()==protocol['dataset_manifest_sha256']
manifest=json.loads(manifest_raw)
records=[]
file_checks=[]
for entry in manifest['files']:
    file=ROOT/entry['path']
    raw=file.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==entry['sha256'] and len(raw)==entry['bytes']
    count=0
    for number,line in enumerate(raw.splitlines(keepends=True),1):
        if not line.strip():
            continue
        row=json.loads(line)
        assert isinstance(row['source_family'],str) and isinstance(row['lineage_group'],str)
        record={
            'id':row['id'],'source_file':entry['path'],'line':number,
            'exact_line_sha256':hashlib.sha256(line).hexdigest(),
            'family_raw':row['source_family'],
            'family':row['source_family'].removeprefix('source-repository:'),
            'lineage':row['lineage_group'],'category':row['category'],
            'language':row.get('language'),'bilingual_task':None,
            'reference_identities':{},
            'owner_gold':row.get('training_gold')is True,
            'owner_approved':row.get('owner_approved')is True,
            'training_use_approved':row.get('training_use_approved')is True,
        }
        if row['category']=='SOURCE_REVIEWED_DOCUMENT_CANDIDATE':
            canonical=row['canonical_record_id']
            assert canonical.endswith(':'+row['language'])
            record['bilingual_task']='chapter:'+canonical.rsplit(':',1)[0]
        elif row['category']=='SOURCE_REVIEWED_FAQ_CANDIDATE':
            record['bilingual_task']='faq:'+json.dumps(row['question_identity'],ensure_ascii=False,separators=(',',':'))
        for key in ['source_evidence_ref','document_ref']:
            ref=row.get(key)
            if isinstance(ref,dict) and isinstance(ref.get('sha256'),str):
                record['reference_identities'][key]=ref['sha256']
        records.append(record)
        count+=1
    assert count==entry['records']
    file_checks.append({'path':entry['path'],'sha256':entry['sha256'],'records':count})
assert len(records)==305 and len({r['id']for r in records})==305
pairs=collections.defaultdict(list)
for row in records:
    if row['bilingual_task']:
        pairs[row['bilingual_task']].append(row)
assert len(pairs)==102 and all(sorted(r['language']for r in group)==['en','pt-br']for group in pairs.values())
assert sum(r['owner_gold']or r['owner_approved']or r['training_use_approved']for r in records)==0
schemes=[]
def partition(key):
    return 'B' if int(hashlib.sha256(key.encode()).hexdigest(),16)%5==0 else 'A'
def crossed(assignment,key_fn):
    groups=collections.defaultdict(lambda:collections.defaultdict(list))
    for row in records:
        key=key_fn(row)
        if key is not None:
            groups[key][assignment[row['id']]].append(row['id'])
    return [{'group':key,'partitions':dict(parts)}for key,parts in sorted(groups.items())if len(parts)>1]
for scheme,key_fn in [
    ('row-identity-hash',lambda row:row['id']),
    ('lineage-group-hash',lambda row:row['lineage']),
    ('declared-source-family-hash',lambda row:row['family']),
]:
    assignment={row['id']:partition(key_fn(row))for row in records}
    bilingual=crossed(assignment,lambda row:row['bilingual_task'])
    lineages=crossed(assignment,lambda row:row['lineage'])
    families=crossed(assignment,lambda row:row['family'])
    refs={key:crossed(assignment,lambda row,key=key:row['reference_identities'].get(key))for key in ['source_evidence_ref','document_ref']}
    schemes.append({
        'scheme':scheme,'hypothetical_partition_counts':dict(collections.Counter(assignment.values())),
        'row_assignments_metadata_only':assignment,
        'split_bilingual_task_groups':bilingual,'split_bilingual_task_count':len(bilingual),
        'split_lineage_groups':lineages,'split_lineage_count':len(lineages),
        'split_declared_source_families':families,'split_family_count':len(families),
        'shared_reference_artifacts_across_partitions':refs,
        'shared_source_evidence_artifact_count':len(refs['source_evidence_ref']),
        'shared_document_artifact_count':len(refs['document_ref']),
    })
a,b,c=schemes
relations={
    'row_partition_splits_some_bilingual_and_families':a['split_bilingual_task_count']>0 and a['split_family_count']>0,
    'lineage_partition_keeps_bilingual_and_lineage_groups':b['split_bilingual_task_count']==b['split_lineage_count']==0,
    'lineage_partition_still_splits_some_source_families':b['split_family_count']>0,
    'family_partition_keeps_declared_groups':c['split_bilingual_task_count']==c['split_lineage_count']==c['split_family_count']==0,
}
assert all(relations.values())
assert hashlib.sha256(manifest_path.read_bytes()).hexdigest()==protocol['dataset_manifest_sha256']
for entry in manifest['files']:
    assert hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest()==entry['sha256']
r={
    'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'status':'HYPOTHETICAL_METADATA_PARTITIONS_NOT_TRAIN_VALIDATION_SPLITS',
    'protocol_sha256':hashlib.sha256((P/'dataset-partition-diagnostic-protocol-v1.json').read_bytes()).hexdigest(),
    'records':records,'record_count':305,'input_file_checks':file_checks,
    'bilingual_tasks':len(pairs),'declared_lineage_groups':len({r['lineage']for r in records}),
    'declared_source_families':len({r['family']for r in records}),
    'schemes':schemes,'expected_relations':relations,
    'frozen_dataset_bytes_unchanged':True,'original_split_fields_unchanged':True,
    'actual_training_or_evaluation_assignments_created':False,
    'example_text_exported':False,'owner_gold':0,'training_steps':0,'launch_allowed':False,
    'certified_independent_evaluation':False,
    'limits':[
        'These are fixed metadata hash-partition illustrations,not recommended final train/evaluation allocations.',
        'Whole declared family grouping removes the measured declared-group overlap but does not resolve hidden ancestry,shareddependencies,semantic duplicates,rights,approval or prior development exposure.',
        'A shared full evidence/document artifact is a concrete overlap signal;it is not alone proof of identical source semantics.',
        'Row counts,102bilingualtasks and305records are not independent approved examples. All original rows remain quarantine and no actual training split was exported.',
    ],
}
with(P/'dataset-partition-diagnostics-v1.json').open('x')as stream:
    json.dump(r,stream,indent=2)
    stream.write('\n')
print({'rows':305,'bilingual_tasks':102,'lineages':r['declared_lineage_groups'],'families':r['declared_source_families'],'schemes':[{k:s[k]for k in ['scheme','split_bilingual_task_count','split_lineage_count','split_family_count','shared_source_evidence_artifact_count']}for s in schemes],'training_splits_created':False})
