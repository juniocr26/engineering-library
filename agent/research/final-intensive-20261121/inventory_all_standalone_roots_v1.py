from pathlib import Path
import json,hashlib,datetime,os,stat,collections
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sha=lambda b:hashlib.sha256(b).hexdigest();receipts=[P/('weekend-capsule-consumption-results-v'+str(i)+'.json') for i in range(1,5)];protocol={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'before_inventory':True,'role':'ALL_FOUR_RECEIPT_DECLARED_SUCCESSFUL_STANDALONE_RESTORES_ONLY','receipts':[{'path':str(f.relative_to(ROOT)),'sha256':sha(f.read_bytes())} for f in receipts],'no_generic_temporary_directory_search':True,'no_content_or_explicit_metadata_writes':True,'atime_not_claimed_preserved':True}
with (P/'all-standalone-root-inventory-protocol-v1.json').open('x') as f:json.dump(protocol,f,indent=2);f.write('\n')
stream=P/'all-standalone-root-inventory-records-v1.jsonl';roots=[];totals=collections.Counter();totalbytes=0
with stream.open('x') as out:
 for receipt in receipts:
  r=json.loads(receipt.read_bytes());assert r['status']=='PASS_EXISTING_CAPSULE_STANDALONE_RECOVERY';base=Path(r['restored_root']);assert base.parent==Path('/private/tmp') and base.name.startswith('el-final-weekend-') and not base.is_symlink();mf=Path(r['inputs']['manifest']);mf=mf if mf.is_absolute() else ROOT/mf;post=Path(r['inputs']['postnote']);post=post if post.is_absolute() else ROOT/post;assert sha(mf.read_bytes())==r['inputs']['manifest_sha256'] and sha(post.read_bytes())==r['inputs']['postnote_sha256'];manifest={e['path']:e for e in json.loads(mf.read_bytes())};note=json.loads(post.read_bytes());after={e['path']:e['after_sha256'] for e in note['reports']};seen=set();counts=collections.Counter();rootbytes=0
  for directory,dirs,files in os.walk(base,followlinks=False):
   for name in dirs[:]:
    if (Path(directory)/name).is_symlink():dirs.remove(name);counts['SYMLINK_DIRECTORY_NOT_FOLLOWED']+=1
   for name in sorted(files):
    f=Path(directory)/name;st=f.lstat();rel=str(f.relative_to(base));e=manifest.get(rel);digest=None;expected=None;expectedbytes=None
    if stat.S_ISREG(st.st_mode):
     raw=f.read_bytes();digest=sha(raw);rootbytes+=len(raw)
     if e:
      seen.add(rel);expected=after.get(rel,e['sha256']);expectedbytes=e['bytes']+(len(note['note_utf8'].encode()) if rel in after else 0);ok=digest==expected and len(raw)==expectedbytes and stat.S_IMODE(st.st_mode)==e['mode'];kind=('MATCH_POSTNOTE_REPORT' if rel in after else 'MATCH_ARCHIVED_INPUT') if ok else 'HASH_SIZE_OR_MODE_DIFFERS'
     else:kind='OWNED_EXTRA_OUTPUT_NOT_IN_INPUT_MANIFEST'
    else:kind='NONREGULAR_NOT_READ'
    counts[kind]+=1;out.write(json.dumps({'receipt':str(receipt.relative_to(ROOT)),'absolute_path':str(f),'relative_path':rel,'bytes':st.st_size,'mode':stat.S_IMODE(st.st_mode),'sha256':digest,'expected_sha256':expected,'expected_bytes':expectedbytes,'kind':kind},separators=(',',':'))+'\n')
  missing=sorted(set(manifest)-seen);assert not missing and counts['HASH_SIZE_OR_MODE_DIFFERS']==0;totals.update(counts);totalbytes+=rootbytes;roots.append({'receipt':str(receipt.relative_to(ROOT)),'root':str(base),'input_files':len(manifest),'counts':dict(counts),'regular_bytes':rootbytes,'missing':missing})
out={'started':protocol['at'],'finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'roots':roots,'root_count':len(roots),'counts':dict(totals),'regular_bytes':totalbytes,'record_stream':str(stream.relative_to(ROOT)),'record_stream_sha256':sha(stream.read_bytes()),'protocol_sha256':sha((P/'all-standalone-root-inventory-protocol-v1.json').read_bytes()),'scope':'All4successfuldeclaredstandaloneroots,includingv3CP051rootomittedbypreviousindividuallatestinventory. FailedCLIcontrolscreatednoroots. No generaltempscan or atimepreservationclaim.'}
with (P/'all-standalone-root-inventory-summary-v1.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({'roots':len(roots),'counts':dict(totals),'regular_bytes':totalbytes}))
