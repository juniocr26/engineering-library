import argparse,json,hashlib,re,subprocess
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);a=ap.parse_args();root=a.root.resolve();p=root/'agent/research/final-intensive-20261121';sha=lambda b:hashlib.sha256(b).hexdigest();reviews=[json.loads((p/n).read_text()) for n in ['redis-expiry-original-target-review-v1.json','redis-expiry-corrected-complete-review-v1.json','redis-ttl-complete-review-v1.json']];protocol=json.loads((p/'redis-c-raw-token-protocol-v1.json').read_text());lex=json.loads((p/'redis-c-raw-token-results-v1.json').read_text());source=p/'redis-targets-source-context-v1'
assert sha(Path('/usr/bin/clang').read_bytes())==protocol['compiler_launcher_sha256'];r=subprocess.run(protocol['command'],cwd=root,capture_output=True,timeout=30);assert r.returncode==lex['exit_code']==0;assert sha(r.stdout)==lex['stdout_sha256'] and sha(r.stderr)==lex['stderr_sha256'];assert len(r.stderr.decode().splitlines())==lex['raw_token_lines']
for review in reviews:
 for e in review['external_dependency_edges']:assert sha((root/e['path']).read_bytes())==e['sha256']
 for e in review['exact_source_range_bindings']:
  b=(source/e['path']).read_bytes();assert sha(b''.join(b.splitlines(keepends=True)[e['lines'][0]-1:e['lines'][1]]))==e['quote_sha256']
 w=review['historical_witness']
 for key in ['request','raw_response','origin']:assert sha((root/w[key]['path']).read_bytes())==w[key]['sha256']
 response=json.loads((root/w['raw_response']['path']).read_text());assert json.loads(response['message']['content'])['facts']==w['facts'];q=json.loads((root/w['request']['path']).read_text());m=q['messages'][-1]['content'];assert json.loads(m.split('BEGIN SOURCE JSON\n',1)[1].split('\nEND SOURCE JSON',1)[0])==w['selected_evidence']
 docs=[(root/d['path']).read_text() for d in review['documents']];spans=lambda t:re.findall(r'(?<!`)`([^`\n]+)`(?!`)',t);ids=lambda t:re.findall(r'<!-- reading-section: faq:([^ ]+) -->',t);assert spans(docs[0])==spans(docs[1]);assert ids(docs[0])==ids(docs[1])==review['FAQ_ids']
 for e in review['logical_original_document_links']:
  f=root/e['document'];target=f.parent/e['relative_link'];assert str(target.relative_to(root))==e['target']['path'] and sha(target.read_bytes())==e['target']['sha256']
assert reviews[0]['technical_status']=='FAIL_HISTORICAL_ATTRIBUTION' and reviews[0]['gates']['G2']['status']=='FAIL';assert 'supports the idea' in reviews[0]['historical_witness']['facts'][0]['en'];assert 'did not explicitly claim' in (root/reviews[1]['documents'][0]['path']).read_text();assert '500 seconds' in reviews[2]['historical_witness']['facts'][0]['en']
for d in reviews[2]['documents']:
 rows=re.findall(r'^\| (ttlCommand|pttlCommand|expiretimeCommand|pexpiretimeCommand) \| ([01]) \| ([01]) \|',(root/d['path']).read_text(),re.M);assert rows==[('ttlCommand','0','0'),('pttlCommand','1','0'),('expiretimeCommand','0','1'),('pexpiretimeCommand','1','1')]
print(json.dumps({'status':'PASS_EXACT_REDIS_TARGETS_AND_PRESERVED_ATTRIBUTION_FAILURE_RECOVERY','chapter_versions':3,'documents':6,'unique_historical_responses':2,'source_range_bindings_by_positive_target':[len(x['exact_source_range_bindings']) for x in reviews[1:]],'raw_lexer_lines':lex['raw_token_lines'],'parser_profile':'Rawtokensonly,notAST/typecheck/build','original_target_failure_preserved':True,'target_server_or_source_execution':False,'new_model_calls':0,'general_semantic_verification':False,'scope':'Samehost exact source/token/document/witness replay, not Redis command/replication/clock or portable compiler recovery.'}))
