"""Read-only Git base plus exact overlay and frozen data/compiler dependencies.

All restoration goes into a fresh owned directory. No Git state, source model,
service, database, existing source tree or historical sealed archive is changed.
"""
from collections import Counter
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import tarfile
import time

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
BASELINE=json.loads((P/'baseline.json').read_text())
CUT=ROOT/'.local-backups/continuation-20261120/intermediate-cut-v1'
RESTORE=Path('/private/tmp/el-engineering-library-continuation-20261120-cut-v1-restore')
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS='0')


def sha(path):
    digest=hashlib.sha256()
    with path.open('rb')as stream:
        for chunk in iter(lambda:stream.read(4*1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()


def source_entry(path,role):
    if path.is_symlink()or not path.is_file():raise ValueError('only explicit regular source artifacts are sealed:'+str(path))
    info=path.stat()
    return {'path':str(path.relative_to(ROOT)),'sha256':sha(path),'bytes':info.st_size,'mode':stat.S_IMODE(info.st_mode),'role':role}


def extract_regular(archive,root,skip=frozenset()):
    extracted=[]
    with tarfile.open(archive,'r:gz')as bundle:
        for member in bundle:
            relative=PurePosixPath(member.name)
            if relative.is_absolute()or'..'in relative.parts or relative.as_posix()!=member.name:
                raise ValueError('noncanonical archive path')
            if member.name in skip:continue
            target=root.joinpath(*relative.parts)
            if member.isdir():target.mkdir(parents=True,exist_ok=True);continue
            if not member.isfile()or member.size>256*1024*1024:raise ValueError('unsupported archive member')
            if any(parent.is_symlink()for parent in target.parents):raise ValueError('restore parent symlink')
            target.parent.mkdir(parents=True,exist_ok=True)
            # The overlay intentionally replaces only files in this newly created
            # owned restore tree. Existing owner/source paths are never destinations.
            with bundle.extractfile(member)as source,target.open('wb')as destination:
                while True:
                    chunk=source.read(4*1024*1024)
                    if not chunk:break
                    destination.write(chunk)
            os.chmod(target,member.mode&0o777)
            extracted.append(member.name)
    return extracted


def main():
    started=time.monotonic();head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,env=ENV,text=True).strip()
    if head!=BASELINE['head']:raise ValueError('owner HEAD changed;do not absorb or reset changes')
    index_before=sha(ROOT/'.git/index')
    if index_before!=BASELINE['index_sha256']:raise ValueError('owner index changed;stop this cut,do not revert')
    # Freeze every overlay input before creating any output folder/archive.
    selected={}
    def add(path,role):
        entry=source_entry(path,role);previous=selected.get(entry['path'])
        if previous and previous['sha256']!=entry['sha256']:raise ValueError('conflicting selected artifact identity')
        selected[entry['path']]=entry
    for name in ['backend/lib/documentation/command.rb','backend/lib/documentation/python_structure.py','agent/recovery/manifest.json']:
        add(ROOT/name,'validated-current-production-overlay')
    for name in ['AI_TRAINING_CAMPAIGN_REPORT.md','AI_TRAINING_FILE_INVENTORY.md','AI_FINE_TUNING_READINESS.md','AI_TRAINING_RESUME.md']:
        add(ROOT/name,'canonical-root-report-at-cut')
    for path in P.rglob('*'):
        if path.is_file()and not path.is_symlink()and'__pycache__'not in path.parts:add(path,'current-technical-research')
    for path in (ROOT/'.local-backups/continuation-20261120').rglob('*'):
        if path.is_file()and not path.is_symlink():add(path,'current-exact-recovery-preimage-or-archive')
    audit=json.loads((P/'dataset-lineage-audit-v1.json').read_text())
    for entry in audit['reference_checks']:
        if entry['status']!='MATCH':raise ValueError('dataset reference audit has unresolved entry')
        path=ROOT/entry['path'];add(path,'frozen-V10-reference')
        if selected[entry['path']]['sha256']!=entry['expected_sha256']:raise ValueError('frozen V10 reference drift')
    data_manifest=json.loads((ROOT/'agent/research/documentation-intelligence-20261119/datasets/v10/manifest.json').read_text())
    add(ROOT/data_manifest['rights_provenance']['path'],'frozen-license-provenance')
    for repo in audit['rights_evidence']:
        for record in repo['license_records']:add(ROOT/record['path'],'frozen-primary-license')
    sdk=ROOT/'.local-backups/continuation-20261119/cached-go-toolchain'
    for path in sdk.rglob('*'):
        if path.is_file()and not path.is_symlink():add(path,'preserved-offline-Go-toolchain')
    add(ROOT/'.local-backups/continuation-20261119/cached-go-toolchain-receipt.json','offline-Go-toolchain-origin-receipt')
    # The old sealed chain independently preserves all440 historical files,
    # including original paths for the five removed live human reports.
    for name in ['.local-backups/documentation-intelligence-20261120/recovery-cut-v1/code-and-research.tar.gz',
                 '.local-backups/documentation-intelligence-20261120/metadata-delta-v1/later-research.tar.gz']:
        add(ROOT/name,'unchanged-old-sealed-history-chain')
    deleted=set(subprocess.check_output(['git','ls-files','--deleted','-z'],cwd=ROOT,env=ENV).decode().split('\0'))-{''}
    expected_deleted={'agent/research/documentation-intelligence-20261120/'+name for name in ['CAMPAIGN_REPORT.md','FILE_INVENTORY.md','FIRST_NEURAL_FINE_TUNING_READINESS.md','PROGRESS.md','RESUME.md']}
    if deleted!=expected_deleted:raise ValueError('unexpected deletion set;owner changes require separate review')
    CUT.mkdir(exist_ok=False)
    manifest={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline_head':head,'baseline_tracked_entries':BASELINE['tracked_identity'],
              'overlay_entries':list(selected.values()),'skip_live_baseline_paths':sorted(deleted),
              'scope':'Intermediate local source/research/frozen-data/compiler cut;existing model store and bundle remain separate verified preservation assets.',
              'model_weights_copied':False,'model_training':False,'trusted_owned_bootstrap_knowledge_verifier_allowed':True,
              'third_party_application_or_model_execution':False,'original_source_tree_written':False}
    manifest_path=CUT/'input-manifest.json';manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    baseline_archive=CUT/'owner-baseline.tar.gz'
    with baseline_archive.open('xb')as stream:
        process=subprocess.run(['git','archive','--format=tar.gz',head],cwd=ROOT,env=ENV,stdout=stream,stderr=subprocess.PIPE,timeout=120)
    if process.returncode:raise ValueError('read-only Git archive failed:'+process.stderr.decode()[:300])
    overlay_archive=CUT/'current-overlay.tar.gz'
    with tarfile.open(overlay_archive,'x:gz')as bundle:
        for index,(name,entry)in enumerate(sorted(selected.items())):
            path=ROOT/name
            if sha(path)!=entry['sha256']or path.stat().st_size!=entry['bytes']:raise ValueError('overlay source changed before archive:'+name)
            bundle.add(path,arcname=name,recursive=False)
            if index%2000==0:print(json.dumps({'phase':'overlay-archive','files_done':index,'files_total':len(selected)}),flush=True)
    RESTORE.mkdir(exist_ok=False)
    base_paths=extract_regular(baseline_archive,RESTORE,deleted)
    for name,entry in BASELINE['tracked_identity'].items():
        if name in deleted:continue
        path=RESTORE/name
        if not path.is_file()or path.stat().st_size!=entry['bytes']or sha(path)!=entry['sha256']:raise ValueError('baseline restore mismatch:'+name)
    overlay_paths=extract_regular(overlay_archive,RESTORE)
    failures=[]
    for name,entry in selected.items():
        path=RESTORE/name
        if not path.is_file()or path.stat().st_size!=entry['bytes']or sha(path)!=entry['sha256']:failures.append(name)
    if failures:raise ValueError('overlay restore hash mismatch:'+str(failures[:5]))
    # Verify untouched baseline files against the owner start cut after overlay.
    for name,entry in BASELINE['tracked_identity'].items():
        if name in deleted or name in selected:continue
        if sha(RESTORE/name)!=entry['sha256']:raise ValueError('untouched baseline drift:'+name)
    bootstrap=RESTORE/'agent/recovery/bootstrap.py'
    result=subprocess.run([sys_executable(),str(bootstrap),'knowledge'],cwd=RESTORE,capture_output=True,timeout=60)
    (CUT/'restored-bootstrap.stdout').write_bytes(result.stdout);(CUT/'restored-bootstrap.stderr').write_bytes(result.stderr)
    if result.returncode:raise ValueError('restored default knowledge refused;rawoutputs preserved')
    parsed=json.loads(result.stdout)
    if parsed['knowledge_files']!=1964:raise ValueError('unexpected restored knowledge closure')
    for name,entry in selected.items():
        if sha(ROOT/name)!=entry['sha256']:raise ValueError('live selected artifact changed during seal:'+name)
    if sha(ROOT/'.git/index')!=index_before or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,env=ENV,text=True).strip()!=head:
        raise ValueError('owner Git state changed during cut;do not claim stable snapshot')
    receipt={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'VERIFIED_INTERMEDIATE_LOCAL_SOURCE_RESEARCH_DATA_CUT','wall_seconds':time.monotonic()-started,
             'baseline_archive':{'path':str(baseline_archive.relative_to(ROOT)),'sha256':sha(baseline_archive),'bytes':baseline_archive.stat().st_size},
             'overlay_archive':{'path':str(overlay_archive.relative_to(ROOT)),'sha256':sha(overlay_archive),'bytes':overlay_archive.stat().st_size},
             'input_manifest':{'path':str(manifest_path.relative_to(ROOT)),'sha256':sha(manifest_path)},
             'baseline_files_restored':len(base_paths),'overlay_files_restored':len(overlay_paths),'roles':dict(Counter(x['role']for x in selected.values())),
             'all_restored_hashes_verified':True,'restore_root':str(RESTORE),'restored_bootstrap':parsed,'skipped_live_reports':sorted(deleted),
             'old_historical_archives_included':True,'git_head_unchanged':True,'git_index_unchanged':True,
             'model_weights_copied':False,'model_store_and_bundle_separate':True,'actual_cold_boot_verified':False,'remote_durability_verified':False,
             'neural_training':False,'eleven_hour_completion_claimed':False}
    with(CUT/'receipt.json').open('x')as stream:json.dump(receipt,stream,indent=2)
    with(P/'intermediate-recovery-cut-receipt-v1.json').open('x')as stream:json.dump(receipt,stream,indent=2)
    print(json.dumps({k:v for k,v in receipt.items()if k not in['roles','skipped_live_reports']}),flush=True)


def sys_executable():
    import sys
    return sys.executable


if __name__=='__main__':main()
