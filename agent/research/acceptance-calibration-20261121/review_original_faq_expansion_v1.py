"""Manual selected atomic annotations for the preregistered 33-pair expansion."""
import json,hashlib,datetime
from pathlib import Path
P=Path(__file__).resolve().parent
Q=json.loads((P/'original-faq-expansion-protocol-v1.json').read_text())
A=json.loads((P/'original-faq-expansion-source-acquisition-v1.json').read_text())
source_by_lineage={r['lineage']:r for r in A['lineages']}
raw_rows=Path(Q['source_dataset']).read_text().splitlines()
# Curated interpretations after reading original EN/PT answers and full relevant source context.
# A tuple is (single proposition, source path suffix, literal witnesses). Membership is checked
# mechanically only to catch transcription mistakes; the SUPPORTED judgment is manual.
S={
'panic-response':[
('ErrAbortHandler is re-panicked before the later logging calls.','recoverer.go',['if rvr == http.ErrAbortHandler {','panic(rvr)','logEntry := GetLogEntry(r)']),
('The selected 500 status call is guarded by a non-Upgrade Connection header.','recoverer.go',['if r.Header.Get("Connection") != "Upgrade" {','w.WriteHeader(http.StatusInternalServerError)'])],
 'timeout-construction':[
('Timeout outer construction returns a middleware factory rather than invoking the request callback.','timeout.go',['func Timeout(timeout time.Duration) func(next http.Handler) http.Handler {','return func(next http.Handler) http.Handler {']),
('Applying that factory returns the wrapped handler.','timeout.go',['return http.HandlerFunc(fn)']),
('The selected callback calls next.ServeHTTP directly; no goroutine statement in its full body forcibly interrupts it.','timeout.go',['next.ServeHTTP(w, r)'])],
'concurrency-not-per-user-rate':[
('Processing-token capacity is the supplied positive Limit.','throttle.go',['tokens:         make(chan token, opts.Limit)']),
('Backlog admission-token capacity includes Limit plus BacklogLimit.','throttle.go',['backlogTokens:  make(chan token, opts.Limit+opts.BacklogLimit)']),
('The waiting branch creates a timer after no immediate processing token is available.','throttle.go',['// No immediate token available, need to wait with timer','timer := time.NewTimer(t.backlogTimeout)'])],
'retry-header-not-execution':[
('The helper sets Retry-After from its callback result rather than retrying the next handler.','throttle.go',['delay := t.retryAfterFn(ctxDone)','w.Header().Set("Retry-After", strconv.FormatInt(int64(seconds), 10))']),
('Negative delays assign zero seconds.','throttle.go',['if delay < 0 {','seconds = 0']),
('A nonzero nonnegative second remainder increments the truncated seconds; exact whole seconds avoid that increment.','throttle.go',['seconds := delay / time.Second','} else if delay%time.Second != 0 {','seconds++'])],
'zero-backlog':[
('The explicit backlog validation rejects values below zero, not zero itself.','throttle.go',['if opts.BacklogLimit < 0 {']),
('With positive Limit and zero backlog, admission capacity remains Limit.','throttle.go',['backlogTokens:  make(chan token, opts.Limit+opts.BacklogLimit)'])],
'no-query-pipeline-proof':[
('The BOOLEAN factory constructs a local Value with logical type BOOLEAN.','value.cpp',['Value result(LogicalType::BOOLEAN);']),
('It writes the input Boolean to the payload member.','value.cpp',['result.value_.boolean = value;']),
('It separately writes a false null flag.','value.cpp',['result.is_null = false;']),
('It returns that same local result.','value.cpp',['Value Value::BOOLEAN(bool value) {','return result;']),
('The additional header declares the BOOLEAN logical-type identifier.','types.hpp',['static constexpr const LogicalTypeId BOOLEAN = LogicalTypeId::BOOLEAN;']),
('The additional header declares the LogicalType conversion constructor.','types.hpp',['DUCKDB_API LogicalType(LogicalTypeId id);'])],
'static-factory-identity':[
('The public header declares BOOLEAN as a static Value-returning bool factory.','value.hpp',['DUCKDB_API static Value BOOLEAN(bool value);']),
('A distinct constructor declaration accepts a LogicalType argument.','value.hpp',['explicit Value(LogicalType type = LogicalType::SQLNULL)'])],
'environment-key-ownership':[
('The zero-argument method branch reads original_method with REQUEST_METHOD fallback.','request.rb',['def method(*args)','get_header("rack.methodoverride.original_method") ||','get_header("REQUEST_METHOD")']),
('request_method instead checks the result of super.','request.rb',['def request_method','@request_method ||= check_method(super)'])],
'memoized-method-invalidation':[
('request_method uses its own memoized instance variable.','request.rb',['@request_method ||= check_method(super)']),
('method uses a distinct memoized instance variable in its no-argument branch.','request.rb',['@method ||= check_method('])],
'inclusive-expiry-boundary':[
('The final time comparison includes equality.','expire.c',['return (when <= commandTimeSnapshot() && !server.loading && !server.masterhost);']),
('A current master client returns zero before that final comparison.','expire.c',['if (server.current_client && server.current_client->flags & CLIENT_MASTER) return 0;']),
('Loading state participates negatively in the final conjunction.','expire.c',['!server.loading']),
('masterhost participates negatively in the final conjunction.','expire.c',['!server.masterhost'])],
'predicate-versus-key-deletion':[
('The caller tests checkAlreadyExpired before entering the explicit delete branch.','expire.c',['if (checkAlreadyExpired(when)) {','int deleted = dbGenericDelete']),
('That caller branch increments dirty state.','expire.c',['server.dirty++;']),
('That caller branch rewrites the client command.','expire.c',['rewriteClientCommandVector(c,2,aux,key);']),
('That caller branch issues a delete notification.','expire.c',['notifyKeyspaceEvent(NOTIFY_GENERIC,"del",key,c->db->id);']),
('That caller branch issues a reply.','expire.c',['addReply(c, shared.cone);']),
('The alternative caller branch invokes setExpire.','expire.c',['kv = setExpire(c,c->db,key,when);'])],
'clock-snapshot-refresh':[
('The getter directly returns server.cmd_time_snapshot.','server.c',['return server.cmd_time_snapshot;']),
('mstime_t is declared as the millisecond time type.','server.h',['typedef long long mstime_t; /* millisecond time type. */']),
('The snapshot field comment describes root-execution nesting.','server.h',['mstime_t cmd_time_snapshot; /* Time snapshot of the root execution nesting. */'])],
'reply-versus-key-deletion':[
('The generic TTL body calls a lookup helper.','expire.c',['kvobj *kv = lookupKeyReadWithFlags']),
('It obtains the expiry through kvobjGetExpire.','expire.c',['expire = kvobjGetExpire(kv);']),
('It selects an explicit -1 sentinel reply or a non-sentinel reply expression.','expire.c',['if (ttl == -1) {','addReplyLongLong(c,-1);','addReplyLongLong(c,output_ms ? ttl : ((ttl+500)/1000));'])],
'sentinels-before-rounding':[
('A missing-key -2 reply returns before the expiry conversion.','expire.c',['if (kv == NULL) {','addReplyLongLong(c,-2);','expire = kvobjGetExpire(kv);']),
('The no-expiry -1 sentinel uses its own branch rather than non-sentinel arithmetic.','expire.c',['if (ttl == -1) {','addReplyLongLong(c,-1);','} else {'])],
'first-matching-vector-entry':[
('The iterator visits inner vector entries through iter().filter_map.','types.rs',['self.inner.iter().filter_map(move |entry| {']),
('It checks basename before the alternative absolute match.','types.rs',['if entry.basename_matcher.is_match_candidate(&basename) {','} else if entry.absolute_matcher.is_match_candidate(&absolute) {']),
('Negation is an explicit separate condition within match selection.','types.rs',['if entry.negated {']),
('The target-version helper selects the next yielded value and copies it.','types.rs',['.iter_matches(path, "Setting Python version")','.next()','.copied()'])],
'optional-version-not-boolean':[
('The helper result type is Option<ast::PythonVersion>, not Boolean.','types.rs',['pub fn is_match(&self, path: &Path) -> Option<ast::PythonVersion>']),
('An empty compiled list returns None.','types.rs',['if self.0.is_empty() {','return None;']),
('The caller uses the stored unresolved target version when the option is absent.','settings.rs',['.unwrap_or(self.unresolved_target_version)'])],
'guard-error-order':[
('The animation validator calls static validation first.','limits.go',['if err := ValidateImageSize(width, height, DefaultMaxDecodedPixels); err != nil {']),
('A static error returns before the frame-count guard.','limits.go',['return err','if frameCount <= 0 {'])],
'static-versus-aggregate-budget':[
('The animation validator explicitly passes DefaultMaxDecodedPixels to its first helper call.','limits.go',['ValidateImageSize(width, height, DefaultMaxDecodedPixels)']),
('The later aggregate expression uses the maxPixels parameter.','limits.go',['if width > maxPixels/height/frameCount {']),
('The aggregate default exists as a separate declaration.','limits.go',['DefaultMaxAnimatedFramePixels = 64_000_000'])],
'cancellation-boundary':[
('The compressor call receives input without a context argument.','usecase.go',['result, err := u.compressor.Compress(input)']),
('Context error checking precedes the compressor call.','usecase.go',['if err := ctx.Err(); err != nil {','result, err := u.compressor.Compress(input)']),
('A later context check follows that call and can return a zero Result.','usecase.go',['result, err := u.compressor.Compress(input)','if err := ctx.Err(); err != nil {','return Result{}, err'])],
'concrete-compressor-composition':[
('The router constructs the use case from compress.NewCompressor().','router.go',['compressImage := imagecompression.NewUseCase(compress.NewCompressor())']),
('It supplies that use case to the handler factory at POST /images/compress.','router.go',['mux.HandleFunc("POST /images/compress", compressimage.ProcessImage(logger, compressImage))']),
('The returned handler calls the supplied use case with request context and uploaded bytes.','handler.go',['result, err := useCase.Execute(r.Context(), imageBytes)'])],
'error-result-handoff':[
('The use-case compressor-error branch returns Result{} instead of the supplied result.','usecase.go',['result, err := u.compressor.Compress(input)','return Result{}, err']),
('The handler delegates non-nil Execute errors to writeCompressionError.','handler.go',['result, err := useCase.Execute(r.Context(), imageBytes)','writeCompressionError(w, logger, err)']),
('The handler writes successful result.Data only on its later success path.','handler.go',['w.WriteHeader(http.StatusOK)','w.Write(result.Data)']),
('Concrete compression selects a codec after DetectFormat.','compressor.go',['detected, err := imaging.DetectFormat(input)','switch detected.Format {'])],
'configuration-consumer':[
('main invokes config.Load before server construction.','main.go',['cfg, err := config.Load()','server := httpserver.NewServer(cfg, logger)']),
('The Load-error branch exits before that construction.','main.go',['logger.Error("failed to load configuration", "error", err)','os.Exit(1)']),
('The server constructor obtains the address from cfg.Addr().','server.go',['Addr:              cfg.Addr()']),
('The server constructor obtains its handler from NewRouter(logger).','server.go',['Handler:           NewRouter(logger)']),
('The constructor assigns read-header, read, write and idle timeout fields.','server.go',['ReadHeaderTimeout: readHeaderTimeout','ReadTimeout:       imageRequestTimeout','WriteTimeout:      imageRequestTimeout','IdleTimeout:       idleConnectionTimeout'])],
'empty-port-fallback':[
('getEnv uses fallback when the obtained string is empty.','config.go',['value := os.Getenv(key)','if value == "" {','return fallback']),
('The nonempty branch forwards the value without local trimming.','config.go',['return value']),
('Load validates the populated string port.','config.go',['if err := validatePort(cfg.Port); err != nil {'])],
'zero-config-on-error':[
('Load returns a zero Config on validation error.','config.go',['return Config{}, err']),
('Load returns the populated cfg only on the success path.','config.go',['return cfg, nil']),
('validatePort parses into a separate integer rather than assigning the stored string field.','config.go',['number, err := strconv.Atoi(port)'])],
'explicit-budget-argument':[
('The static wrapper forwards the supplied maxPixels parameter.','limits.go',['return ValidateImageSize(cfg.Width, cfg.Height, maxPixels)']),
('Its named decoded-pixel default is declared separately.','limits.go',['DefaultMaxDecodedPixels = 32_000_000'])],
'quotient-equality':[
('The static budget comparison is strictly greater than.','limits.go',['if width > maxPixels/height {']),
('Nonpositive dimensions return before that division.','limits.go',['if width <= 0 || height <= 0 {','return imageprocessing.ErrInvalidImage'])],
'wrapper-parameters':[
('ValidateDimensions declares cfg and maxPixels parameters.','limits.go',['func ValidateDimensions(cfg image.Config, maxPixels int) error {']),
('It extracts cfg.Width and cfg.Height as helper arguments.','limits.go',['return ValidateImageSize(cfg.Width, cfg.Height, maxPixels)'])],
'aspect-ratio-validation-order':[
('Pixel mode initially checks both converted width and height for safe integers.','resize-options.ts',['let width = Number(options.width);','let height = Number(options.height);','![width, height].every(Number.isSafeInteger)']),
('That initial invalid-dimension branch returns null before later axis-specific scale selection.','resize-options.ts',['return null;','options.axis === "height" ? height / info.height : width / info.width'])],
'error-message-versus-validation':[
('dimensionError receives target as a parameter typed from targetDimensions.','resize-options.ts',['target: ReturnType<typeof targetDimensions>']),
('Its first guard tests target falsiness and returns a message.','resize-options.ts',['if (!target) return "Enter a positive whole number for each dimension.";']),
('String conversion belongs to targetDimensions.','resize-options.ts',['let width = Number(options.width);','let height = Number(options.height);'])],
'pixel-boundary-and-message-return':[
('The single-frame product check is strictly greater than 32 million.','resize-options.ts',['if (target.width * target.height > 32_000_000)']),
('The aggregate product check is strictly greater than 64 million.','resize-options.ts',['if (target.width * target.height * info.frameCount > 64_000_000)']),
('dimensionError returns its message strings or null in its selected body.','resize-options.ts',['return "The output must not exceed 32 million pixels.";','return "This animation exceeds the output frame pixel limit.";','return null;'])],
'inclusive-quality-boundaries':[
('The lower quality clamp uses value<1.','compressor.go',['if value < 1 {']),
('The upper quality clamp uses value>100.','compressor.go',['if value > 100 {']),
('The zero branch returns before those comparisons.','compressor.go',['if value == 0 {','return fallback'])],
'no-codec-quality-equivalence':[
('clampQuality returns its fallback unchanged when input is zero.','compressor.go',['func clampQuality(value, fallback int) int {','if value == 0 {','return fallback']),
('Nonzero input below one returns one.','compressor.go',['if value < 1 {','return 1']),
('Input above100 returns100.','compressor.go',['if value > 100 {','return 100']),
('Other input reaches the unchanged-value return.','compressor.go',['return value'])],
'zero-input-fallback':[
('The fallback-return branch is selected by zero input.','compressor.go',['if value == 0 {','return fallback']),
('The JPEG wrapper supplies DefaultJPEGQuality.','compressor.go',['return clampQuality(c.JPEGQuality, DefaultJPEGQuality)'])]
}
result=[];atoms=[]
for pair in Q['pairs']:
 qid=json.loads(pair['question_identity'])[1];assert qid in S
 acquired=source_by_lineage[pair['lineage']];original=[]
 for m in pair['rows']:
  row=json.loads(raw_rows[m['line']-1]);assert hashlib.sha256(json.dumps(row,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()==m['canonical_row_sha256']
  doc=Path(m['document_ref']['path']).read_bytes();assert hashlib.sha256(doc).hexdigest()==m['document_ref']['sha256'];assert ' '.join(row['answer'].split()) in ' '.join(doc.decode().split())
  original.append({'language':row['language'],'id':row['canonical_record_id'],'question':row['question'],'answer':row['answer'],'row_hash':m['canonical_row_sha256']})
 ids=[]
 for index,(claim,suffix,witnesses) in enumerate(S[qid],1):
  choices=[f for f in acquired['files'] if f['path'].endswith(suffix)];assert len(choices)==1,(qid,suffix)
  f=choices[0];raw=Path(f['snapshot']).read_bytes();assert hashlib.sha256(raw).hexdigest()==f['sha256'];text=raw.decode();spans=[]
  for w in witnesses:
   assert w in text,(qid,w)
   # All occurrences retained; a common token's first occurrence is never promoted as the lexical owner.
   hits=[];start=0
   while True:
    at=text.find(w,start)
    if at<0:break
    hits.append(text[:at].count('\n')+1);start=at+len(w)
   spans.append({'literal':w,'all_occurrence_lines':hits})
  cid='FAQ-EXP-'+qid+'-'+str(index);ids.append(cid)
  atoms.append({'claim_id':cid,'family':pair['family'],'lineage':pair['lineage'],'question_id':qid,'source_revision':acquired['revision'],'package':acquired['package'],'package_version':acquired['package_version'],'source_path':f['path'],'source_snapshot':f['snapshot'],'source_sha256':f['sha256'],'exact_witnesses':spans,'expected_interpretation':claim,'generated_interpretation':claim,'generated_occurrences':'Original EN/PT answer text linked by question_id in pairs; manual paraphrase identifies the reviewed clause.','verdict':'SUPPORTED','critical_if_false':True,'en_pt_consistency':'Preserved for this selected source proposition','reviewer':'Same campaign agent after full relevant context/EN/PT reading; not independent human','mechanical_limits':'Witness membership, hashes and document inclusion are integrity checks, not the semantic verdict.'})
 result.append({'family':pair['family'],'lineage':pair['lineage'],'question_id':qid,'original_pair':original,'selected_atom_ids':ids,'source_relationship_and_question_relevance':'PASS_BOUNDED_SOURCE_REVIEW','en_pt_parity':'PASS_BOUNDED_SOURCE_REVIEW','scope_and_epistemic_review':'Source-only negative statements scoped to selected bodies; no hidden helper, runtime, memory, delivery, pipeline, training-rights or whole-project guarantee inferred. Tables/diagrams interpreted as source traces, not executions.','procedural_caveat':'Historical rechecked/executed/not-executed wording belongs to original retained review. Current campaign confirms its own recorded read-only acquisition and observations; no independent historical actor certification.','owner_approved':False,'training_gold':False,'rights_cleared':False})
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':'original-faq-expansion-protocol-v1.json','pairs':result,'selected_atoms':atoms,'pair_count':len(result),'language_rows':len(result)*2,'selected_atomic_annotation_count':len(atoms),'precision_scope':'Selected source propositions only; some overlap with previous questions/topics and repeated relationships. Not an independent atom count across the entire305 corpus and not full-prose precision.','full305_precision':None,'source_pair_pass':{'numerator':33,'denominator':33,'unit':'Bounded technical source/translation review, not owner acceptance or whole-chapter acceptance'},'normalized_answer_document_membership':{'numerator':66,'denominator':66,'not_semantic_proof':True},'original_dataset_unchanged':True,'source_execution':False,'model_calls':0,'independent_holdout':False,'gold':0,'optimizer_updates':0}
with (P/'original-faq-expansion-semantic-review-v1.json').open('x') as f:json.dump(out,f,indent=2,ensure_ascii=False);f.write('\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['pairs','selected_atoms']},indent=2))
