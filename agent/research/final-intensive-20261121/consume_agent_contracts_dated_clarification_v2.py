import argparse,json,hashlib,re,tarfile
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True,type=Path);root=ap.parse_args().root.resolve();p=root/'agent/research/final-intensive-20261121'
sha=lambda b:hashlib.sha256(b).hexdigest()
def read(s):
 f=root/s
 assert f.is_file() and not f.is_symlink()
 assert f.resolve().is_relative_to(root)
 return f.read_bytes()
def data(s):return json.loads(read(s))
deps=data('agent/research/final-intensive-20261121/remaining-chapters-recovery-dependencies-v35.json')
for e in deps['dependencies']:assert sha(read(e['path']))==e['sha256']
construction=json.loads((p/'agent-contracts-dated-clarification-construction-v1.json').read_bytes());docs=0;links=0
for row in construction['records']:
 name=row['language'];original=(p/'agent-contracts-current-chapter-snapshot-v1'/name).read_bytes();candidate=(p/'agent-contracts-dated-reviewed-candidate-v1'/name).read_bytes()
 assert sha(original)==row['original_sha256'] and sha(candidate)==row['candidate_sha256']
 text=candidate.decode();restored=text.replace('\n'+row['scope_note'],'',1)
 for link in row['relative_links']:
  target=(p/'agent-contracts-dated-reviewed-candidate-v1'/link['after']).resolve();assert target.is_relative_to(root) and target.is_file() and sha(target.read_bytes())==link['sha256']
  restored=restored.replace(']('+link['after']+')',']('+link['before']+')');links+=1
 assert restored.encode()==original
 ids=lambda t:re.findall(r'<!-- reading-section: faq:([^ ]+) -->',t)
 assert ids(text)==ids(original.decode())==['research-not-training','human-content-boundary','helper-not-autonomous-mcp'];docs+=1
packet=json.loads((p/'agent-contracts-current-chapter-snapshot-v1/source-excerpts.json').read_bytes());spans=0
for e in packet['historical_frozen_excerpt_checks']:
 raw=read(e['source_file']);assert sha(raw)==e['full_file_sha256'];quote=b''.join(raw.splitlines(keepends=True)[e['first_line']-1:e['last_line']]);assert quote.decode()==e['quote'] and sha(quote)==e['quote_sha256'];spans+=1
recovery=json.loads((p/'agent-contracts-dated-source-recovery-v1.json').read_bytes());archive=root/recovery['source_archive']['path'];assert sha(archive.read_bytes())==recovery['source_archive']['sha256']
with tarfile.open(archive,'r:gz') as tf:
 members=tf.getmembers()
 for e in recovery['records']:
  matches=[m for m in members if m.name==e['archive_member']];assert len(matches)==1 and matches[0].isfile()
  content=tf.extractfile(matches[0]).read();assert sha(content)==e['expected_sha256'] and content==read(e['saved_path'])
logs=json.loads((p/'agent-contracts-historical-test-log-correspondence-v1.json').read_bytes())
for e in logs['observations']:
 raw=read(e['log']);assert sha(raw)==e['log_sha256'];m=re.search(rb'Ran (\d+) tests? in ([\d.]+)s',raw);assert m and int(m[1])==e['tests'] and b'\nOK' in raw
rows=[json.loads(x) for x in read('.local-backups/continuation-20261119/agent-project-chapter-progress.jsonl').splitlines()]
accepted=[x for x in rows if x.get('status')=='generated-unreviewed' and x.get('exit')==0];refused=[x for x in rows if x.get('status')=='rejected' and x.get('exit')==1]
assert len(accepted)==9 and len(refused)==3
extra=json.loads((p/'agent-contracts-dated-clarification-construction-v2.json').read_bytes())
for row in extra['records']:
 name=row['language'];before=(p/'agent-contracts-dated-reviewed-candidate-v1'/name).read_bytes();after=(p/'agent-contracts-dated-reviewed-candidate-v2'/name).read_bytes()
 assert sha(before)==row['before_sha256'] and sha(after)==row['candidate_sha256']
 assert after.decode().count(row['after'])==1 and after.decode().replace(row['after'],row['before']).encode()==before
 assert ids(after.decode())==['research-not-training','human-content-boundary','helper-not-autonomous-mcp']
extra_deps=json.loads((p/'remaining-chapters-recovery-dependencies-v36.json').read_bytes())
for edge in extra_deps['dependencies']:assert sha(read(edge['path']))==edge['sha256']
closure=json.loads((p/'agent-contracts-additional-source-receipt-closure-v1.json').read_bytes())
for edge in closure['external_dependency_edges']:assert sha(read(edge['path']))==edge['sha256']
for row in json.loads((p/'agent-contracts-additional-historical-log-correspondence-v1.json').read_bytes())['records']:
 raw=read(row['path']);assert sha(raw)==row['sha256'];m=re.search(rb'Ran (\d+) tests? in ([\d.]+)s',raw);assert m and int(m[1])==row['tests'] and b'\nOK' in raw
r=data('agent/research/documentation-intelligence-20261119/revision-signals-current-evaluation.json');assert len({x['path'] for x in r['results']})==2 and sum(len(x['result']['observations']['observations']) for x in r['results'])==5
review=json.loads((p/'agent-contracts-dated-complete-review-v1.json').read_bytes());assert len(review['claim_group_reviews'])==37 and len(review['challenge_pass'])==8 and all(g['status']=='PASS' for g in review['gates'].values()) and review['G9']['status']=='PENDING'
for doc in review['documents']:assert sha(read(doc['path']))==doc['sha256']
for group in review['claim_group_reviews']:assert sha((p/group['supporting_observation']).read_bytes())==group['supporting_observation_sha256']
print(json.dumps({'status':'PASS_INTERNAL_DATED_CHAPTER_V2_EXACT_RECOVERY','candidate_documents':2,'preserved_original_and_v1_documents':4,'relocated_links':links,'historical_source_cards':spans,'dated_optional_sources_from_archive':len(recovery['records']),'historical_logs':8,'declared_dependency_hashes':len(extra_deps['dependencies']),'manual_composite_groups_bound':37,'human_independent_approval':False,'whole_chapter_semantic_approval_from_this_consumer':False,'new_model_calls':0,'new_old_test_executions':0,'publication_authorized':False,'training_gold':False}))
