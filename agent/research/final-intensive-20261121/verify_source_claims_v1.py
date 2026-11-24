"""Reacquire pinned public Git objects and audit exact 28 source claims."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
PRIOR = ROOT/'agent/research/acceptance-calibration-20261121'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
protocol = json.loads((PRIOR/'verified-fact-render-protocol-v1.json').read_text())
refs = json.loads((PRIOR/'atomic-reference-ledger-v2.json').read_text())['claims']
repos = {r['repository']: r for r in json.loads((P/'baseline-verification-v1.json').read_text())['repositories']}
selection = [r for r in refs if r['claim_id'] in protocol['metadata'].get(r['task'], {}).get('required_ids', [])]
assert len(selection) == 28
freeze = {'frozen_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'reference_ledger_sha256': sha((PRIOR/'atomic-reference-ledger-v2.json').read_bytes()),
          'selected_claim_ids': [r['claim_id'] for r in selection],
          'procedure': 'Fresh git show at each frozen revision; compare full file hashes and exact declared line spans. Compare model bilingual fact strings to reviewed reference and manually read source context. No runtime execution.',
          'semantic_review': 'Same campaign Codex agent read contextual source blocks and all 28 EN/PT fact pairs before this script. Separate Git acquisition, no independent human.',
          'semantic_scope': 'Only the 28 exact propositions, not all metadata, all prior outputs, general architecture or execution guarantees.',
          'expected': 'All 28 have exact source identity and support in declared static scope; do not adjust reference or span if discrepancy.',
          'producer_sha256': sha(Path(__file__).read_bytes())}
with (P/'source-claim-reacquisition-protocol-v1.json').open('x') as stream:
    json.dump(freeze, stream, indent=2)
    stream.write('\n')
acquired = {}
commands = []
(P/'reacquired-public-sources').mkdir()
for ref in selection:
    key = (ref['task'], ref['source_revision'], ref['source_path'])
    if key in acquired:
        continue
    task, revision, source_path = key
    command = ['git', '--no-optional-locks', '-C', repos[task]['absolute_path'], 'show', revision+':'+source_path]
    result = subprocess.run(command, capture_output=True, timeout=30)
    target = P/'reacquired-public-sources'/task/source_path
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as stream:
        stream.write(result.stdout)
    commands.append({'command': command, 'exit_code': result.returncode, 'stderr': result.stderr.decode(),
                     'saved_path': str(target.relative_to(ROOT)), 'sha256': sha(result.stdout), 'bytes': len(result.stdout)})
    assert result.returncode == 0
    acquired[key] = result.stdout
rows = []
for ref in selection:
    raw = acquired[(ref['task'], ref['source_revision'], ref['source_path'])]
    a, b = ref['source_lines']
    span = '\n'.join(raw.decode().splitlines()[a-1:b])
    content = json.loads((PRIOR/'verified-fact-render-v1'/ref['task']/'K/model-content.txt').read_text())
    pair = content['facts'][ref['claim_id']]
    physical = sha(raw) == ref['source_file_sha256'] and span == ref['exact_source_evidence']
    copied = pair == ref['expected_interpretation']
    rows.append({**ref, 'reacquired_source_sha256': sha(raw), 'exact_span_matches': span == ref['exact_source_evidence'],
                 'whole_file_identity_matches': sha(raw) == ref['source_file_sha256'], 'generated_interpretation': pair,
                 'exact_reviewed_bilingual_pair_matches': copied,
                 'current_static_verdict': 'SUPPORTED' if physical and copied else 'INCONCLUSIVE',
                 'current_review_basis': 'Source contextual reading and exact scoped proposition, not citation membership. Operational guarantees outside selected conditions remain unknown.',
                 'current_reviewer': 'Same Codex campaign agent; fresh Git acquisition; not independent-human review.',
                 'runtime_executed': False})
result = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'commands': commands, 'claims': rows,
          'source_identity_and_exact_span': {'numerator': sum(r['exact_span_matches'] and r['whole_file_identity_matches'] for r in rows), 'denominator': 28},
          'supported_exact_bilingual_reference_copies': {'numerator': sum(r['current_static_verdict']=='SUPPORTED' for r in rows), 'denominator': 28},
          'language_occurrences': 56, 'source_files': len(acquired), 'critical_errors_found_in_selected_pairs': sum(r['current_static_verdict']!='SUPPORTED' for r in rows),
          'population': 'Same 28 prior K source claims, three exposed related task families; repeated source review, not 28 new independent neural outputs.',
          'baseline': 'generation-K-results-v1.json reported 28/28 exact reference pairs.',
          'method': 'Source contextual review plus separate pinned Git object acquisition and exact spans.',
          'confidence_limitations': 'No holdout, new inference, exhaustive metadata review, runtime proof, owner/Gold/publication approval or model learning.',
          'neural_calls': 0, 'optimizer_updates': 0, 'gold': 0}
with (P/'source-claim-reacquisition-results-v1.json').open('x') as stream:
    json.dump(result, stream, indent=2, ensure_ascii=False)
    stream.write('\n')
print(json.dumps({k: result[k] for k in ['source_identity_and_exact_span', 'supported_exact_bilingual_reference_copies', 'source_files']}))
