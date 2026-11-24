"""Replay frozen reference-source comparisons/intake, never run shellwords or shell commands."""
from pathlib import Path
import argparse,json,subprocess,sys,hashlib
parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args();ROOT=args.root.resolve();P=ROOT/'agent/research/final-intensive-20261121';folder=P/'go-shellwords-version-source-comparison-v3';count=0
for tag in ['before','after']:
 for n in [1,2]:
  stem=tag+'-'+str(n);raw=(folder/(stem+'-request.json')).read_bytes();run=subprocess.run([sys.executable,'-B',str(ROOT/'agent/tools/go_source_ast.py')],input=raw,capture_output=True,timeout=25);assert run.returncode==0;assert json.loads(run.stdout)==json.loads((folder/(stem+'-response.json')).read_text());count+=1
intake=P/'go-shellwords-v1.0.13-frozen-type-intake-v1';protocol=json.loads((intake/'protocol.json').read_text());binary=P/'offline-go-type-observer-v2/observer';assert hashlib.sha256(binary.read_bytes()).hexdigest()==protocol['observer_sha256'];request=json.loads((intake/'request.json').read_text());request['export_root']=str(ROOT);run=subprocess.run([str(binary)],input=json.dumps(request).encode(),capture_output=True,timeout=25);assert run.returncode==0;assert json.loads(run.stdout)==json.loads((intake/'result.json').read_text())['packet']
print(json.dumps({'source_comparison_packets_replayed':count,'selected_callables':8,'correlated_version_pairs':1,'separate_new_version_subset_type_packet_replayed':True,'raw_upstream_git_blob_identity':'UNVERIFIED','complete_doc_acceptance':False,'target_source_executed':False,'model_calls':0}))
