"""Restore an explicitly pinned existing research capsule; never create a new source archive."""
import argparse,base64,datetime,hashlib,json,os,stat,subprocess,sys,tarfile,tempfile,time
from pathlib import Path,PurePosixPath
REPORTS=('AI_TRAINING_CAMPAIGN_REPORT.md','AI_TRAINING_FILE_INVENTORY.md','AI_FINE_TUNING_READINESS.md','AI_TRAINING_RESUME.md')
CONSUMERS=('consume_dataset_faq_row_bindings_v1.py','consume_h71_h72_mask_state_v1.py','consume_scope_and_first_pilot_review_v1.py','consume_next_neural_matched_dimensions_v1.py','consume_pinned_tree_membership_v1.py','consume_owner_review_batch_identity_v1.py','consume_weekend_recovery_receipts_v4.py')
REL=Path('agent/research/final-intensive-20261121')
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def canonical_name(name):
 p=PurePosixPath(name)
 if not name or p.is_absolute() or str(p)!=name or any(x in ('','..','.') for x in name.split('/')) or '\\' in name:raise ValueError('NONCANONICAL_OR_UNSAFE_MEMBER_NAME')
 return name
def validate_members(members,manifest,max_members,max_bytes):
 if len(members)>max_members or sum(e['bytes'] for e in manifest.values())>max_bytes:raise ValueError('DECLARED_RESOURCE_BOUND_EXCEEDED')
 seen=set()
 for member in members:
  name=canonical_name(member.name)
  if name in seen:raise ValueError('DUPLICATE_MEMBER')
  seen.add(name)
  if not member.isfile():raise ValueError('NONREGULAR_MEMBER')
  if name not in manifest:raise ValueError('UNLISTED_MEMBER')
  e=manifest[name]
  if member.size!=e['bytes'] or stat.S_IMODE(member.mode)!=e['mode']:raise ValueError('MEMBER_SIZE_OR_MODE_MISMATCH')
 if seen!=set(manifest):raise ValueError('MISSING_MANIFEST_MEMBER')
