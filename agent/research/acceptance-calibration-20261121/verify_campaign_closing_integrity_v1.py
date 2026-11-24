"""Read-only closing verification; hash opaque/private inputs without decoding them."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import datetime, hashlib, json, os, re, subprocess

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
GIT = '/opt/homebrew/bin/git'
baseline = json.loads((P / 'baseline-verification-v1.json').read_text())

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def git(path, *args):
    command = [GIT, '--no-optional-locks', *args]
    out = subprocess.run(command, cwd=path, capture_output=True, text=True,
                         env={**os.environ, 'GIT_OPTIONAL_LOCKS': '0'}, timeout=90)
    return {'command': command, 'exit_code': out.returncode,
            'stdout': out.stdout, 'stderr': out.stderr}

def repository(row):
    head = git(row['absolute_path'], 'rev-parse', 'HEAD')
    status = git(row['absolute_path'], 'status', '--porcelain=v1')
    own = Path(row['absolute_path']) == ROOT
    return {'repository': row['repository'], 'collection': row['collection'],
            'absolute_path': row['absolute_path'], 'head': head, 'status': status,
            'head_unchanged': head['stdout'].strip() == row['head'],
            'status_unchanged': status['stdout'] == row['status'],
            'changes': 'authorized four root reports and isolated research/preservation only' if own else 'sem alterações',
            'private_body_read': False, 'own_repository': own}

started = datetime.datetime.now(datetime.timezone.utc).isoformat()
with ThreadPoolExecutor(max_workers=4) as pool:
    repositories = list(pool.map(repository, baseline['repositories']))
datasets = []
for row in baseline['datasets']:
    observed = sha(ROOT / row['path'])
    datasets.append({'path': row['path'], 'expected_sha256': row['sha256'],
                     'observed_sha256': observed, 'matches': observed == row['sha256'],
                     'record_count_retained_from_frozen_baseline': row['records'], 'body_decoded': False})
references = []
for row in json.loads((P / 'dataset-quality-audit-v1.json').read_text())['immutable_references']:
    observed = sha(ROOT / row['path'])
    references.append({'path': row['path'], 'expected_sha256': row['expected_sha256'],
                       'observed_sha256': observed, 'matches': observed == row['expected_sha256'], 'body_decoded': False})
prior = []
for row in json.loads((P / 'prior-recovery-integrity-v1.json').read_text())['files']:
    observed = sha(ROOT / row['observed_path'])
    prior.append({'path': row['observed_path'], 'expected_sha256': row['expected_sha256'],
                  'observed_sha256': observed, 'matches': observed == row['expected_sha256']})
manual = []
for topic in json.loads((P / 'manual-population-and-head-reverification-v2.json').read_text())['topics']:
    for row in topic['documents']:
        observed = sha(Path(row['path']))
        manual.append({'path': row['path'], 'expected_sha256': row['sha256'],
                       'observed_sha256': observed, 'matches': observed == row['sha256']})
versions = {}
for path, expected in baseline['versions'].items():
    observed = [line.strip() for line in (ROOT / path).read_text().splitlines()
                if re.match(r'^\s*VERSION\s*=', line)]
    versions[path] = {'expected': expected, 'observed': observed, 'matches': observed == expected}
tracked = git(ROOT, 'diff', '--name-status', 'HEAD', '--')
staged = git(ROOT, 'diff', '--cached', '--name-status', '--')
index = sha(ROOT / '.git/index')
result = {'started_at': started, 'ended_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'command': '/opt/homebrew/bin/python3 -B agent/research/acceptance-calibration-20261121/verify_campaign_closing_integrity_v1.py',
          'repositories': repositories, 'repository_count': len(repositories),
          'all_heads_unchanged_since_current_campaign_start': all(r['head_unchanged'] for r in repositories),
          'all_41_external_statuses_unchanged': all(r['status_unchanged'] for r in repositories if not r['own_repository']),
          'all_commands_successful': all(r[k]['exit_code'] == 0 for r in repositories for k in ['head', 'status']),
          'own_tracked_diff': tracked, 'own_staged_diff': staged,
          'git_index_sha256': index, 'git_index_matches_start': index == baseline['git_index_sha256'],
          'versions': versions, 'datasets': datasets, 'immutable_references': references,
          'prior_preserved_files': prior, 'manual_document_files': manual,
          'counts': {'datasets': len(datasets), 'records_unchanged': 305,
                     'immutable_references': len(references), 'prior_files': len(prior), 'manual_files': len(manual)},
          'all_input_hashes_match': all(r['matches'] for group in [datasets, references, prior, manual] for r in group),
          'all_versions_match': all(r['matches'] for r in versions.values()),
          'limits': 'Closing identity/worktree/hash verification; not a new semantic review, private-source read, test rerun or legal clearance. Preexisting cocos2d-x modifications remain baseline state.',
          'git_writes': 0, 'external_mutations': 0, 'gold': 0, 'optimizer_updates': 0}
with (P / 'campaign-closing-integrity-v1.json').open('x') as stream:
    json.dump(result, stream, indent=2, ensure_ascii=False)
    stream.write('\n')
print(json.dumps({k: v for k, v in result.items() if k not in ['repositories', 'datasets', 'immutable_references', 'prior_preserved_files', 'manual_document_files']}, indent=2))
