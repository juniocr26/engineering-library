"""Freeze real-revision lifecycle questions before source-diff adjudication."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
baseline = json.loads((P/'baseline-verification-v1.json').read_text())
repos = {row['repository']: row for row in baseline['repositories']}
parent = 'b586e484a56ef7e868c7257b2ea11ad9f71b606b'
child = '7dbc3b696ddafb6a302ae47ea412e85b587bc308'
protocol = {
    'frozen_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'question': 'Does the real full-callable cache-validation revision require a bounded maintenance note for existing helper documentation, and can external clone ancestors establish real before/after scope?',
    'self_task': {'repository': 'engineering-library', 'before': parent, 'after': child,
                  'source_paths': ['agent/tools/documentation_retrieval.py', 'agent/tools/documentation_job_budget.py', 'agent/tools/documentation_retrieval.md'],
                  'existing_document': 'agent/tools/documentation_retrieval.md',
                  'declared_scope': 'Version and cached complete lexical-unit revalidation, call sites, exception boundary; no source or doc integration.',
                  'audience': 'Operator integrating the optional bounded helper API',
                  'languages': ['en', 'pt-BR'],
                  'mandatory': ['Old and new source identity', 'Version delta', 'Python complete callable reconstruction', 'Go complete callable reconstruction', 'Cached and fresh call-site tracing', 'Static-only limits', 'Known cached subprocess exception boundary', 'No execution claim', 'Existing documentation impact'],
                  'criterion': 'MODIFY only with pinned old/new source plus existing document evidence; no runtime behavior inferred beyond written control flow.'},
    'external_tasks': [{'repository': name, 'after': repos[name]['head'], 'before': 'first-parent-of-after', 'criterion': 'If first parent object unavailable locally, INCONCLUSIVE; do not fetch, invent before behavior or infer REMOVE.'} for name in ['fastapi', 'cobra', 'zod']],
    'independence': 'Same-agent static source/diff review; original helper defect experiments are retained and will not be rerun as new discoveries.',
    'no_external_execution': True, 'no_private_product_source': True,
    'training_excluded': True, 'owner_approval': False,
}
with (P/'real-revision-protocol-v1.json').open('x') as stream:
    json.dump(protocol, stream, indent=2)
    stream.write('\n')
out = P/'real-revision-evidence-v1'
out.mkdir()
observations = []
for revision, label in [(parent, 'before'), (child, 'after')]:
    for name in protocol['self_task']['source_paths']:
        command = ['git', '--no-optional-locks', '-C', str(ROOT), 'show', revision+':'+name]
        result = subprocess.run(command, capture_output=True, timeout=30)
        destination = out/label/name
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('xb') as stream:
            stream.write(result.stdout)
        observations.append({'command': command, 'exit_code': result.returncode, 'stderr': result.stderr.decode(),
                             'saved_path': str(destination.relative_to(ROOT)), 'sha256': hashlib.sha256(result.stdout).hexdigest()})
        assert result.returncode == 0
command = ['git', '--no-optional-locks', '-C', str(ROOT), 'diff', parent, child, '--', *protocol['self_task']['source_paths']]
diff = subprocess.run(command, capture_output=True, timeout=30)
with (out/'selected-revision.diff').open('xb') as stream:
    stream.write(diff.stdout)
observations.append({'command': command, 'exit_code': diff.returncode, 'stderr': diff.stderr.decode(), 'sha256': hashlib.sha256(diff.stdout).hexdigest(), 'saved_path': str((out/'selected-revision.diff').relative_to(ROOT))})
external = []
for task in protocol['external_tasks']:
    name = task['repository']
    folder = repos[name]['absolute_path']
    results = []
    for args in [['rev-parse', '--is-shallow-repository'], ['rev-parse', '--verify', task['after']+'^']]:
        command = ['git', '--no-optional-locks', '-C', folder, *args]
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        results.append({'command': command, 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
    external.append({'repository': name, 'observations': results, 'before_available': results[1]['exit_code']==0,
                     'lifecycle_status': 'INCONCLUSIVE' if results[1]['exit_code'] else 'PENDING_SOURCE_COMPARISON',
                     'reason': 'Missing first-parent object prevents before/after claim; no deletion or source absence inference.', 'changes': 'sem alterações'})
with (P/'real-revision-acquisition-v1.json').open('x') as stream:
    json.dump({'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'self_observations': observations, 'external': external,
               'runtime_or_tests_executed': False, 'model_calls': 0}, stream, indent=2, ensure_ascii=False)
    stream.write('\n')
print(json.dumps({'self_objects_preserved': len(observations)-1, 'external': [{k:r[k] for k in ['repository', 'before_available', 'lifecycle_status']} for r in external]}))
