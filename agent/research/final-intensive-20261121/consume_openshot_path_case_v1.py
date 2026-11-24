"""Validate restored prospective evaluation bindings, never score semantic/model correctness."""
from pathlib import Path
import argparse,ast,json,hashlib
parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args()
P=args.root/'agent/research/final-intensive-20261121';case=json.loads((P/'openshot-path-evaluation-case-v2.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
assert case['status']=='FROZEN_NOT_EXECUTED' and not case['training_eligible'] and case['new_inference_calls']==0
for row in case['source_files']:
 f=args.root/row['path'];raw=f.read_bytes();assert sha(raw)==row['sha256'] and len(raw)==row['bytes'];ast.parse(raw,filename=row['name'])
for row in case['reference_propositions']:
 raw=(args.root/row['snapshot']).read_bytes();assert sha(raw)==row['file_sha256'];lines=raw.decode().splitlines();quote='\n'.join(lines[row['start_line']-1:row['end_line']])+'\n';assert quote==row['quote'] and sha(quote.encode())==row['quote_sha256']
assert len(case['reference_propositions'])==21 and len(case['adverse_reference_claims'])==10
print(json.dumps({'task':case['task_id'],'source_hashes_and_syntax_matched':len(case['source_files']),'reference_quote_bindings_matched':21,'semantic_accuracy_measured':False,'model_evaluated':False,'target_source_executed':False,'certified_holdout':False}))
