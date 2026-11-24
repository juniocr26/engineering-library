"""Replay retained exact-byte/source-attribution bindings without executing target code."""
import argparse,json,hashlib,re
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);a=ap.parse_args();p=a.root/'agent/research/final-intensive-20261121';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
manifest=json.loads((p/'go-image-animation-candidate-recovery-manifest-v1.json').read_text())
for edge in manifest['external_dependencies']:assert sha(a.root/edge['path'])==edge['sha256']
for edge in manifest['candidate_documents']:
 before=(a.root/edge['source_path']).read_text();target=a.root/edge['candidate_path'];after=target.read_text();assert sha(target)==edge['candidate_sha256'];assert before.count(edge['replacement_before'])==1;assert before.replace(edge['replacement_before'],edge['replacement_after'])==after;assert re.findall(r'```.*?```',before,re.S)==re.findall(r'```.*?```',after,re.S)
review=json.loads((p/'go-image-historical-attribution-review-v1.json').read_text());base=a.root/'agent/research/acceptance-calibration-20261121/original-public-chapter-provenance-captures-v1'
for row in review['records']:
 q=json.loads((a.root/row['request']['path']).read_text());response=json.loads((a.root/row['response']['path']).read_text());assert json.loads(response['message']['content'])['facts']==row['facts']
 assert sha(a.root/row['request']['path'])==row['request']['sha256'];assert sha(a.root/row['response']['path'])==row['response']['sha256']
source=p/'go-image-animation-source-context-v1/backend/internal/infrastructure/imaging/limits.go';assert sha(source)=='b1b23e6c4721e843b93864a1109900d27217c58792a8e9def4fe9bb181044cb8';text=source.read_text();assert 'if width > maxPixels/height/frameCount' in text and 'if frameCount <= 0' in text
assert 'Se nenhuma dessas condições for atendida' in review['records'][0]['facts'][0]['pt-br'];assert 'ancho é menor que o número máximo' in review['records'][1]['facts'][0]['pt-br'];assert 'zero ou negativo' in review['records'][1]['facts'][1]['pt-br']
print(json.dumps({'status':'PASS_BOUND_TARGET_SOURCE_AND_HISTORICAL_ATTRIBUTION_RECOVERY','external_edges':len(manifest['external_dependencies']),'candidate_documents':2,'target_code_executed':False,'model_calls':0,'semantic_verification_generalized':False}))
