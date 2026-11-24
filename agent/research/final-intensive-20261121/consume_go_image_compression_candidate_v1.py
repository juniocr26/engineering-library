import argparse,json,hashlib,re
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);a=ap.parse_args();p=a.root/'agent/research/final-intensive-20261121';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();m=json.loads((p/'go-image-compression-recovery-manifest-v1.json').read_text())
for edge in m['external_dependencies']:assert sha(a.root/edge['path'])==edge['sha256']
for edge in m['source_files']:assert sha(a.root/edge['saved_path'])==edge['sha256']
for edge in m['changes']:
 before=(a.root/edge['source_path']).read_text();after=(a.root/edge['candidate_path']).read_text();assert sha(a.root/edge['source_path'])==edge['before_sha256'];assert sha(a.root/edge['candidate_path'])==edge['candidate_sha256'];assert before.replace(edge['replacement_before'],edge['replacement_after'])==after;assert re.findall(r'```.*?```',before,re.S)==re.findall(r'```.*?```',after,re.S)
witnesses={}
for w in m['witnesses']:
 assert sha(a.root/w['request_path'])==w['request_sha256'];assert sha(a.root/w['response_path'])==w['response_sha256'];witnesses[w['id']]=json.loads(json.loads((a.root/w['response_path']).read_text())['message']['content'])['facts']
assert 'checks again for an error in the context' in witnesses['gio-compression-flow-caller'][0]['en'];assert all('context' not in r['en'].lower() for r in witnesses['gio-compression-flow-helpers'])
review=json.loads((p/m['review']).read_text());group=next(r for r in review['source_claim_groups'] if r['id']=='P7');raw=(p/'go-image-compression-source-context-v1'/group['path']).read_text().splitlines();quote='\n'.join(raw[group['lines'][0]-1:group['lines'][1]]);assert 'useCase.Execute(r.Context(), imageBytes)' in quote and 'writeCompressionError' in quote and 'w.Write(result.Data)' in quote
print(json.dumps({'status':'PASS_BOUND_COMPRESSION_TARGET_AND_ATTRIBUTION_RECOVERY','external_edges':len(m['external_dependencies']),'source_files':len(m['source_files']),'candidate_documents':len(m['changes']),'target_execution':False,'new_model_calls':0,'general_semantic_verifier':False}))
