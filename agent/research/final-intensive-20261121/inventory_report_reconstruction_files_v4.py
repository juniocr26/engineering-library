from pathlib import Path
import json,hashlib,datetime,stat,collections
p=Path(__file__).resolve().parent;root=p.parents[2];sha=lambda b:hashlib.sha256(b).hexdigest();records=[];roots=[];refs=[];counts=collections.Counter()
for receipt in sorted(p.glob('root-report-checkpoint-[0-9][0-9][0-9]-postnote-v1.json')):
 d=json.loads(receipt.read_text());base=Path(d['reconstructed_root']);assert base.parent==Path('/private/tmp') and base.name.startswith('el-report-reconstruction-') and not base.is_symlink();expected={x['path']:x['after_sha256'] for x in d['reports']}
 refs.append({'path':str(receipt.relative_to(root)),'sha256':sha(receipt.read_bytes())});seen=set();root_counts=collections.Counter()
 if not base.is_dir():
  roots.append({'root':str(base),'checkpoint':d['checkpoint'],'exists':False,'missing':list(expected)});counts['MISSING_DECLARED_ROOT']+=1;continue
 for f in sorted(base.iterdir()):
  st=f.lstat();raw=None;digest=None;name=f.name
  if stat.S_ISLNK(st.st_mode):kind='SYMLINK_NOT_FOLLOWED'
  elif stat.S_ISREG(st.st_mode):
   digest=sha(f.read_bytes());seen.add(name);kind=('MATCH_POSTNOTE_AFTERHASH' if digest==expected[name] else 'DIFFERS_POSTNOTE_AFTERHASH') if name in expected else 'UNEXPECTED_REGULAR_OUTPUT'
  else:kind='NONREGULAR_NOT_READ'
  records.append({'absolute_path':str(f),'bytes':st.st_size,'sha256':digest,'kind':kind,'expected_afterhash':expected.get(name),'checkpoint':d['checkpoint'],'purpose':'Exact historical final-report reconstruction at its own dated cut; not latestcanonicalbytes or trainingapproval'});counts[kind]+=1;root_counts[kind]+=1
 missing=sorted(set(expected)-seen);counts['MISSING_DECLARED_FILE']+=len(missing);roots.append({'root':str(base),'checkpoint':d['checkpoint'],'exists':True,'counts':dict(root_counts),'missing':missing})
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'roots':roots,'records':records,'source_receipts':refs,'counts':dict(counts),'root_count':len(roots),'file_count':len(records),'regular_bytes':sum(x['bytes'] for x in records if x['sha256']),'no_temporary_content_or_explicit_metadata_writes':True,'access_timestamp_preservation_not_claimed':True,'scope':'Onlysuccessfulpostnotereceipt-declared roots; failed040emptyrootnot claimed successful and not searchedgenerically; no equivalence tocurrentcanonicalreportimplied.'}
with (p/'temporary-report-reconstruction-inventory-results-v4.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({k:out[k] for k in ['root_count','file_count','regular_bytes','counts']}))
