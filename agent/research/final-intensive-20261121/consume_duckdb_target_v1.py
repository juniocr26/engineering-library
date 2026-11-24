import argparse,json,hashlib,re
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True,type=Path);root=ap.parse_args().root.resolve();p=root/'agent/research/final-intensive-20261121';sha=lambda b:hashlib.sha256(b).hexdigest();review=json.loads((p/'duckdb-target-complete-review-v1.json').read_text());source=p/'duckdb-target-source-context-v1'
for e in review['external_dependency_edges']:assert sha((root/e['path']).read_bytes())==e['sha256']
for e in review['exact_source_range_bindings']:
 raw=(source/e['path']).read_bytes();assert sha(raw)==e['source_sha256'];assert sha(b''.join(raw.splitlines(keepends=True)[e['lines'][0]-1:e['lines'][1]]))==e['quote_sha256']
texts=[]
for e in review['documents']:
 raw=(root/e['path']).read_bytes();assert sha(raw)==e['sha256'];assert (root/e['readable_original_path']).read_bytes()==raw;texts.append(raw.decode());assert (root/e['readable_original_path']).parent.joinpath('source-excerpts.json').is_file()
ids=lambda t:re.findall(r'<!-- reading-section: faq:([^ ]+) -->',t);codes=lambda t:re.findall(r'(?<!`)`([^`\n]+)`(?!`)',t);assert ids(texts[0])==ids(texts[1])==review['FAQ_ids'];assert codes(texts[0])==codes(texts[1]);assert all('| true | true | false |' in t and '| false | false | false |' in t for t in texts)
b=root/'agent/research/acceptance-calibration-20261121/original-public-chapter-provenance-captures-v1/duckdb-boolean-factory';origin=json.loads((b/'origin.json').read_text());raw=(b/'raw-response.json').read_bytes();assert sha(raw)==origin['original_response_sha256'];r=json.loads(raw);facts=json.loads(r['message']['content'])['facts'];assert len(facts)==5 and all(x==facts[1] for x in facts[1:]);assert 'constructor' in facts[0]['en'] and 'construtor' in facts[0]['pt-br'];q=json.loads((b/'recorded-request.json').read_text());evidence=json.loads(q['messages'][-1]['content'].split('BEGIN SOURCE JSON\n')[1].split('\nEND SOURCE JSON')[0]);assert set(evidence)=={'S1','S2'}
assert not review['DuckDB_parser_compiler_build_or_runtime_executed'] and not review['new_model_calls']
print(json.dumps({'status':'PASS_DUCKDB_ORIGINAL_TARGET_EXACT_RECOVERY','documents':2,'source_ranges':6,'historical_response':1,'historical_items':5,'unique_bilingual_fact_items':2,'conceptual_rows_not_runtime':2,'DuckDB_compilation_or_execution':False,'general_semantic_verification':False}))
