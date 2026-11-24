"""Freeze restoration and negative controls for the exact original K renderer."""
from pathlib import Path
import datetime
import hashlib
import json

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
PRIOR = ROOT/'agent/research/acceptance-calibration-20261121'
anchor = json.loads((P/'trusted-binding-anchor-v1.json').read_text())
dependencies = {item['path'] for bundle in anchor.values() for item in bundle['dependencies']}
dependencies |= {str((PRIOR/name).relative_to(ROOT)) for name in ['render_verified_fact_note_v1.py', 'frozen_schema_subset_v2.py']}
rows = [{'path': name, 'sha256': hashlib.sha256((ROOT/name).read_bytes()).hexdigest(), 'bytes': (ROOT/name).stat().st_size} for name in sorted(dependencies)]
cases = []
for task in ['fastapi', 'cobra', 'zod']:
    for kind, expected, scope in [
        ('baseline', 'ASSEMBLED_EXACT_SEMANTIC_PAYLOAD', 'Identical preserved trusted inputs; timestamp may differ.'),
        ('missing-schema-module', 'NO_ASSEMBLY', 'Restore dependency missing.'),
        ('missing-source', 'NO_ASSEMBLY', 'Pinned source snapshot missing.'),
        ('missing-review', 'NO_ASSEMBLY', 'Semantic review receipt missing.'),
        ('stale-content', 'NO_ASSEMBLY', 'Changed valid JSON model string without new content-bound review.'),
        ('wrong-reference-revision', 'REQUIRES_DEPENDENCY_PIN', 'Alter only reference citation revision, preserving source hashes, fact text and old review.'),
        ('invented-metadata-test-claim', 'REQUIRES_DEPENDENCY_PIN', 'Alter frozen manual scope metadata to claim tests passed, preserving neural text and old review.'),
    ]:
        cases.append({'id': task+'-'+kind, 'task': task, 'kind': kind, 'expected': expected, 'scope': scope})
protocol = {'frozen_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'hypothesis': 'The exact original renderer can be restored with dependency closure and reproduce semantic payload; candidate-content pins alone may not detect tampered reference/metadata dependencies before assembly. Caller-owned dependency envelope should refuse those changes.',
            'cases': cases, 'dependencies': rows,
            'replay': 'Run only the original owned research renderer with preserved outputs/inputs in separate temporary case roots; never execute upstream source or model inference.',
            'output_preservation': 'Original rendered candidates included in capsule but kept outside replay target to allow exclusive creation; baseline compared after removing timestamp only.',
            'acceptance_boundary': 'Renderer assembly is not complete-note technical acceptance. No mutated candidate is submitted to, or credited as passing, the complete-note review. Dependency tampering is an owned integrity challenge, not evidence original frozen trusted inputs were wrong.',
            'production_integration': False, 'new_model_calls': 0, 'optimizer_updates': 0, 'gold': 0}
with (P/'renderer-recovery-protocol-v1.json').open('x') as stream:
    json.dump(protocol, stream, indent=2)
    stream.write('\n')
print(json.dumps({'cases': len(cases), 'dependencies': len(rows)}))
