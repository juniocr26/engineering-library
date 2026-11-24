import argparse,json,hashlib,subprocess,re
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);a=ap.parse_args();root=a.root.resolve();p=root/'agent/research/final-intensive-20261121';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();m=json.loads((p/'go-image-configuration-recovery-manifest-v1.json').read_text());r=json.loads((p/m['review']).read_text())
for edge in m['external_edges']:assert sha(root/edge['path'])==edge['sha256']
for edge in m['source_files']:assert sha(root/edge['saved_path'])==edge['sha256']
for edge in m['documents']:assert sha(root/edge['path'])==edge['sha256']
for w in r['witnesses']:
 assert sha(root/w['request_path'])==w['request_sha256'];assert sha(root/w['response_path'])==w['response_sha256'];assert json.loads(json.loads((root/w['response_path']).read_text())['message']['content'])['facts']==w['facts']
caller=next(w for w in r['witnesses'] if w['id'].endswith('-caller'));helper=next(w for w in r['witnesses'] if w['id'].endswith('-helpers'));assert 'with the loaded port number and an error if validation fails' in caller['facts'][0]['en'];assert helper['facts'][2]==helper['facts'][3]==helper['facts'][4]
obs=json.loads((p/m['static_observation_receipt']).read_text())
for edge in obs['sdk_contract_sources']:assert sha(root/edge['saved_path'])==edge['sha256']
for row in obs['commands']:
 original=Path(row['command'][-1]);parts=original.parts;ix=parts.index('go-image-configuration-source-context-v1');f=p.joinpath(*parts[ix:]);assert sha(f)==row['source_sha256'];result=subprocess.run([row['command'][0],'-e','-d',str(f)],capture_output=True,timeout=20);assert result.returncode==row['exit_code']==0
 # The actual archived observations are empty, so no root-sensitive diff is normalized away.
 assert (root/row['stdout_path']).read_bytes()==result.stdout==b'';assert (root/row['stderr_path']).read_bytes()==result.stderr==b''
spans=lambda text:re.findall(r'(?<!`)`([^`\n]+)`(?!`)',text);assert spans((root/m['documents'][0]['path']).read_text())==spans((root/m['documents'][1]['path']).read_text())
print(json.dumps({'status':'PASS_EXACT_ORIGINAL_CONFIG_TARGET_RECOVERY','documents':2,'source_files':len(m['source_files']),'historical_responses':2,'Go_syntax_replays':len(obs['commands']),'sdk_contract_snapshots':len(obs['sdk_contract_sources']),'application_or_tests_executed':False,'new_model_calls':0,'semantic_verifier':False}))
