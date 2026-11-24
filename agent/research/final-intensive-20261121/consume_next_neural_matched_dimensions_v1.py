import argparse,json,hashlib,copy,re
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True,type=Path);root=ap.parse_args().root.resolve();p=root/'agent/research/final-intensive-20261121';folder=p/'next-neural-matched-dimensions-v2';sha=lambda b:hashlib.sha256(b).hexdigest()
protocol=json.loads((p/'next-neural-matched-dimensions-protocol-v1.json').read_bytes());receipt=json.loads((folder/'preparation-receipt.json').read_bytes());assert receipt['protocol_sha256']==sha((p/'next-neural-matched-dimensions-protocol-v1.json').read_bytes())
assert protocol['actual_current_model_calls']==receipt['actual_model_calls']==0 and receipt['actual_generated_tokens']==0
for artifact in receipt['artifacts']:assert sha((root/artifact['path']).read_bytes())==artifact['sha256']
requests={arm:json.loads((folder/('arm-'+arm+'-request.json')).read_bytes()) for arm in ['A','B']}
a,b=requests['A'],requests['B'];extract=lambda x:json.loads(x['messages'][-1]['content'].split('BEGIN SOURCE JSON\n',1)[1].split('\nEND SOURCE JSON',1)[0]);ca,cb=extract(a),extract(b);removed={'preparation','syntax_producer','syntax_parser_version'}
assert len(ca)==len(cb)==4
for key in ca:assert {k:v for k,v in ca[key].items() if k not in removed}==cb[key] and set(ca[key])-set(cb[key])==removed
for field in ['model','stream','format','options','keep_alive']:assert a[field]==b[field]
assert a['messages'][0]==b['messages'][0]
source=(root/protocol['frozen_source']['source']['path']).read_bytes();assert sha(source)==protocol['frozen_source']['source']['sha256'] and ca['S4']['quote'].encode()==source
lines=source.splitlines(keepends=True)
for key in ['S1','S2','S3']:
 card=ca[key];quote=card['quote'].encode();assert b''.join(lines[card['line']-1:card['line']-1+len(quote.splitlines())])==quote
meta=json.loads((folder/'external-provenance-envelope.json').read_bytes());assert meta['all_original_source_cards']==ca
for e in meta['skills']:assert sha((root/e['path']).read_bytes())==e['sha256']
identity=json.loads((root/'agent/recovery/manifest.json').read_bytes())['model'];assert protocol['future_model_settings']['expected_runtime_digest']==identity['runtime_digest'] and a['model']==identity['name']
for edge in json.loads((p/'remaining-chapters-recovery-dependencies-v37.json').read_bytes())['dependencies']:assert sha((root/edge['path']).read_bytes())==edge['sha256']
audit=json.loads((p/'next-neural-matched-dimensions-request-audit-v1.json').read_bytes());assert audit['actual_model_calls']==0 and audit['full_reference_prose_paragraph_matches_in_requests']==0 and audit['source_cards']==4
print(json.dumps({'status':'PASS_NOT_RUN_MATCHED_DEV_REQUEST_RECOVERY','requests':2,'source_cards':4,'whole_source_quote_recovered':True,'skill_files':3,'metadata_factor_field_names':3,'prompt_content_bytes':receipt['prompt_content_bytes'],'model_calls':0,'model_performance_measured':False,'context_admission_verified':False,'publication_authorized':False,'training_gold':False}))
