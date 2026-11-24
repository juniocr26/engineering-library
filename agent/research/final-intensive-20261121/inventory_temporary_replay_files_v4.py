from pathlib import Path
import json,hashlib,datetime,os,collections,stat
p=Path(__file__).resolve().parent;root=p.parents[2];sha=lambda b:hashlib.sha256(b).hexdigest();started=datetime.datetime.now(datetime.timezone.utc).isoformat();records=collections.Counter();summaries=[];receipts=[]
stream=p/'temporary-replay-file-inventory-records-v4.jsonl'
with stream.open('x') as out:
 for f in sorted(p.glob('checkpoint-[0-9][0-9][0-9].json')):
  d=json.loads(f.read_text());assert 'restored_root' in d
  base=Path(d['restored_root']);assert base.parent==Path('/private/tmp') and base.name.startswith('el-final-') and not base.is_symlink()
  mf=Path(d['input_manifest']);mf=mf if mf.is_absolute() else root/mf;raw=mf.read_bytes();assert sha(raw)==d['input_manifest_sha256'];manifest={x['path']:x for x in json.loads(raw)};seen=set();counts=collections.Counter();total=0
  if not base.is_dir():
   summaries.append({'checkpoint':d['checkpoint'],'root':str(base),'status':'MISSING_ROOT','missing_declared':len(manifest)});continue
  for directory,dirs,files in os.walk(base,followlinks=False):
   for name in dirs[:]:
    x=Path(directory)/name
    if x.is_symlink():dirs.remove(name);counts['SYMLINK_DIRECTORY_NOT_FOLLOWED']+=1
   for name in sorted(files):
    x=Path(directory)/name;rel=str(x.relative_to(base));st=x.lstat();kind='OTHER_NONREGULAR_NOT_READ';digest=None
    if stat.S_ISLNK(st.st_mode):kind='SYMLINK_FILE_NOT_FOLLOWED'
    elif stat.S_ISREG(st.st_mode):
     digest=sha(x.read_bytes());total+=st.st_size
     if rel in manifest:
      seen.add(rel);kind='RESTORED_INPUT_CURRENT_HASH_MATCH' if digest==manifest[rel]['sha256'] else 'RESTORED_INPUT_CURRENT_HASH_DIFFERS'
     else:kind='OWNED_REPLAY_OUTPUT_NOT_IN_ARCHIVED_INPUT_MANIFEST'
    row={'checkpoint':d['checkpoint'],'absolute_path':str(x),'relative_path':rel,'bytes':st.st_size,'sha256':digest,'kind':kind,'purpose':'Temporary exact archive reconstruction input' if rel in manifest else 'Temporary finite consumer/replay output; not automatically a source/training artifact','declared_archive_sha256':manifest.get(rel,{}).get('sha256')}
    out.write(json.dumps(row,separators=(',',':'))+'\n');counts[kind]+=1;records[kind]+=1
  missing=sorted(set(manifest)-seen)
  summaries.append({'checkpoint':d['checkpoint'],'root':str(base),'status':'OBSERVED_CURRENT_ROOT','counts':dict(counts),'regular_bytes':total,'missing_declared':missing});receipts.append({'path':str(f.relative_to(root)),'sha256':sha(f.read_bytes()),'input_manifest':str(mf.relative_to(root)),'input_manifest_sha256':sha(raw)})
d={'started':started,'finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':dict(records),'temporary_roots':summaries,'source_receipts':receipts,'record_stream':str(stream.relative_to(root)),'record_stream_sha256':sha(stream.read_bytes()),'failed_checkpoint031':'Not a successful receipt/root; failed archive and sidecar accounted separately in repository inventory','no_temporary_content_or_explicit_metadata_writes':True,'access_timestamp_preservation_not_claimed':True,'not_full_machine_or_crash_proof':True}
with (p/'temporary-replay-file-inventory-summary-v4.json').open('x') as f:json.dump(d,f,indent=2);f.write('\n')
print(json.dumps({'roots':len(summaries),'records':dict(records),'missing_declared_total':sum(len(x['missing_declared']) if isinstance(x['missing_declared'],list) else x['missing_declared'] for x in summaries)}))
