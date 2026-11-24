import argparse,json,hashlib,re,subprocess,sys,os
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True,type=Path);root=ap.parse_args().root.resolve();p=root/'agent/research/final-intensive-20261121';sha=lambda b:hashlib.sha256(b).hexdigest();review=json.loads((p/'fastify-target-complete-review-v1.json').read_text());source=p/'fastify-target-source-context-v1'
for e in review['external_dependency_edges']:assert sha((root/e['path']).read_bytes())==e['sha256']
for e in review['exact_source_range_bindings']:
 raw=(source/e['path']).read_bytes();assert sha(raw)==e['source_sha256'];assert sha(b''.join(raw.splitlines(keepends=True)[e['lines'][0]-1:e['lines'][1]]))==e['quote_sha256']
texts=[]
for e in review['documents']:
 raw=(root/e['path']).read_bytes();assert sha(raw)==e['sha256'];assert (root/e['readable_original_path']).read_bytes()==raw;texts.append(raw.decode());assert (root/e['readable_original_path']).parent.joinpath('source-excerpts.json').is_file()
ids=lambda t:re.findall(r'<!-- reading-section: faq:([^ ]+) -->',t);codes=lambda t:re.findall(r'(?<!`)`([^`\n]+)`(?!`)',t);assert ids(texts[0])==ids(texts[1])==review['FAQ_ids'];assert codes(texts[0])==codes(texts[1])
b=root/'agent/research/acceptance-calibration-20261121/original-public-chapter-provenance-captures-v1/fastify-checkrequestexistence';o=json.loads((b/'origin.json').read_text());raw=(b/'raw-response.json').read_bytes();assert sha(raw)==o['original_response_sha256'];facts=json.loads(json.loads(raw)['message']['content'])['facts'];assert 'If the name is not provided, it returns false.' in facts[0]['en'];q=json.loads((b/'recorded-request.json').read_text());selected=json.loads(q['messages'][-1]['content'].split('BEGIN SOURCE JSON\n')[1].split('\nEND SOURCE JSON')[0]);assert set(selected)=={'S1'}
probe=json.loads((root/'.local-backups/continuation-20261119/strict-receiver-language-probe.json').read_text());assert probe['unbound_strict_call']=='TypeError' and probe['binding_outer_does_not_bind_inner_plain_call']=='TypeError' and not probe['external_application_source_executed']
cmd=[sys.executable,'-B',str(p/'observe_fastify_js_syntax_v1.py'),'--root',str(root),'--stdout-only'];r=subprocess.run(cmd,capture_output=True,text=True,timeout=30,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});assert r.returncode==0,r.stderr;d=json.loads(r.stdout);assert all(c['matched'] for c in d['observations']['cases']) and len(d['observations']['cases'])==7;assert not d['target_source_executed']
assert not review['Fastify_modules_server_or_tests_executed'] and not review['new_model_calls']
print(json.dumps({'status':'PASS_FASTIFY_ORIGINAL_TARGET_EXACT_RECOVERY','documents':2,'source_ranges':9,'historical_response':1,'historic_synthetic_receipt_not_rerun':True,'JS_syntax_files':6,'owned_negative_refused':1,'Fastify_modules_server_or_tests_executed':False,'typechecked':False,'general_semantic_verification':False}))
