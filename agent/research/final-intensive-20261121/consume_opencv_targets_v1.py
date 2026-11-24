import argparse,json,hashlib,re
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True,type=Path);root=ap.parse_args().root.resolve();p=root/'agent/research/final-intensive-20261121';sha=lambda b:hashlib.sha256(b).hexdigest();source=p/'opencv-targets-source-context-v1';count=0
for topic in ['opencv-depth-coercion','opencv-shape-contract']:
 review=json.loads((p/(topic+'-complete-review-v1.json')).read_text())
 for e in review['external_dependency_edges']:assert sha((root/e['path']).read_bytes())==e['sha256']
 for e in review['exact_source_range_bindings']:
  raw=(source/e['path']).read_bytes();assert sha(raw)==e['source_sha256'];assert sha(b''.join(raw.splitlines(keepends=True)[e['lines'][0]-1:e['lines'][1]]))==e['quote_sha256'];count+=1
 texts=[(root/e['path']).read_text() for e in review['documents']]
 for e in review['documents']:assert sha((root/e['path']).read_bytes())==e['sha256'];assert (root/e['readable_original_path']).read_bytes()==(root/e['path']).read_bytes()
 ids=lambda t:re.findall(r'<!-- reading-section: faq:([^ ]+) -->',t);code=lambda t:re.findall(r'(?<!`)`([^`\n]+)`(?!`)',t);assert ids(texts[0])==ids(texts[1])==review['FAQ_ids'];assert code(texts[0])==code(texts[1]);assert not review['OpenCV_parser_compiler_build_or_runtime_executed'];assert not review['new_model_calls']
 for doc in review['documents']:
  original=root/doc['readable_original_path']
  for link in re.findall(r'\]\(([^)]+)\)',original.read_text()):assert (original.parent/link).is_file()
depth=p/'opencv-depth-historical-capture-v1';r=json.loads((depth/'record.json').read_text());raw=(depth/'raw-response.json').read_bytes();assert sha(raw)==r['trace'][1]['payload']['historical_original_body_sha256'];assert json.loads(raw)==r['result']['response'];assert json.loads((depth/'recorded-request.json').read_text())==r['result']['request'];assert json.loads(r['result']['response']['message']['content'])==r['result']['result'];assert 'maximum depth' in r['result']['result']['facts'][0]['en']
b=root/'agent/research/acceptance-calibration-20261121/original-public-chapter-provenance-captures-v1/opencv-shape-contract';r=json.loads((b/'raw-response.json').read_text());facts=json.loads(r['message']['content'])['facts'];assert 'transmissão' in facts[0]['pt-br'];assert 'right to left' in facts[0]['en']
print(json.dumps({'status':'PASS_OPENCV_EXACT_TARGET_RECOVERY','documents':4,'source_ranges':count,'historical_responses':2,'parser_compiler_or_OpenCV_execution':False,'general_semantic_verification':False,'new_model_calls':0}))
