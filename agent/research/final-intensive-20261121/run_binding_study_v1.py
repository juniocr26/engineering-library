"""Observe pre-frozen receipt mutations without editing source artifacts."""
from pathlib import Path
import copy
import datetime
import hashlib
import json
import time
import binding_envelope_v1 as profile

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
protocol_raw = (P/'binding-study-protocol-v1.json').read_bytes()
protocol = json.loads(protocol_raw)
anchor_raw = (P/protocol['anchor_path']).read_bytes()
assert profile.digest(anchor_raw) == protocol['anchor_sha256']
anchor = json.loads(anchor_raw)
freeze = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'protocol_sha256': profile.digest(protocol_raw),
          'producer_sha256': profile.digest(Path(__file__).read_bytes()), 'validator_sha256': profile.digest((P/'binding_envelope_v1.py').read_bytes())}
with (P/'binding-validator-freeze-v1.json').open('x') as stream:
    json.dump(freeze, stream, indent=2)
    stream.write('\n')
rows = []
start = time.monotonic()
for case in protocol['cases']:
    trusted = anchor[case['task']]
    envelope = copy.deepcopy(trusted)
    overlay, missing, symlinks = {}, set(), set()
    mutation, value = case['mutation'], case['value']
    if mutation in ['missing_role', 'append_bytes', 'symlink_role']:
        item = next(x for x in envelope['dependencies'] if x['role'] == value)
        if mutation == 'missing_role':
            missing.add(item['path'])
        elif mutation == 'symlink_role':
            symlinks.add(item['path'])
        else:
            overlay[item['path']] = (ROOT/item['path']).read_bytes()+b'\n'
    elif mutation == 'change_envelope':
        node = envelope
        for key in value[:-2]:
            node = node[key]
        node[value[-2]] = value[-1]
    elif mutation == 'drop_requirement':
        envelope['source_identity']['required_ids'].pop()
    elif mutation == 'rehash_candidate':
        item = next(x for x in envelope['dependencies'] if x['role'] == 'candidate')
        raw = (ROOT/item['path']).read_bytes()+b'\n'
        overlay[item['path']] = raw
        item['sha256'], item['bytes'] = profile.digest(raw), len(raw)
    elif mutation == 'change_path':
        next(x for x in envelope['dependencies'] if x['role'] == 'source')['path'] = value
    raw = profile.canonical(envelope)
    if mutation == 'duplicate_json':
        raw = b'{"task":"forged",'+raw[1:]
    reasons = profile.validate(raw, trusted, ROOT, overlay, missing, symlinks)
    result = 'REFUSED' if reasons else 'VALID'
    rows.append({**case, 'observed': result, 'matches_frozen_expectation': result == case['expected'],
                 'reasons': reasons, 'envelope_sha256': profile.digest(raw),
                 'new_technical_acceptance': False, 'semantic_verifier_executed': False})
negatives = [x for x in rows if x['expected'] == 'REFUSED']
positives = [x for x in rows if x['expected'] == 'VALID']
result = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'protocol_sha256': profile.digest(protocol_raw),
          'wall_seconds': time.monotonic()-start, 'records': rows,
          'integrity_false_admission': {'numerator': sum(x['observed']=='VALID' for x in negatives), 'denominator': len(negatives)},
          'integrity_false_refusal': {'numerator': sum(x['observed']=='REFUSED' for x in positives), 'denominator': len(positives)},
          'all_frozen_expectations_match': all(x['matches_frozen_expectation'] for x in rows),
          'population': '63 owned mutations of three development-exposed historical K envelopes; strongly correlated, manually selected controls.',
          'baseline': 'Historical candidate/review/source byte pins; no unchanged production admission comparator measured.',
          'confidence_limitations': 'Not semantic verifier false-acceptance/rejection, not independent model benchmark, no automatic acceptance/Gold/publication. Caller-owned anchor assumed trustworthy. Static symlink preflight not TOCTOU-safe.',
          'model_calls': 0, 'optimizer_updates': 0, 'gold': 0}
with (P/'binding-study-results-v1.json').open('x') as stream:
    json.dump(result, stream, indent=2, ensure_ascii=False)
    stream.write('\n')
print(json.dumps({key: result[key] for key in ['all_frozen_expectations_match', 'integrity_false_admission', 'integrity_false_refusal', 'wall_seconds']}))
