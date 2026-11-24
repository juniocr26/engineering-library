"""Read-only repository metadata and immutable dataset verification."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import time

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
prior = json.loads((ROOT/'agent/research/acceptance-calibration-20261121/baseline-verification-v1.json').read_text())
started = time.monotonic()
rows = []
for old in prior['repositories']:
    folder = Path(old['absolute_path'])
    observations = []
    for args in [['rev-parse', 'HEAD'], ['status', '--porcelain=v1', '--untracked-files=normal']]:
        command = ['git', '--no-optional-locks', '-C', str(folder), *args]
        result = subprocess.run(command, capture_output=True, text=True, timeout=40)
        observations.append({'command': command, 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
    head = observations[0]['stdout'].strip()
    status = observations[1]['stdout']
    rows.append({'repository': old['repository'], 'collection': old['collection'], 'absolute_path': str(folder), 'head': head,
                 'prior_head': old['head'], 'matches_prior_head': head == old['head'], 'status': status,
                 'matches_prior_status': status == old['status'], 'observations': observations,
                 'source_body_read': False, 'campaign_changes': 'sem alterações' if folder != ROOT else 'research and canonical reports only'})
datasets = []
for old in prior['datasets']:
    raw = (ROOT/old['path']).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    datasets.append({'path': old['path'], 'sha256': digest, 'matches_prior': digest == old['sha256'],
                     'records': len(raw.splitlines()), 'row_semantics_reviewed': False})
versions = {}
for name in prior['versions']:
    source = (ROOT/name).read_text()
    versions[name] = [line.strip() for line in source.splitlines() if line.strip().startswith('VERSION =')]
result = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'wall_seconds': time.monotonic()-started,
          'repositories': rows, 'repository_count': len(rows), 'datasets': datasets, 'records': sum(x['records'] for x in datasets),
          'versions': versions, 'all_dataset_hashes_match': all(x['matches_prior'] for x in datasets),
          'all_external_heads_match_prior': all(x['matches_prior_head'] for x in rows if Path(x['absolute_path']) != ROOT),
          'all_external_statuses_match_prior': all(x['matches_prior_status'] for x in rows if Path(x['absolute_path']) != ROOT),
          'git_index_sha256': hashlib.sha256((ROOT/'.git/index').read_bytes()).hexdigest(),
          'scope': 'Metadata only for private/external repositories. No reserve source or private body read. Original datasets hashed and counted, not semantically re-audited.',
          'model_current_identity': 'UNVERIFIED_DOCKER_PERMISSION_DENIED', 'neural_calls': 0, 'optimizer_updates': 0, 'gold': 0}
with (P/'baseline-verification-v1.json').open('x') as stream:
    json.dump(result, stream, indent=2, ensure_ascii=False)
    stream.write('\n')
print(json.dumps({k: result[k] for k in ['repository_count', 'records', 'all_dataset_hashes_match', 'all_external_heads_match_prior', 'all_external_statuses_match_prior', 'wall_seconds']}))
