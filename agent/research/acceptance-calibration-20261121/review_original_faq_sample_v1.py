"""Source-first, same-agent annotation of the frozen six-pair FAQ sample."""
import json, hashlib, datetime
from pathlib import Path
P=Path(__file__).resolve().parent
protocol=json.loads((P/'original-faq-semantic-sample-protocol-v1.json').read_text())
acquisition=json.loads((P/'original-faq-source-reacquisition-v1.json').read_text())
lines=Path(protocol['source_dataset']).read_text().splitlines()
def sha(b):return hashlib.sha256(b).hexdigest()
# Each tuple is one bounded source proposition, with a literal source witness.
specs={
'chi':[
('The recovered-panic branch obtains logEntry by a distinct GetLogEntry call.','middleware/recoverer.go','logEntry := GetLogEntry(r)'),
('For non-nil logEntry the selected call is logEntry.Panic.','middleware/recoverer.go','if logEntry != nil {'),
('The alternative selected call is PrintPrettyStack.','middleware/recoverer.go','PrintPrettyStack(rvr)')],
'duckdb':[
('Boolean payload is assigned to value_.boolean.','src/common/types/value.cpp','result.value_.boolean = value;'),
('The factory separately assigns a non-null flag, without a bool-value branch.','src/common/types/value.cpp','result.is_null = false;'),
('The returned object is the same local result after those assignments.','src/common/types/value.cpp','return result;')],
'ruff':[
('The resolver declares a PythonVersion result, not a returned Result error.','crates/ruff_workspace/src/settings.rs','pub fn resolve_target_version(&self, path: &Path) -> PythonVersion'),
('The matching iterator obtains the filename with expect, which may panic if absent.','crates/ruff_linter/src/settings/types.rs','path.file_name().expect("Unable to parse filename")'),
('An empty compiled list returns before iterator acquisition.','crates/ruff_linter/src/settings/types.rs','if self.0.is_empty() {'),
('The compiled-list constructor has its own Result contract.','crates/ruff_linter/src/settings/types.rs','pub fn resolve(per_file_versions: Vec<PerFileTargetVersion>) -> Result<Self>')],
'redis':[
('The getter returns the cached cmd_time_snapshot member.','src/server.c','return server.cmd_time_snapshot;'),
('The getter declares the mstime_t result type.','src/server.c','mstime_t commandTimeSnapshot(void)'),
('The source defines mstime_t as its millisecond time type.','src/server.h','typedef long long mstime_t; /* millisecond time type. */'),
('The inspected expiry predicate actually calls the getter.','src/expire.c','return (when <= commandTimeSnapshot() && !server.loading && !server.masterhost);')],
'rails':[
('The header fallback joins the original and REQUEST_METHOD reads with Ruby ||.','lib/action_dispatch/http/request.rb','get_header("rack.methodoverride.original_method") ||'),
('check_method gates lookup on the truthiness of name.','lib/action_dispatch/http/request.rb','if name'),
('An unrecognized truthy name can raise UnknownHttpMethod.','lib/action_dispatch/http/request.rb','HTTP_METHOD_LOOKUP[name] || raise(ActionController::UnknownHttpMethod')],
'go-image-optimizer':[
('The documented aggregate quantity is canvas-sized frame pixel work.','backend/internal/infrastructure/imaging/limits.go','// DefaultMaxAnimatedFramePixels caps canvas-sized animation work.'),
('The source divides maxPixels by height and frameCount before comparing width.','backend/internal/infrastructure/imaging/limits.go','if width > maxPixels/height/frameCount {')]
}
notes={
'chi':'Both languages preserve helper separation. Logging backend identity/durability/request-wide observability are explicit unverified boundaries, not negative claims about the whole project.',
'duckdb':'Both ordinary input paths means bool true versus false through this straight-line factory, not two syntactic branches or a second API. The bool constructor uses an initializer; it is not represented as the exact factory assignment. SQL execution/layout were not tested.',
'ruff':'Both languages preserve nonempty versus empty-list reachability, panic versus Result, and configuration versus resolver function ownership. No concrete path-trigger execution or formatter run occurred.',
'redis':'No fresh clock read occurs in the full getter body; broader update schedules/concurrency remain unverified. Historical dataset statement about no Redis execution describes that original experiment, not a universal claim about all repository activity.',
'rails':'Empty String truthiness is stable Ruby language semantics needed to interpret the source; it is not a token-membership proof. Both languages distinguish fallback selection from validation. Package version/hash is used, without an invented Rails checkout revision.',
'go-image-optimizer':'Both languages distinguish pixel arithmetic from measured bytes/allocation/RAM. The whole acquired function has no byte/allocation measurement. Earlier positive-dimension/frame guards qualify the division; no runtime memory cap is established.'}
records=[]
for pair, acquired in zip(protocol['pairs'], acquisition['pairs']):
 name=pair['family'].split(':',1)[1]; assert pair['family']==acquired['family']
 originals=[]
 for meta in pair['rows']:
  raw=lines[meta['line']-1]; assert sha(raw.encode())==meta['row_sha256']
  row=json.loads(raw);assert row['canonical_record_id']==meta['canonical_record_id']
  for key in ['source_evidence_ref','document_ref','claim_alignment_ref']:
   ref=meta[key];assert sha(Path(ref['path']).read_bytes())==ref['sha256']
  originals.append({'canonical_record_id':row['canonical_record_id'],'language':row['language'],'question':row['question'],'answer':row['answer'],'row_sha256':meta['row_sha256']})
 files={f['path']:f for f in acquired['files']};atoms=[]
 for index,(claim,path,witness) in enumerate(specs[name],1):
  f=files[path];raw=Path(f['snapshot']).read_bytes();assert sha(raw)==f['sha256'];text=raw.decode();assert witness in text
  start=text[:text.index(witness)].count('\n')+1
  atoms.append({'id':name+'-'+str(index),'proposition':claim,'source_identity':acquired['source_identity'],'source_path':path,'source_sha256':f['sha256'],'witness_line':start,'literal_witness':witness,'verdict':'SUPPORTED','review_basis':'Manual interpretation of full acquired context, not witness membership alone'})
 records.append({'family':pair['family'],'original_pair':originals,'selected_source_atoms':atoms,'source_only_question_relevance':'PASS','en_pt_semantic_parity':'PASS_FOR_THIS_PAIR','critical_unsupported_claim_found':False,'review_note':notes[name],'editorial_recommendation':'RETAIN_IN_QUARANTINE_FOR_OWNER_REVIEW','owner_approved':False,'rights_cleared':False,'training_gold':False})
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':'original-faq-semantic-sample-protocol-v1.json','reviewer':'Same campaign Codex agent; not independent human review','pairs':records,'pair_count':6,'language_records':12,'selected_unique_source_atoms':sum(len(r['selected_source_atoms']) for r in records),'full_original305_precision':None,'independent_holdout':False,'pair_source_review_pass':{'numerator':6,'denominator':6,'scope':'Only these six metadata-selected source-only FAQ pairs; procedural/epistemic scope clauses reviewed separately; no global acceptance or training approval'},'original_rows_and_splits_unchanged':True,'model_calls':0,'optimizer_updates':0,'gold':0}
with (P/'original-faq-semantic-sample-review-v1.json').open('x') as f:json.dump(result,f,indent=2,ensure_ascii=False);f.write('\n')
print(json.dumps({k:v for k,v in result.items() if k!='pairs'},indent=2))
