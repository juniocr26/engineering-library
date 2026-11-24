"""Read-only pinned training-framework source and model metadata, never weights."""
import datetime
import hashlib
import json
from pathlib import Path
import urllib.request

P = Path(__file__).resolve().parent
OUT = P / 'training-primary-sources-v1'
OUT.mkdir(exist_ok=False)
rows = []


def fetch(url, name, cap=524288):
    row = {'url': url, 'name': name, 'at': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'EngineeringLibraryReadinessResearch/1.0'}), timeout=40) as response:
            raw = response.read(cap + 1);row['status_code'] = response.status
        if len(raw) > cap:
            raise ValueError('metadata byte cap exceeded')
        path = OUT / name
        with path.open('xb') as stream:stream.write(raw)
        row.update(status='preserved', bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        rows.append(row)
        return raw
    except Exception as error:
        row.update(status='failed', error=str(error));rows.append(row)
        return None


raw = fetch('https://api.github.com/repos/ml-explore/mlx-lm/commits/main', 'mlx-lm-head.json')
if raw:
    rev = json.loads(raw)['sha']
    for path in ['README.md', 'mlx_lm/LORA.md', 'mlx_lm/lora.py', 'mlx_lm/tuner/trainer.py', 'mlx_lm/tuner/datasets.py', 'pyproject.toml', 'LICENSE']:
        fetch('https://raw.githubusercontent.com/ml-explore/mlx-lm/' + rev + '/' + path, 'mlx-lm--' + path.replace('/', '--'))
for model, name in [('mlx-community/Llama-3.2-3B-Instruct-4bit', 'community-3b'), ('meta-llama/Llama-3.2-3B-Instruct', 'upstream-3b')]:
    raw = fetch('https://huggingface.co/api/models/' + model, name + '-metadata.json')
    if raw:
        rev = json.loads(raw).get('sha')
        if rev:
            for path in ['README.md', 'config.json', 'tokenizer_config.json', 'LICENSE.txt']:
                fetch('https://huggingface.co/' + model + '/resolve/' + rev + '/' + path, name + '--' + path)
with (P / 'training-primary-source-provenance-v1.json').open('x') as stream:
    json.dump({'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'rows': rows,
               'weights_requested': False, 'tokenizer_weights_requested': False, 'framework_installed': False,
               'source_executed': False, 'neural_training': False}, stream, indent=2)
print(json.dumps({'preserved': sum(r['status'] == 'preserved' for r in rows), 'failed': [r for r in rows if r['status'] != 'preserved']}))
