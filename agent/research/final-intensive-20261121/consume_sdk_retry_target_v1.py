import argparse,json,hashlib,re,subprocess
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True,type=Path);root=ap.parse_args().root.resolve();p=root/'agent/research/final-intensive-20261121';sha=lambda b:hashlib.sha256(b).hexdigest();d=json.loads((p/'sdk-retry-corrected-complete-review-v1.json').read_text());source=p/'sdk-retry-target-source-context-v1'
for e in d['external_dependency_edges']:assert sha((root/e['path']).read_bytes())==e['sha256']
for e in d['exact_source_range_bindings']:
 raw=(source/e['path']).read_bytes();assert sha(raw)==e['source_sha256'];assert sha(b''.join(raw.splitlines(keepends=True)[e['lines'][0]-1:e['lines'][1]]))==e['quote_sha256']
texts=[]
for e in d['documents']:
 raw=(root/e['path']).read_bytes();assert sha(raw)==e['sha256'];texts.append(raw.decode())
ids=lambda t:re.findall(r'<!-- reading-section: faq:([^ ]+) -->',t);codes=lambda t:re.findall(r'(?<!`)`([^`\n]+)`(?!`)',t);assert ids(texts[0])==ids(texts[1])==d['FAQ_ids'];assert codes(texts[0])==codes(texts[1])
for e in d['logical_document_links']:
 target=((root/e['document']).parent/e['relative_link']).resolve();assert target==root/e['target'] and sha(target.read_bytes())==e['sha256']
original=json.loads((p/'sdk-retry-original-target-review-v1.json').read_text());assert original['gates']['G2']['status']=='FAIL'
for e in original['documents']:assert sha((root/e['path']).read_bytes())==e['sha256']
obs=json.loads((p/'sdk-retry-binding-census-observations-v2.json').read_text());assert len(obs['census_dependencies'])==207
for e in obs['census_dependencies']:assert sha((root/e['path']).read_bytes())==e['sha256']
assert len({(v['profile']['goos'],v['profile']['goarch']) for v in obs['profiles'].values()})==2
for name in ['sdk-retry-function','sdk-retry-with-constants','sdk-contiguous-contract']:
 b=root/'agent/research/acceptance-calibration-20261121/original-public-chapter-provenance-captures-v1'/name;o=json.loads((b/'origin.json').read_text());raw=(b/'raw-response.json').read_bytes();assert sha(raw)==o['original_response_sha256'];facts=json.loads(json.loads(raw)['message']['content'])['facts'];assert len(facts)==1
s=json.loads((p/'sdk-retry-target-syntax-observations-v1.json').read_text());parser=Path(s['parser_path']);assert sha(parser.read_bytes())==s['parser_sha256']
for e in s['target_files']:
 r=subprocess.run([str(parser),'-e'],input=(root/e['path']).read_bytes(),capture_output=True,timeout=20);assert r.returncode==0 and not r.stderr
r=subprocess.run([str(parser),'-e'],input=(root/s['owned_negative']['path']).read_bytes(),capture_output=True,timeout=20);assert r.returncode!=0 and r.stderr
assert not d['SDK_typecheck_build_tests_or_service_executed'] and not d['historical_binding_experiment_rerun']
print(json.dumps({'status':'PASS_SDK_RETRY_COMPLETE_CORRECTION_EXACT_RECOVERY','candidate_documents':2,'failed_original_documents':2,'source_ranges':2,'census_files':207,'historic_profiles':2,'historical_responses':3,'local_links':6,'Go_syntax_files':5,'owned_negative_refused':1,'SDK_build_tests_or_service_executed':False,'general_semantic_verification':False}))
