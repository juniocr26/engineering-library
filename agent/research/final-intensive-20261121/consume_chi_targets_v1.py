import argparse,json,hashlib,re,subprocess
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True,type=Path);root=ap.parse_args().root.resolve();p=root/'agent/research/final-intensive-20261121';sha=lambda b:hashlib.sha256(b).hexdigest();source=p/'chi-targets-source-context-v1';count=0
for topic in ['chi-middleware','chi-throttle-workflow']:
 d=json.loads((p/(topic+'-complete-review-v1.json')).read_text())
 for e in d['external_dependency_edges']:assert sha((root/e['path']).read_bytes())==e['sha256']
 for e in d['exact_source_range_bindings']:
  raw=(source/e['path']).read_bytes();assert sha(raw)==e['source_sha256'];assert sha(b''.join(raw.splitlines(keepends=True)[e['lines'][0]-1:e['lines'][1]]))==e['quote_sha256'];count+=1
 texts=[]
 for e in d['documents']:
  raw=(root/e['path']).read_bytes();assert sha(raw)==e['sha256'];assert (root/e['readable_original_path']).read_bytes()==raw;texts.append(raw.decode());assert (root/e['readable_original_path']).parent.joinpath('source-excerpts.json').is_file()
 ids=lambda t:re.findall(r'<!-- reading-section: faq:([^ ]+) -->',t);codes=lambda t:re.findall(r'(?<!`)`([^`\n]+)`(?!`)',t);assert ids(texts[0])==ids(texts[1])==d['FAQ_ids'];assert codes(texts[0])==codes(texts[1]);assert not d['chi_typecheck_build_tests_or_HTTP_server_executed']
for name,n in [('chi-timeout',1),('chi-recoverer',5),('chi-throttle-workflow',5)]:
 b=root/'agent/research/acceptance-calibration-20261121/original-public-chapter-provenance-captures-v1'/name;o=json.loads((b/'origin.json').read_text());raw=(b/'raw-response.json').read_bytes();assert sha(raw)==o['original_response_sha256'];facts=json.loads(json.loads(raw)['message']['content'])['facts'];assert len(facts)==n
 if name=='chi-recoverer':assert 'handled before the next function' in facts[1]['en']
 if name=='chi-throttle-workflow':assert any('backlogLimit to be positive' in x['en'] for x in facts)
guard=json.loads((root/'agent/research/continuation-20261119/defer-guard-candidate.json').read_text());assert guard['status']=='REJECTED_FALSE_POSITIVE' and guard['candidate_matches_both']
obs=json.loads((p/'chi-target-test-and-language-observations-v1.json').read_text());assert len(obs['header_derivations'])==8 and all(r['matches'] for r in obs['header_derivations']) and not obs['upstream_tests_executed']
s=json.loads((p/'chi-targets-syntax-observations-v1.json').read_text());parser=Path(s['parser_path']);assert sha(parser.read_bytes())==s['parser_sha256']
for e in s['target_files']:
 r=subprocess.run([str(parser),'-e'],input=(root/e['path']).read_bytes(),capture_output=True,timeout=20);assert r.returncode==0 and not r.stderr
r=subprocess.run([str(parser),'-e'],input=(root/s['owned_negative']['path']).read_bytes(),capture_output=True,timeout=20);assert r.returncode!=0 and r.stderr
print(json.dumps({'status':'PASS_CHI_ORIGINAL_TARGET_EXACT_RECOVERY','documents':4,'source_ranges':count,'historical_responses':3,'syntax_files':6,'owned_negative_refused':1,'chi_build_tests_or_HTTPserver_executed':False,'general_semantic_verification':False,'new_model_calls':0}))
