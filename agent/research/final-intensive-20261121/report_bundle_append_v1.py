"""Research write-ahead appends for exactly four canonical reports, with owned recovery controls.
No truncation, replacement, deletion, publication, Git or automatic retry. POSIX local only.
"""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,stat
REPORTS=('AI_TRAINING_CAMPAIGN_REPORT.md','AI_TRAINING_FILE_INVENTORY.md','AI_FINE_TUNING_READINESS.md','AI_TRAINING_RESUME.md')
sha=lambda b:hashlib.sha256(b).hexdigest()
class AppendRefused(ValueError):pass
class OwnedInterruption(RuntimeError):pass

def write_new(path,raw):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 try:
  at=0
  while at<len(raw):at+=os.write(fd,raw[at:])
  os.fsync(fd)
 finally:os.close(fd)

def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()

def prepare(root,journal,payloads):
 root=Path(root).resolve();journal=Path(journal).resolve();assert set(payloads)==set(REPORTS)
 journal.mkdir(mode=0o700);rows=[]
 for name in REPORTS:
  f=root/name
  if f.is_symlink() or not f.is_file():raise AppendRefused('Regular canonical reports required')
  before=f.read_bytes();payload=payloads[name]
  if not isinstance(payload,bytes) or not 0<len(payload)<=1048576:raise AppendRefused('Bounded nonempty byte payload required')
  write_new(journal/(name+'.before.bin'),before);write_new(journal/(name+'.append.bin'),payload)
  rows.append({'path':name,'before_bytes':len(before),'before_sha256':sha(before),'payload_bytes':len(payload),'payload_sha256':sha(payload),'after_bytes':len(before+payload),'after_sha256':sha(before+payload),'before_mode':stat.S_IMODE(f.stat().st_mode)})
 plan={'schema':'four-report-append-plan-v1','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'original_root':str(root),'reports':rows,'scope':'Local write-ahead byte plan; not atomic4file commit, semantic approval or host crash proof.'}
 write_new(journal/'plan.json',canonical(plan));fd=os.open(journal,os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
 return plan

def apply(root,journal,*,owned_stop_after_reports=None,owned_stop_after_bytes=None):
 root=Path(root).resolve();journal=Path(journal).resolve();plan=json.loads((journal/'plan.json').read_text());assert plan['schema']=='four-report-append-plan-v1';assert [r['path'] for r in plan['reports']]==list(REPORTS)
 attempt=1
 while (journal/f'attempt-{attempt:03d}.json').exists():attempt+=1
 outcome={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':str(root),'plan_sha256':sha((journal/'plan.json').read_bytes()),'reports':[],'status':'PENDING'};opened=[]
 try:
  # Lock and validate all four before writing any. Uncooperative writers remain outside this guarantee.
  for row in plan['reports']:
   name=row['path'];before=(journal/(name+'.before.bin')).read_bytes();payload=(journal/(name+'.append.bin')).read_bytes();after=before+payload
   if sha(before)!=row['before_sha256'] or sha(payload)!=row['payload_sha256'] or sha(after)!=row['after_sha256']:raise AppendRefused('Plan/preimage/payload identity mismatch')
   fd=os.open(root/name,os.O_RDWR|os.O_APPEND|os.O_NOFOLLOW);opened.append(fd);fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);info=os.fstat(fd)
   if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode)!=row['before_mode']:raise AppendRefused('File type/mode changed')
   raw=os.pread(fd,info.st_size+1,0)
   if raw==after:state='ALREADY_APPLIED'
   elif raw==before:state='BEFORE'
   elif len(before)<len(raw)<len(after) and raw.startswith(before) and after.startswith(raw):state='PARTIAL_EXPECTED_APPEND'
   else:raise AppendRefused('Foreign/missing prefix state; no truncation or overwrite permitted')
   outcome['reports'].append({'path':name,'initial_state':state,'observed_before_sha256':sha(raw),'remaining_bytes':len(after)-len(raw)})
  for index,(fd,row,observed) in enumerate(zip(opened,plan['reports'],outcome['reports'])):
   name=row['path'];before=(journal/(name+'.before.bin')).read_bytes();payload=(journal/(name+'.append.bin')).read_bytes();after=before+payload;raw=os.pread(fd,os.fstat(fd).st_size+1,0)
   if sha(raw)!=observed['observed_before_sha256']:raise AppendRefused('Report changed after preflight')
   remaining=after[len(raw):]
   if owned_stop_after_bytes is not None and remaining:
    n=min(owned_stop_after_bytes,len(remaining));os.write(fd,remaining[:n]);os.fsync(fd);raise OwnedInterruption('Owned partial-byte interruption after durable append fragment')
   while remaining:
    n=os.write(fd,remaining);remaining=remaining[n:]
   os.fsync(fd);final=os.pread(fd,os.fstat(fd).st_size+1,0)
   if sha(final)!=row['after_sha256']:raise AppendRefused('After append identity differs')
   observed['final_sha256']=sha(final)
   if owned_stop_after_reports is not None and index+1==owned_stop_after_reports:raise OwnedInterruption('Owned between-report interruption')
  outcome['status']='APPLIED_OR_ALREADY_APPLIED'
 except Exception as error:
  outcome.update(status='OWNED_INTERRUPTION' if isinstance(error,OwnedInterruption) else 'REFUSED',error_type=type(error).__name__,error=str(error))
 finally:
  for fd in reversed(opened):os.close(fd)
  write_new(journal/f'attempt-{attempt:03d}.json',canonical(outcome))
 return outcome
