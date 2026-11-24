import argparse,json,hashlib,re,subprocess,os
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);a=ap.parse_args();root=a.root.resolve();p=root/'agent/research/final-intensive-20261121';sha=lambda b:hashlib.sha256(b).hexdigest();review=json.loads((p/'rails-request-complete-review-v1.json').read_text());observation=json.loads((p/'rails-request-static-observations-v1.json').read_text());source=p/'rails-request-source-context-v1/request.rb'
for e in review['external_dependency_edges']:assert sha((root/e['path']).read_bytes())==e['sha256']
for e in json.loads((p/'rails-request-source-acquisition-v1.json').read_text())['records']:assert sha((root/e['saved_path']).read_bytes())==e['sha256']
assert sha(Path('/usr/bin/ruby').read_bytes())==observation['ruby_executable_sha256'];assert sha((p/'observe_rails_request_ripper_v1.rb').read_bytes())==observation['observer_sha256'];r=subprocess.run(['/usr/bin/ruby','--disable-gems',str(p/'observe_rails_request_ripper_v1.rb'),str(source)],capture_output=True,timeout=30,env={**os.environ,'RUBYOPT':''});assert r.returncode==observation['exit_code']==0;expected=json.loads((p/'rails-request-ripper-stdout-v1.json').read_text());packet=json.loads(r.stdout);assert packet==expected and packet['status']=='PARSED_FULL_FILE_SELECTED_METHODS';assert not packet['target_source_loaded_or_executed']
raw=source.read_bytes();lines=raw.decode().splitlines(keepends=True)
for e in review['exact_source_range_bindings']:assert sha(''.join(lines[e['lines'][0]-1:e['lines'][1]]).encode())==e['quote_sha256']
def const_name(n):
 if isinstance(n,list):
  if n and n[0]=='@const':return n[1]
  if n and n[0] in ['const_ref','var_ref','top_const_ref']:return const_name(n[1])
  if n and n[0]=='const_path_ref':return const_name(n[1])+'::'+const_name(n[2])
 raise ValueError('Unsupported lexical constant node')
owned=[]
def walk(n,scopes):
 if not isinstance(n,list) or not n:return
 kind=n[0] if isinstance(n[0],str) else None
 if kind=='module':walk(n[2],scopes+[const_name(n[1])]);return
 if kind=='class':walk(n[3],scopes+[const_name(n[1])]);return
 if kind=='def' and n[1][1] in packet['selected_method_nodes']:owned.append({'name':n[1][1],'lexical_scopes':scopes,'declaration_line':n[1][2][0],'node_sha256':sha(json.dumps(n,separators=(',',':')).encode())})
 for c in n:
  if isinstance(c,list):walk(c,scopes)
walk(packet['full_file_sexp'],[]);assert owned==review['lexical_owner_records'];assert all(e['lexical_scopes']==['ActionDispatch','Request'] for e in owned)
for w in review['historical_witnesses']:
 for key in ['request','raw_response']:assert sha((root/w[key]['path']).read_bytes())==w[key]['sha256']
 r=json.loads((root/w['raw_response']['path']).read_text());assert json.loads(r['message']['content'])['facts']==w['facts'];q=json.loads((root/w['request']['path']).read_text());m=q['messages'][-1]['content'];assert json.loads(m.split('BEGIN SOURCE JSON\n',1)[1].split('\nEND SOURCE JSON',1)[0])==w['selected_evidence']
docs=[(root/d['path']).read_text() for d in review['documents']];spans=lambda t:re.findall(r'(?<!`)`([^`\n]+)`(?!`)',t);ids=lambda t:re.findall(r'<!-- reading-section: faq:([^ ]+) -->',t);assert spans(docs[0])==spans(docs[1]);assert ids(docs[0])==ids(docs[1])==review['FAQ_ids']
for e in review['logical_original_document_links']:
 f=root/e['document'];target=f.parent/e['relative_link'];assert str(target.relative_to(root))==e['target']['path'] and sha(target.read_bytes())==e['target']['sha256']
assert not review['runtime_method_bindings_verified'] and not review['framework_runtime_compatibility_verified']
print(json.dumps({'status':'PASS_EXACT_RAILS_REQUEST_ORIGINAL_TARGET_RECOVERY','documents':2,'whole_public_source_parsed':True,'source_ranges':len(review['exact_source_range_bindings']),'lexical_methods':len(owned),'historical_responses':len(review['historical_witnesses']),'logical_links':len(review['logical_original_document_links']),'target_source_or_gemspec_execution':False,'new_model_calls':0,'framework_runtime_compatibility':False,'general_semantic_verification':False,'scope':'Samehost exactRuby2.6/Ripper/source/AST/document replay; not actionpack runtime or clean-machine restore.'}))
