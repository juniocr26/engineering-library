import argparse,json,hashlib,re,subprocess,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);a=ap.parse_args();root=a.root.resolve();p=root/'agent/research/final-intensive-20261121';sha=lambda b:hashlib.sha256(b).hexdigest();review=json.loads((p/'go-image-quality-complete-review-v1.json').read_text());protocol=json.loads((p/'go-image-quality-target-protocol-v1.json').read_text());static=json.loads((p/'go-image-quality-static-observations-v1.json').read_text())
for e in review['external_dependency_edges']:assert sha((root/e['path']).read_bytes())==e['sha256']
source=root/protocol['source']['path'];raw=source.read_bytes();assert sha(raw)==protocol['source']['sha256'];lines=raw.decode().splitlines()
for e in review['exact_source_range_bindings']:assert sha(('\n'.join(lines[e['lines'][0]-1:e['lines'][1]])).encode())==e['quote_sha256']
for record in static['records']:
 req=p/'go-image-quality-parser-observations-v1'/f"batch-{record['batch']}.request.json";r=subprocess.run([sys.executable,'-B',str(root/'agent/tools/go_source_ast.py')],input=req.read_bytes(),capture_output=True,timeout=30);assert r.returncode==record['exit_code']==0;packet=json.loads(r.stdout);assert packet==record['packet'];assert packet['source_executed'] is False and packet['syntax_only'] is True
for w in review['historical_witnesses']:
 for key in ['request','raw_response']:assert sha((root/w[key]['path']).read_bytes())==w[key]['sha256']
 r=json.loads((root/w['raw_response']['path']).read_text());assert json.loads(r['message']['content'])['facts']==w['facts'];q=json.loads((root/w['request']['path']).read_text());m=q['messages'][-1]['content'];e=json.loads(m.split('BEGIN SOURCE JSON\n',1)[1].split('\nEND SOURCE JSON',1)[0]);assert e==w['selected_evidence'];assert not any('DefaultJPEGQuality =' in x['quote'] for x in e.values())
docs=[(root/d['path']).read_text() for d in review['documents']];spans=lambda t:re.findall(r'(?<!`)`([^`\n]+)`(?!`)',t);ids=lambda t:re.findall(r'<!-- reading-section: faq:([^ ]+) -->',t);assert spans(docs[0])==spans(docs[1]);assert ids(docs[0])==ids(docs[1])==review['FAQ_ids']
for t in docs:
 rows=[[int(x.strip()) for x in l.strip('|').split('|')] for l in t.splitlines() if re.match(r'^\| -?\d+ \|',l)];assert rows==review['static_table_rows']
for e in review['logical_original_document_links']:
 f=root/e['document'];assert sha((f.parent/e['relative_link']).read_bytes())==e['target']['sha256']
print(json.dumps({'status':'PASS_EXACT_GO_IMAGE_QUALITY_ORIGINAL_TARGET_RECOVERY','documents':2,'source_ranges':len(review['exact_source_range_bindings']),'current_parser_batches':len(static['records']),'historical_responses':len(review['historical_witnesses']),'bilingual_static_table_rows':len(review['static_table_rows']),'target_source_execution':False,'new_model_calls':0,'general_semantic_verification':False}))
