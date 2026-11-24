"""Finite retained-study replay; not semantic equivalence validation."""
import argparse,json,hashlib,re
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True,type=Path);a=ap.parse_args();p=a.root/'agent/research/final-intensive-20261121'
raw=(p/'bilingual-guard-study-protocol-v1.json').read_bytes();protocol=json.loads(raw);result=json.loads((p/'bilingual-guard-study-results-v1.json').read_text());assert hashlib.sha256(raw).hexdigest()==result['protocol_sha256'];assert hashlib.sha256((p/'source-claim-reacquisition-results-v1.json').read_bytes()).hexdigest()==protocol['reference_sha256'];policy=protocol['frozen_policy'];records=[]
for case in protocol['cases']:
 missing={lang:[lit for lit in policy['identifiers'][case['claim_id']] if lit not in case[lang]] for lang in ('en','pt-BR')};flags=[]
 if any(missing.values()):flags.append('PROTECTED_LITERAL_MISSING')
 if bool(re.search(policy['en_negation_pattern'],case['en'],re.I))!=bool(re.search(policy['pt_negation_pattern'],case['pt-BR'],re.I)):flags.append('NEGATION_PRESENCE_DIFFERS')
 records.append({'id':case['id'],'category':case['category'],'verdict':'FLAG' if flags else 'SCREEN_CLEAR','flags':flags,'missing':missing,'manual_reference_pair_equivalence':case['manual_reference_pair_equivalence'],'technical_acceptance':False})
assert records==result['records']
metric=json.loads((p/'requested-metric-reconciliation-v1.json').read_text());assert metric['request_sha256']==hashlib.sha256((p/'user-request-original-v1.txt').read_bytes()).hexdigest();assert metric['audit_sha256']==hashlib.sha256((p/'current-metric-population-audit-results-v2.json').read_bytes()).hexdigest();assert len(metric['records'])==16
print(json.dumps({'status':'PASS_RETAINED_SCREEN_REPLAY_AND_METRIC_BINDINGS','owned_controls':len(records),'requested_metric_names':16,'semantic_verification':False,'model_calls':0}))
