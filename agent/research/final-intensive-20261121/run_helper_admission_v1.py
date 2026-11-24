"""Exercise existing extraction/validation only; never execute inspected sources."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import sys
import time

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
sys.path.insert(0,str(ROOT/'agent/tools'))
import documentation_retrieval as retrieval

sha = lambda raw: hashlib.sha256(raw).hexdigest()
protocol_raw = (P/'helper-admission-protocol-v1.json').read_bytes()
protocol = json.loads(protocol_raw)
for item in protocol['dependencies']:
    assert sha((ROOT/item['path']).read_bytes()) == item['sha256']
refs = {r['claim_id']:r for r in json.loads((ROOT/'agent/research/acceptance-calibration-20261121/atomic-reference-ledger-v2.json').read_text())['claims']}
output = P/'helper-admission-observations-v1'
output.mkdir()
rows=[]
for task in protocol['tasks']:
    raw=(P/'reacquired-public-sources'/task['task']/task['path']).read_bytes()
    assert sha(raw)==task['source_sha256']
    start=time.monotonic()
    unit=None
    error=None
    admitted=False
    try:
        unit=retrieval.extract(raw.decode(),task['selector'],task['language'])
        retrieval.validate_unit(unit,raw,task['selector'],task['language'])
        admitted=True
    except Exception as exc:
        error={'class':type(exc).__name__,'message':str(exc)}
    covered=[]
    if admitted:
        for cid in task['claim_ids']:
            ref=refs[cid]
            if (unit['first_line'] <= ref['source_lines'][0] <= ref['source_lines'][1] <= unit['last_line']
                    and ref['exact_source_evidence'] in unit['quote']):
                covered.append(cid)
    status='ADMITTED_LEXICAL_UNIT' if admitted else 'REFUSED'
    row={**task,'actual':status,'error':error,'extracted_intermediate_unit':unit,
         'admitted_quote_covers_reference_ids':covered,
         'uncovered_reference_ids':[cid for cid in task['claim_ids'] if cid not in covered],
         'matches_frozen_status':status==task['expected'],
         'matches_frozen_reason':task.get('expected_reason') is None or task['expected_reason'] in (error or {}).get('message',''),
         'wall_seconds':time.monotonic()-start,'source_program_executed':False,'runtime_bindings_verified':False}
    with (output/(task['id']+'.json')).open('x') as stream:
        json.dump(row,stream,indent=2,ensure_ascii=False)
        stream.write('\n')
    rows.append(row)
covered=sorted({cid for row in rows for cid in row['admitted_quote_covers_reference_ids']})
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':sha(protocol_raw),
        'producer_sha256':sha(Path(__file__).read_bytes()),'records':rows,
        'admitted_requests':{'numerator':sum(r['actual']=='ADMITTED_LEXICAL_UNIT' for r in rows),'denominator':len(rows)},
        'exact_required_evidence_span_coverage':{'numerator':len(covered),'denominator':28},'covered_reference_ids':covered,
        'all_frozen_status_expectations_match':all(r['matches_frozen_status'] for r in rows),
        'all_frozen_refusal_causes_match':all(r['matches_frozen_reason'] for r in rows),
        'population':'Eight owned API-phase requests covering28 existing K reference propositions in three development-exposed families.',
        'baseline':'All28 facts source-reviewed using separate Git/static procedures; not previously asserted as helper-acquired.',
        'method':'Actual existing extract and validate_unit on immutable source text, without helper journal, job wrapper or model.',
        'confidence_limitations':'Not model accuracy, general helper success rate, retrieval semantic correctness or complete-document acceptance. Refusal may be an intended boundary. No source code executed; owned parser binary executed.',
        'source_size_max':retrieval.MAX_SOURCE,'quote_size_max':retrieval.MAX_QUOTE,
        'native_parser_installed_used':True,'permanent_tests_executed':False,
        'model_calls':0,'optimizer_updates':0,'gold':0}
with (P/'helper-admission-results-v1.json').open('x') as stream:
    json.dump(result,stream,indent=2,ensure_ascii=False)
    stream.write('\n')
print(json.dumps({key:result[key] for key in ['admitted_requests','exact_required_evidence_span_coverage','all_frozen_status_expectations_match','all_frozen_refusal_causes_match']}))
