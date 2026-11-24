from pathlib import Path
import json,hashlib,datetime,re,collections
p=Path(__file__).resolve().parent;root=p.parents[2];sha=lambda b:hashlib.sha256(b).hexdigest();packet=json.loads((p/'agent-contracts-current-chapter-snapshot-v1/source-excerpts.json').read_text());rows=[];spans=[]
def observe(path,expected,role,logical=None):
 f=root/path;rec={'path':path,'expected_sha256':expected,'role':role,'exists':f.is_file(),'symlink':f.is_symlink()}
 if f.is_file() and not f.is_symlink():rec.update(actual_sha256=sha(f.read_bytes()),bytes=f.stat().st_size);rec['status']='MATCH' if rec['actual_sha256']==expected else 'DIFFERENT'
 else:rec['status']='MISSING_OR_SYMLINK'
 if logical:
  x=root/logical;rec['logical_current_path']=logical;rec['logical_current_sha256']=sha(x.read_bytes()) if x.is_file() and not x.is_symlink() else None;rec['logical_current_matches_historical']=rec['logical_current_sha256']==expected
 rows.append(rec)
for key in ['historical_source_files','current_source_files']:
 for e in packet[key]:observe(e['source_file'],e['full_file_sha256'],key,e['path'])
for e in packet['historical_frozen_excerpt_checks']:
 f=root/e['source_file'];raw=f.read_bytes();q=b''.join(raw.splitlines(keepends=True)[e['first_line']-1:e['last_line']]);spans.append({'section':e['section'],'evidence_id':e['evidence_id'],'path':e['source_file'],'lines':[e['first_line'],e['last_line']],'full_source_matches':sha(raw)==e['full_file_sha256'],'quote_matches':q.decode()==e['quote'] and sha(q)==e['quote_sha256']})
for e in packet['current_optional_tool_inventory']:observe(e['path'],e['sha256'],'original_chapter_current_optional_path')
for history in packet['optional_tool_inventory_history']:
 for e in history['files']:
  path=e.get('preserved_source_file')
  if path:observe(path,e['sha256'],'preserved_optional_history:'+history['preserved_at'],e['path'])
original=root/'agent/research/documentation-intelligence-20261119/chapters/documentation-agent-contracts';links=[]
for lang in ['en','pt-br']:
 for target in re.findall(r'\]\(([^)]+)\)',(p/'agent-contracts-current-chapter-snapshot-v1'/(lang+'.md')).read_text()):
  if target.startswith(('https://','http://')):continue
  f=(original/target).resolve();rec={'language':lang,'relative_link':target,'logical_target':str(f.relative_to(root)),'exists':f.is_file()}
  if f.is_file():rec.update(sha256=sha(f.read_bytes()),bytes=f.stat().st_size)
  links.append(rec)
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_identity_records':rows,'historical_exact_spans':spans,'logical_original_document_links':links,'identity_counts':dict(collections.Counter(r['status'] for r in rows)),'current_logical_matches':sum(r.get('logical_current_matches_historical',False) for r in rows),'historical_span_matches':sum(r['full_source_matches'] and r['quote_matches'] for r in spans),'historical_span_count':len(spans),'broken_logical_links':[r for r in links if not r['exists']],'technical_status':'INCONCLUSIVE_WHOLE_REVIEW_IN_PROGRESS','meaning':'Oldsourceidentity isseparatefromactualcurrentpathstate; MATCHdoesnotproveprose/sourceclaim semantics, DIFFERENTdoesnoterasehistoricalreceipt','new_model_calls':0,'files_modified':False}
with (p/'agent-contracts-source-identity-observations-v1.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({k:out[k] for k in ['identity_counts','historical_span_matches','historical_span_count']}));print('CURRENT_OPTIONAL_DIFFERENCES',[r['path'] for r in rows if r['role']=='original_chapter_current_optional_path' and r['status']!='MATCH']);print('BROKEN_LINKS',len(out['broken_logical_links']))
