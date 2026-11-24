import argparse,json,hashlib,re,subprocess
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True,type=Path);root=ap.parse_args().root.resolve();p=root/'agent/research/final-intensive-20261121';sha=lambda b:hashlib.sha256(b).hexdigest();source=p/'prometheus-targets-source-context-v1';count=0
for name in ['prometheus-builder-complete-review-v1.json','prometheus-keep-corrected-complete-review-v1.json']:
 d=json.loads((p/name).read_text())
 for e in d['external_dependency_edges']:assert sha((root/e['path']).read_bytes())==e['sha256']
 for e in d['exact_source_range_bindings']:
  raw=(source/e['path']).read_bytes();assert sha(b''.join(raw.splitlines(keepends=True)[e['lines'][0]-1:e['lines'][1]]))==e['quote_sha256'];count+=1
 texts=[]
 for e in d['documents']:
  raw=(root/e['path']).read_bytes();assert sha(raw)==e['sha256'];texts.append(raw.decode())
  logical=root/e.get('readable_original_path',e['path']);assert (logical.parent/'source-excerpts.json').is_file()
 ids=lambda t:re.findall(r'<!-- reading-section: faq:([^ ]+) -->',t);codes=lambda t:re.findall(r'(?<!`)`([^`\n]+)`(?!`)',t);assert ids(texts[0])==ids(texts[1])==d['FAQ_ids'];assert codes(texts[0])==codes(texts[1]);assert not d['Prometheus_typecheck_build_or_execution']
original=json.loads((p/'prometheus-keep-original-target-review-v1.json').read_text());assert original['technical_status']=='FAIL_HISTORICAL_ATTRIBUTION' and original['gates']['G2']['status']=='FAIL'
for e in original['documents']:assert sha((root/e['path']).read_bytes())==e['sha256']
for change in original['changes']:
 before=(root/change['original']['path']).read_text();after=(root/change['candidate_path']).read_text();assert sha(after.encode())==change['candidate_sha256'];assert len([l for l in change['diff'].splitlines() if l.startswith('-') and not l.startswith('---')])==1
hist=json.loads((p/'prometheus-builder-historical-origins-v1.json').read_text());assert [r['writer_exit'] for r in hist['records']]==[1,0]
for r in hist['records']:
 for e in r['artifacts']:assert sha((root/e['path']).read_bytes())==e['sha256']
 assert all(f['evidence_id']=='S1' for f in r['facts'])
assert 'returns the updated Builder' in hist['records'][0]['facts'][0]['en'];assert 'return' not in hist['records'][1]['facts'][0]['en'].lower()
syntax=json.loads((p/'prometheus-targets-syntax-observations-v1.json').read_text());parser=Path(syntax['parser_path']);assert sha(parser.read_bytes())==syntax['parser_sha256']
for e in syntax['target_files']:
 r=subprocess.run([str(parser),'-e'],input=(root/e['path']).read_bytes(),capture_output=True,timeout=20);assert r.returncode==0 and not r.stderr
r=subprocess.run([str(parser),'-e'],input=(root/syntax['owned_negative']['path']).read_bytes(),capture_output=True,timeout=20);assert r.returncode!=0 and r.stderr
print(json.dumps({'status':'PASS_PROMETHEUS_TARGET_EXACT_RECOVERY','candidate_documents':4,'failed_original_documents_retained':2,'source_ranges':count,'historical_builder_responses':2,'syntax_files':4,'owned_negative_refused':1,'type_build_or_Prometheus_execution':False,'general_semantic_verification':False}))
