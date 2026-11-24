import datetime
import hashlib
import json
from pathlib import Path
import urllib.request

P = Path(__file__).resolve().parent
OUT = P / 'training-primary-sources-v1'
rows = []


def fetch(url, name):
    row = {'url': url, 'name': name, 'at': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'EngineeringLibraryReadinessResearch/1.0'}), timeout=40) as response:
            raw = response.read(524289);row['status_code'] = response.status
        if len(raw) > 524288:
            raise ValueError('metadata byte cap exceeded')
        with (OUT / name).open('xb') as stream:stream.write(raw)
        row.update(status='preserved', bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest());rows.append(row)
        return raw
    except Exception as error:
        row.update(status='failed', error=str(error));rows.append(row)
        return None


raw = fetch('https://api.github.com/repos/ml-explore/mlx-lm/git/ref/heads/main', 'mlx-lm-main-ref.json')
if raw:
    rev = json.loads(raw)['object']['sha']
    for path in ['README.md', 'mlx_lm/LORA.md', 'mlx_lm/lora.py', 'mlx_lm/tuner/trainer.py', 'mlx_lm/tuner/datasets.py', 'pyproject.toml', 'LICENSE']:
        fetch('https://raw.githubusercontent.com/ml-explore/mlx-lm/' + rev + '/' + path, 'mlx-lm--' + path.replace('/', '--'))
with (P / 'training-framework-source-provenance-v1.json').open('x') as stream:
    json.dump({'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'reason': 'Git commits endpoint exceeded cap due to attached diff; use bounded git-ref endpoint instead. No gated upstream config retry or credential access.', 'rows': rows, 'source_executed': False, 'packages_installed': False, 'training_steps': 0}, stream, indent=2)
print(json.dumps({'preserved': sum(r['status'] == 'preserved' for r in rows), 'failed': [r for r in rows if r['status'] != 'preserved']}))
