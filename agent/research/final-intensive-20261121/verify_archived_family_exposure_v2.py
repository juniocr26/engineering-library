"""Verify public archival bytes with fixed inventory and path boundaries."""
from pathlib import Path
import datetime
import hashlib
import json

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
protocol=json.loads((P/'archived-family-exposure-integrity-protocol-v2.json').read_text())
base=ROOT/protocol['base']
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
rows=[]
inventories=[]
dependencies={}
for reference in protocol['inventories']:
    inventory=ROOT/reference['path']
    assert sha(inventory)==reference['sha256']
    metadata=json.loads(inventory.read_text())
    entries=metadata.get('inspected_only',{}).get('preserved_source_files',[])
    inventories.append({'repository':metadata['repository'],'revision':metadata['revision'],
                        'inventory':reference['path'],'source_entries':len(entries),
                        'inventory_sha256':reference['sha256']})
    dependencies[reference['path']]={'path':reference['path'],'sha256':reference['sha256'],
                                     'role':'Exact archived public source exposure inventory'}
    for entry in entries:
        relative=Path(entry['snapshot'])
        row={'repository':metadata['repository'],'revision':entry.get('revision',metadata['revision']),
             'source_path':entry['path'],'snapshot':str((base/relative).relative_to(ROOT)),
             'expected_sha256':entry['sha256'],'expected_bytes':entry['bytes'],
             'source_body_semantically_reviewed_now':False,'target_executed':False}
        target=base/relative
        if relative.is_absolute() or '..' in relative.parts:
            row['status']='UNSAFE_RELATIVE_PATH'
        elif not any(str(relative).startswith(prefix) for prefix in protocol['allowed_snapshot_prefixes']):
            row['status']='UNSUPPORTED_ARCHIVE_PREFIX'
        elif not target.resolve().is_relative_to(base.resolve()):
            row['status']='ESCAPES_FROZEN_ARCHIVE'
        elif target.is_symlink() or not target.is_file():
            row['status']='MISSING_OR_UNSAFE_FILE'
        else:
            try:
                actual=sha(target)
                size=target.stat().st_size
                row.update(actual_sha256=actual,actual_bytes=size,
                           status='MATCH' if actual==entry['sha256'] and size==entry['bytes'] else 'MISMATCH')
                if row['status']=='MATCH':
                    path=str(target.relative_to(ROOT))
                    dependencies[path]={'path':path,'sha256':actual,
                                        'role':'Previously preserved public source snapshot; current hash/size verification only, no new semantic review or execution'}
            except OSError as error:
                row.update(status='UNREADABLE',error_class=type(error).__name__)
        rows.append(row)
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'protocol_sha256':sha(P/'archived-family-exposure-integrity-protocol-v2.json'),
        'inventories':inventories,'records':rows,'source_entries':len(rows),
        'unique_snapshot_paths':len({r['snapshot'] for r in rows}),
        'matching_entries':sum(r['status']=='MATCH' for r in rows),
        'nonmatching_entries':[r for r in rows if r['status']!='MATCH'],
        'bytes_hashed':sum(r.get('actual_bytes',0) for r in rows),
        'source_families_with_matching_archived_bytes':sorted({r['repository'] for r in rows if r['status']=='MATCH'}),
        'current_semantic_claim_denominator':None,'local_model_exposure_inferred_from_hashes':False,
        'all_originals_unchanged':True,'training_eligible':False}
with (P/'archived-family-exposure-integrity-results-v2.json').open('x') as stream:
    json.dump(result,stream,indent=2)
    stream.write('\n')
with (P/'remaining-chapters-recovery-dependencies-v11.json').open('x') as stream:
    json.dump({'dependencies':list(dependencies.values())},stream,indent=2)
    stream.write('\n')
print(json.dumps({key:result[key] for key in ['source_entries','unique_snapshot_paths','matching_entries',
                                            'bytes_hashed','source_families_with_matching_archived_bytes']}))