def run_finite_consumer(command,root,timeout):
 record={'command':command,'exit_code':None,'timeout_seconds':timeout};stdout=b'';stderr=b''
 try:
  run=subprocess.run(command,capture_output=True,timeout=timeout,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},cwd=root)
  stdout=run.stdout;stderr=run.stderr;record.update(exit_code=run.returncode,status='EXIT_ZERO' if run.returncode==0 else 'NONZERO_EXIT')
 except subprocess.TimeoutExpired as e:
  stdout=e.stdout or b'';stderr=e.stderr or b'';record.update(status='TIMEOUT_PARTIAL_CAPTURED_NO_RETRY',exception_type=type(e).__name__,exception=str(e),capture_scope='Exact bytes available on TimeoutExpired, not a claim that every byte ever emitted was captured.')
 except OSError as e:record.update(status='LAUNCH_FAILURE_NO_RETRY',exception_type=type(e).__name__,exception=str(e))
 for name,raw in [('stdout',stdout),('stderr',stderr)]:
  record[name]=raw.decode('utf-8',errors='replace');record[name+'_base64']=base64.b64encode(raw).decode('ascii');record[name+'_sha256']=hashlib.sha256(raw).hexdigest();record[name+'_bytes']=len(raw)
 return record
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--capsule-dir',required=True,type=Path);ap.add_argument('--receipt-sha256',required=True);ap.add_argument('--postnote',required=True,type=Path);ap.add_argument('--postnote-sha256',required=True);ap.add_argument('--result',required=True,type=Path);ap.add_argument('--max-total-bytes',type=int,default=2*1024**3);ap.add_argument('--max-members',type=int,default=10000);a=ap.parse_args()
 a.capsule_dir=a.capsule_dir.resolve();a.postnote=a.postnote.resolve();a.result=a.result.resolve()
 if a.result.exists():raise ValueError('RESULT_ALREADY_EXISTS')
 started=datetime.datetime.now(datetime.timezone.utc).isoformat();tic=time.monotonic();out={'started':started,'status':'RUNNING','restored_root':None,'consumers':[],'model_calls':0,'framework_imports':0,'optimizer_updates':0,'scope':'Local research recovery and seven finite data-only consumers; no model,upstreamapplication,cleanclone,Windows,remote,crash or semanticquality certification.'}
 try:
  receipt=a.capsule_dir/'receipt.json'
  if digest(receipt)!=a.receipt_sha256:raise ValueError('RECEIPT_PIN_MISMATCH')
  r=json.loads(receipt.read_bytes());archive=a.capsule_dir/Path(r['archive']).name;mf=a.capsule_dir/Path(r['input_manifest']).name
  if digest(archive)!=r['archive_sha256'] or digest(mf)!=r['input_manifest_sha256']:raise ValueError('ARCHIVE_OR_MANIFEST_HASH_MISMATCH')
  if digest(a.postnote)!=a.postnote_sha256:raise ValueError('POSTNOTE_PIN_MISMATCH')
  note=json.loads(a.postnote.read_bytes())
  if note['checkpoint']!=r['checkpoint']:raise ValueError('POSTNOTE_CHECKPOINT_MISMATCH')
  entries=json.loads(mf.read_bytes());manifest={canonical_name(e['path']):e for e in entries}
  if len(manifest)!=len(entries):raise ValueError('DUPLICATE_MANIFEST_PATH')
  if len(entries)!=r['regular_files_restored_and_hash_verified']:raise ValueError('MANIFEST_COUNT_MISMATCH')
  if not all(str(REL/name) in manifest for name in CONSUMERS):raise ValueError('CAPSULE_MISSING_REQUIRED_SEVEN_CONSUMERS')
  out['inputs']={'checkpoint':r['checkpoint'],'archive':str(archive),'archive_sha256':digest(archive),'manifest':str(mf),'manifest_sha256':digest(mf),'receipt':str(receipt),'receipt_sha256':a.receipt_sha256,'postnote':str(a.postnote),'postnote_sha256':a.postnote_sha256}
  with tarfile.open(archive,'r:gz') as tar:
   members=tar.getmembers();validate_members(members,manifest,a.max_members,a.max_total_bytes)
   base=Path(tempfile.mkdtemp(prefix='el-final-weekend-',dir='/private/tmp'));os.chmod(base,0o700);out['restored_root']=str(base)
   for member in members:
    dest=base/member.name;dest.parent.mkdir(parents=True,exist_ok=True);source=tar.extractfile(member)
    with dest.open('xb') as target:
     while True:
      chunk=source.read(1024*1024)
      if not chunk:break
      target.write(chunk)
    os.chmod(dest,manifest[member.name]['mode'])
   for name,e in manifest.items():
    f=base/name
    if f.stat().st_size!=e['bytes'] or digest(f)!=e['sha256'] or stat.S_IMODE(f.stat().st_mode)!=e['mode']:raise ValueError('RESTORED_INPUT_MISMATCH')
  out['regular_files_restored_and_hash_verified']=len(manifest);out['file_modes_verified']=True
  if 'note_utf8' not in note or hashlib.sha256(note['note_utf8'].encode()).hexdigest()!=note['note_sha256']:raise ValueError('POSTNOTE_PAYLOAD_MISMATCH')
  # This generic consumer handles ordinary archive-prefix+note checkpoints, not CP040's additional late sidecars.
  if set(e['path'] for e in note['reports'])!=set(REPORTS):raise ValueError('POSTNOTE_REPORT_SET_MISMATCH')
  for e in note['reports']:
   f=base/e['path']
   if digest(f)!=e['before_sha256']:raise ValueError('POSTNOTE_REQUIRES_ADDITIONAL_PREFIX_SIDECAR')
   after=f.read_bytes()+note['note_utf8'].encode()
   if hashlib.sha256(after).hexdigest()!=e['after_sha256']:raise ValueError('POSTNOTE_AFTERHASH_MISMATCH')
   f.write_bytes(after)
  out['exact_postnote_reports_reconstructed']=4
  for name in CONSUMERS:
   script=base/REL/name;command=[sys.executable,'-B',str(script),'--root',str(base)];record=run_finite_consumer(command,base,90);record['script']=name
   out['consumers'].append(record)
   if record['status']!='EXIT_ZERO':raise ValueError('FINITE_CONSUMER_FAILED_PRESERVED_NO_RETRY')
  out['actual_data_consumer_count']=len(out['consumers']);out['consumer_source_sha256']=digest(Path(__file__));out['working_directory_at_dispatch']=str(Path.cwd())
  out['status']='PASS_EXISTING_CAPSULE_STANDALONE_RECOVERY'
 except Exception as e:
  out.update(status='FAILED_PRESERVED_NO_RETRY',exception_type=type(e).__name__,exception=str(e));raise
 finally:
  out.update(finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-tic)
  with a.result.open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
  print(json.dumps({k:v for k,v in out.items() if k not in ('inputs','consumers')},ensure_ascii=False))
if __name__=='__main__':main()
