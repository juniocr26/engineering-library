"""Execute frozen owned child stops and preserve every partial/orphan byte."""
from pathlib import Path
import datetime,hashlib,json,os,stat,subprocess,sys
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
protocol_path=P/'atomic-publication-process-protocol-v1.json'
protocol=json.loads(protocol_path.read_text())
worker=P/'atomic_publication_worker_v1.py'
assert hashlib.sha256(worker.read_bytes()).hexdigest()==protocol['worker_sha256']
base=P/'atomic-publication-process-v1';base.mkdir(mode=0o700)
rows=[]

def payload(tag):return json.dumps({'owned_marker':tag,'body':protocol['body_text']},sort_keys=True,separators=(',',':')).encode()+b'\n'

def observe_final(folder,tag):
 f=folder/'artifact.json'
 if f.is_symlink():return {'state':'SYMLINK_RETAINED','target':os.readlink(f),'target_not_followed':True}
 if not f.exists():return {'state':'ABSENT'}
 raw=f.read_bytes();expected=payload(tag)
 state='FULL_PAYLOAD'if raw==expected else('PREEXISTING_BYTES'if raw==b'owned-original-sentinel\n'else'PARTIAL')
 return {'state':state,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'mode':oct(stat.S_IMODE(f.stat().st_mode))}

for case in protocol['cases']:
 folder=base/case['id'];folder.mkdir(mode=0o700)
 if case.get('preexisting')=='file':(folder/'artifact.json').write_bytes(b'owned-original-sentinel\n')
 if case.get('preexisting')=='symlink':
  (folder/'owned-target.txt').write_bytes(b'owned-target-sentinel\n')
  (folder/'artifact.json').symlink_to('owned-target.txt')
 command=[sys.executable,'-B',str(worker),case['variant'],case['phase'],str(folder.resolve()),'single']
 out=subprocess.run(command,capture_output=True,timeout=15)
 with(folder/'worker.stdout').open('xb')as stream:stream.write(out.stdout)
 with(folder/'worker.stderr').open('xb')as stream:stream.write(out.stderr)
 observed=observe_final(folder,'single')
 stages=[{'path':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}for f in sorted(folder.glob('stage-*.json'))]
 target_ok=(folder/'owned-target.txt').read_bytes()==b'owned-target-sentinel\n'if case.get('preexisting')=='symlink'else None
 row={**case,'command':command,'exit_code':out.returncode,'observed_final':observed,'retained_stages':stages,
      'symlink_target_bytes_unchanged':target_ok,'matches_frozen_expected':out.returncode==case['expected_exit_code']and observed['state']==case['expected_final_state']and target_ok is not False}
 rows.append(row)

# Two owned workers race only for their dedicated final name, with different bodies.
race=base/'two-publishers';race.mkdir(mode=0o700);workers=[]
for tag in ['alpha','beta']:
 command=[sys.executable,'-B',str(worker),'owned_stage_link','normal',str(race.resolve()),tag]
 workers.append((tag,command,subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)))
race_rows=[]
for tag,command,process in workers:
 stdout,stderr=process.communicate(timeout=15)
 (race/(tag+'.stdout')).write_bytes(stdout);(race/(tag+'.stderr')).write_bytes(stderr)
 race_rows.append({'tag':tag,'command':command,'exit_code':process.returncode,'stdout_sha256':hashlib.sha256(stdout).hexdigest()})
final=(race/'artifact.json').read_bytes();winner=[tag for tag in ['alpha','beta']if final==payload(tag)]
race_receipt={'workers':race_rows,'exit_codes':sorted(r['exit_code']for r in race_rows),'exactly_one_complete_winner':len(winner)==1,
 'winner':winner,'final_sha256':hashlib.sha256(final).hexdigest(),'both_original_stage_payloads_retained':all((race/('stage-'+tag+'.json')).read_bytes()==payload(tag)for tag in ['alpha','beta']),
 'no_overwrite_observed':sorted(r['exit_code']for r in race_rows)==[0,17]and len(winner)==1}
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':protocol_path.name,
 'protocol_sha256':hashlib.sha256(protocol_path.read_bytes()).hexdigest(),'records':rows,
 'single_worker_cases':len(rows),'child_processes_total':len(rows)+2,
 'all_single_worker_expectations_match':all(r['matches_frozen_expected']for r in rows),'two_publisher_race':race_receipt,
 'finding':'Currentactualwrite_newpublishesempty/partialfinalnamewhenstoppedbefore/midwrite. Ownedstaged-linkprofilekeepsfinalabsentuntilcompletefilefsyncandno-overwritehardlinkpublication; stopsafterlinkretainfullfinal. Existingfiles/symlinksrefused, bothracebodiespreservedwithonewinner. ThisisfinitePOSIXsingle-filepublicationresearch,notproductionpatch or transaction/jobreconciliation/nativecheckpointrecovery.',
 'limits':['Actualchildprocessstopnotpowerloss/kernelcrash/storagefault. Directoryfsyncdurabilitynotpower-tested.',
           'SameownedfilesystemPOSIXhardlinks; Windows/SMB/cross-device/hostileconcurrentpathreplacementunvalidated.',
           'No automaticorphanreconciliation/retry/budgetreset. Multi-filejobtransactionsandmissing/tamperedcompletionstillneedseparatepolicy.',
           'No source applications, neural inference or permanenttests executed/created. Sourcebaselineunchanged.'],
 'production_changes':0,'historical_files_deleted':0,'gold':0,'optimizer_updates':0}
with(P/'atomic-publication-process-results-v1.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps({k:v for k,v in result.items()if k not in ['records','two_publisher_race']},indent=2))
