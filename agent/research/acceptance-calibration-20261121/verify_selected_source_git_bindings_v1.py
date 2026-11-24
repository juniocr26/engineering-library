"""Cross-check retained public snapshots against exact local Git blobs, read-only."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import datetime,hashlib,json,os,subprocess
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
inventory=json.loads((P/'repository-inspected-files-v2.json').read_text())
inputs=[(repo,row)for repo in inventory['repositories']for row in repo['inspected_only_public_pinned_files']]

def observe(item):
 repo,row=item;spec=row['revision']+':'+row['source_path']
 command=['/opt/homebrew/bin/git','--no-optional-locks','show',spec]
 out=subprocess.run(command,cwd=repo['absolute_path'],capture_output=True,
                    env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'},timeout=30)
 observed=hashlib.sha256(out.stdout).hexdigest()if out.returncode==0 else None
 header=('blob '+str(len(out.stdout))+'\0').encode()
 blob=hashlib.sha1(header+out.stdout).hexdigest()if out.returncode==0 else None
 return {'repository':repo['repository'],'revision':row['revision'],'source_path':row['source_path'],
         'expected_snapshot_sha256':row['sha256'],'observed_git_blob_sha256':observed,
         'observed_git_blob_sha1':blob,'blob_bytes':len(out.stdout)if out.returncode==0 else None,
         'matches':observed==row['sha256'],'command':command,'cwd':repo['absolute_path'],
         'exit_code':out.returncode,'stderr':out.stderr.decode(),
         'purpose':row['purposes'],'source_executed':False,'external_changes':'sem alterações'}

with ThreadPoolExecutor(max_workers=4)as pool:rows=list(pool.map(observe,inputs))
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'inventory':'repository-inspected-files-v2.json',
        'inventory_sha256':hashlib.sha256((P/'repository-inspected-files-v2.json').read_bytes()).hexdigest(),
        'records':rows,'selected_local_git_file_identities':len(rows),
        'repositories_with_selected_public_blobs':len({r['repository']for r in rows}),
        'all_commands_successful':all(r['exit_code']==0 for r in rows),
        'all_retained_snapshot_hashes_match_exact_git_revision_blobs':all(r['matches']for r in rows),
        'outside42_installed_rails_source_not_git_checked':inventory['retained_source_snapshots_not_in42clones'],
        'scope':'Read69selectedpublicGitblobidentitiesonly; no checkout/index writes, upstream applications/tests/private sources or claimsemanticreadjudication. Thiscross-checkdoesnotcleartrainingrightsorindependence.',
        'gold':0,'optimizer_updates':0}
with(P/'selected-source-git-binding-audit-v1.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps({k:v for k,v in result.items()if k not in ['records','outside42_installed_rails_source_not_git_checked']},indent=2))
