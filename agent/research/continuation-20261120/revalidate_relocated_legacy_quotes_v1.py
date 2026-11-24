"""Read-only review of sealed legacy evidence; never a HelperRetrieval duplicate."""
import copy,datetime,hashlib,importlib.util,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'agent/tools'))
import documentation_retrieval as current
from documentation_workspace import directory,read,same_root
assert current.VERSION=='0.1.4'
cut=json.loads((P/'recovery-delta-receipt-v3.json').read_text());root=Path(cut['restored_root']);rp=root/'agent/research/continuation-20261120';manifest_path=ROOT/cut['input_manifest']['path'];raw=manifest_path.read_bytes();assert hashlib.sha256(raw).hexdigest()==cut['input_manifest']['sha256'];expected=json.loads(raw)['effective_expected_files']

def sealed(relative):
 path=root/relative;raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==expected[relative]['sha256'],relative
 return raw

registry_relative='agent/research/continuation-20261120/helper-public-registry-v1.json';registry_bytes=sealed(registry_relative);registry=current.strict_json(registry_bytes);original_registry_sha=current.sha(current.canonical(registry));relocated=copy.deepcopy(registry)
for source in relocated.values():source['root']=str(root/Path(source['root']).relative_to(ROOT))
old_tool_relative='agent/tools/documentation_retrieval.py';old_tool_bytes=sealed(old_tool_relative);assert current.sha(old_tool_bytes)!=current.LOADED_IMPLEMENTATION_SHA256
old_path=root/old_tool_relative;spec=importlib.util.spec_from_file_location('sealed_legacy_helper_validator_013',old_path);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old);assert old.VERSION=='0.1.3'
assert current.sha((root/'agent/tools/documentation_workspace.py').read_bytes())==current.LOADED_WORKSPACE_SHA256
current_identity=current.extractor_identity('python');rows=[];total_bytes=0
journal_relative='agent/research/continuation-20261120/helper-journal-public-v1';journal=root/journal_relative
keys=['facade-compile','facade-search','parser-cache','parser-errors']
with directory(str(journal))as journal_fd:
 for key in keys:
  raw_records={suffix:sealed(journal_relative+'/'+key+suffix)for suffix in ['.request.json','.result.json','.receipt.json']}
  for suffix,value in raw_records.items():assert read(journal_fd,key+suffix,16384)[0]==value
  request=current.strict_json(raw_records['.request.json']);cached=current.strict_json(raw_records['.result.json']);receipt=current.strict_json(raw_records['.receipt.json']);identity=cached['extractor_identity']
  assert identity['implementation_sha256']==expected[old_tool_relative]['sha256']and identity['workspace_sha256']==expected['agent/tools/documentation_workspace.py']['sha256']
  entry=relocated[request['source_id']];file_entry=entry['files'][request['path']];assert file_entry['language']=='python'and request['qualified_symbol']in file_entry['selectors']and request['revision']==entry['revision']and request['expected_sha256']==file_entry['sha256']
  with directory(entry['root'])as source_fd:
   source,metadata=read(source_fd,request['path'],65536);assert metadata['sha256']==request['expected_sha256']
   assert receipt==old.receipt_for(raw_records['.result.json'],old.canonical(request),original_registry_sha,metadata['sha256'],identity)
   old.validate_cached(cached,request,old.canonical(request),original_registry_sha,source,identity)
   # Current0.1.4 independently checks complete lexical ownership and metadata.
   current.validate_unit(cached['evidence'],source,request['qualified_symbol'],'python')
   assert read(source_fd,request['path'],65536)[0]==source and same_root(entry['root'],source_fd)
  for suffix,value in raw_records.items():assert read(journal_fd,key+suffix,16384)[0]==value
  total_bytes+=cached['quote_bytes']
  rows.append({'request_id':key,'status':'SEALED_LEGACY_QUOTE_REVALIDATED_FOR_REVIEW','original_result_sha256':current.sha(raw_records['.result.json']),'original_receipt_sha256':current.sha(raw_records['.receipt.json']),'original_registry_sha256':original_registry_sha,'original_extractor_identity':identity,'relocated_source_root':entry['root'],'path':request['path'],'revision':request['revision'],'source_sha256':metadata['sha256'],'complete_lexical_unit_revalidated_by_current_tool':True,'current_extractor_identity':current_identity,'evidence':cached['evidence'],'source_executed':False,'owner_approved':False,'training_gold':False,'automatic_helper_duplicate':False,'automatic_generation_context_injection':False,'budget_refund_allowed':False})
 assert same_root(str(journal),journal_fd)
assert total_bytes==1603 and len(rows)==4
assert current.extractor_identity('python')==current_identity
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':rows,'sealed_manifest_sha256':cut['input_manifest']['sha256'],'relocated_registry_sha256':current.sha(current.canonical(relocated)),'original_step_consumption_preserved':4,'original_quote_byte_consumption_preserved':total_bytes,'automatic_retry_or_context_injection':False,'old_journals_or_receipts_rewritten':False,'new_job_budget_created':False,'new_registered_tool_duplicate_status':False,'public_source_executed':False,'trusted_owned_validation_tools_executed':True,'current_validator_version':current.VERSION,'archived_validator_version':old.VERSION,'new_distinct_evaluation_cases':0,'model_calls':0,'training_steps':0,'owner_approved':False,'limitations':['Read-only review projection, not an existing HelperRetrieval response or automatic cache migration.','Operator-frozen source registry/recovery manifest are trust anchors; no new upstream Git authentication is claimed.','Original runtime identities remain recorded; the current lexical validator is a distinct producer.','Budget use is preserved, not refunded; no autonomous model tool routing or publication.']}
with(P/'relocated-legacy-quote-review-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'reviewed_legacy_units':len(rows),'old_version':old.VERSION,'current_version':current.VERSION,'prior_steps_preserved':4,'prior_bytes_preserved':total_bytes,'automatic_injection':False})
