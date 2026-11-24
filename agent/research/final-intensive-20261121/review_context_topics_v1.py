"""Record full paired prose/source review separately from mechanical checks."""
from pathlib import Path
import datetime
import hashlib
import json

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
PRIOR=ROOT/'agent/research/portfolio-vivabem-20261120'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
protocol=json.loads((P/'remaining-chapters-v3-review-protocol-v1.json').read_text())
observations=json.loads((P/'context-topic-source-acquisition-v1.json').read_text())['observations']
mechanical=json.loads((P/'context-topic-verification-results-v1.json').read_text())
assert mechanical['all_frozen_source_checks_pass']
reviews={
    'fastapi-request-context':[
        ('Scope and identity','Pinned revision, selected path and MIT notice verified from fresh Git objects; no whole-project/runtime/owner claim.'),
        ('Factory view','routing1322-1347 initializes route from self and selects effective context under non-None/original_route identity guard; route keywords preserved, self.form_limits exception does not contradict qualified wording.'),
        ('Handler solver handoff','routing528-535 passes declared arguments without dependency_cache or **kwargs; direct import at66-76 and nested app return821 verified.'),
        ('Cache initialization and propagation','utils679/700-701 defaults None then local dict;726-737 recursive keyword and823-829 constructor handoff verified. Global/request isolation and lifetime expressly unknown.'),
        ('Endpoint guarded path','Selected ordinary call762-766 is under not errors and else streaming/generator branches; call values preserved. Streaming paths actually contain their own direct dependant.call, as the chapter carefully allows.'),
        ('Endpoint helper','routing372-385 has assertion, coroutine await and threadpool _run_sync_endpoint with function/arguments. No execution claim.'),
        ('Serialization and errors','Non-Response branch encloses selected serialization784-796. Request error808-815 and response validation343-369 are distinct; earlier body errors and stack assertions are acknowledged.'),
        ('Example','Both code fences byte-identical; current Python AST parse and keyword requirement comparison pass. Prepared request/import/runtime assumptions explicit.'),
        ('Written tests and FAQ','Fresh test_sub_counter64-71 has reset, two calls and1/1 then2/2/status assertions. Yield-scope file presence is not converted to lifetime proof. All four FAQs preserve guarded scope.'),
        ('Bilingual and procedural limits','Complete EN/PT texts read; conditions, negations, route view, identifiers, argument names and source-versus-runtime distinctions match. Separate procedures do not imply independent human reviewer.'),
    ],
    'chi-wrapper-context':[
        ('Scope and identity','Exact9f8adb source/test objects and04f7f55 historical implementation reacquired; selected current implementation also equals local checkout HEAD c64ed7 bytes.'),
        ('Capability dispatch','Native selected NewWrapResponseWriter and full source15-44 match protocol/capability routing, including final fl/base fallbacks; no universal protocol validity promised.'),
        ('Interface boundary','WrapResponseWriter48-70 omits ReadFrom. Selected HTTP2 comment differs from declared receiver methods; chapter explicitly refuses repo-wide/typechecked absence inference.'),
        ('Base state and accessors','Status/code, BytesWritten/bytes, Tee replacement, Unwrap and Discard146-148 supported. Base object holds state directly, other wrappers embed it; phrase base state is conceptual, not an assertion every return anonymously embeds a second basicWriter.'),
        ('Header and flush','Informational100-199 excluding101, discard-gated delegation, first final header, implicit200 and flush helper order all match83-128.'),
        ('Write and error precedence','Underlying write before buf[:n] tee; tee error replaces nil underlying error only; discard destinations and b.bytes+=n verified97-114. No client-delivery guarantee.'),
        ('ReadFrom fallback','Tee/discard branch211-220 calls io.Copy on base then immediately returns; no additional counter increment. Runtime reader/writer semantics explicitly left unknown.'),
        ('ReadFrom direct','Type assertion, rf.ReadFrom, n>0&&!wroteHeader recorded state, int(n) update and unchanged count/error return match221-229. No err==nil guard or wrapper WriteHeader call.'),
        ('Historical revision','04f7f55 direct path calls maybeWriteHeader before delegate;9f8adb uses post-return guarded state. Existing fallback is explicitly not attributed to that change.'),
        ('Example','Both fragments identical. Existing owned native parser freshly parsed wrapped fragment, with no typecheck/module resolution/Chi execution. Historical go.mod/module receipt retained separately.'),
        ('Written tests','Fresh entire selected test21-220 read: helper recorder, flush matrix, tee, discard, byte-count and discard ReadFrom assertions match. Manually constructed wrappers do not establish whole factory matrix.'),
        ('FAQ and bilingual','All four Q/A pairs supported within scoped source; EN/PT preserve counter/transport, order, guard, discard, error and runtime limits.'),
        ('Negative controls','Current source/native quotes support three Chi contradictions and unknown delivery control; prior unchanged-source12 manual controls retain their original label/status and are not recounted as new model-verifier trials.'),
    ],
}
rows=[]
for topic,groups in reviews.items():
    item=next(x for x in protocol['items'] if x['topic']==topic)
    for doc in item['documents']:
        assert sha((ROOT/doc['path']).read_bytes())==doc['sha256']
    gates={
        'G1':{'status':'PASS','evidence':'Fresh pinned Git source objects, complete original candidate hashes and relevant source spans; acquisition receipt.'},
        'G2':{'status':'PASS','evidence':'All actual EN/PT prose, examples/tests/FAQ and qualifications read against contextual source; review groups below. No critical contradiction observed.'},
        'G3':{'status':'PASS','evidence':'Frozen selected-path dependencies/callers/callees/state/errors covered; excluded global/runtime/type guarantees remain explicitly unknown.'},
        'G4':{'status':'PASS','evidence':'Original pre-generation topic scope and criteria retained; no retrospective scope/N-A changes. Complete candidate present in both languages.'},
        'G5':{'status':'PASS','evidence':'Owned Python or Go snippet parsed now; API shape/static-only and written-versus-run test limits truthful. Upstream application/tests not executed.'},
        'G6':{'status':'PASS','evidence':'Both full texts read; exact code fences and source expressions preserved; no changed condition, negation or unsupported language-specific claim observed.'},
        'G7':{'status':'PASS','evidence':'NO-OP for exact historical pinned-source candidate within declared scope; not whole-repository/current-new-revision approval. All source-dependent claims remain supported; selected Chi implementation also matches local HEAD bytes.'},
        'G8':{'status':'PASS','evidence':'Separate source reacquisition, exact-owner Python AST/native Go syntax queries and explicit negative/unknown challenges. Same-agent semantic adjudication; no independent-human claim.'},
        'G9':{'status':'INCONCLUSIVE','evidence':'Exact source/candidate/protocol/review bindings preserved; pending next current review dependency checkpoint and consumer restore.'},
    }
    rows.append({'topic':topic,'documents':item['documents'],'original_scope_spec':item['original_scope_spec'],
                 'original_scope_sha256':item['original_scope_sha256'],'gates':gates,
                 'review_groups':[{'group':label,'verdict':'SUPPORTED_WITH_FROZEN_STATIC_LIMITS','evidence':text} for label,text in groups],
                 'review_groups_not_atomic_claim_denominator':True,'atomic_precision_metric':None,
                 'all_actual_prose_reviewed':True,'critical_unsupported_claims_observed':0,
                 'lifecycle_action':'NO-OP','lifecycle_scope':'Exact existing pinned historical candidate only; no application or deletion.',
                 'technical_status':'INCONCLUSIVE_PENDING_EXACT_REVIEW_RECOVERY',
                 'owner_approved':False,'publication_approved':False,'training_gold_approved':False,
                 'training_eligible':False,'neural_contribution':False,'independent_human_review':False})
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'stronger_contract_sha256':sha((P/'documentation-done-v3.json').read_bytes()),
        're_review_protocol_sha256':sha((P/'remaining-chapters-v3-review-protocol-v1.json').read_bytes()),
        'source_acquisition_sha256':sha((P/'context-topic-source-acquisition-v1.json').read_bytes()),
        'mechanical_verification_sha256':sha((P/'context-topic-verification-results-v1.json').read_bytes()),
        'records':rows,'remaining_topics_not_reviewed':6,'no_historical_scores_replaced':True,
        'model_calls':0,'optimizer_updates':0,'gold':0}
with (P/'context-topic-complete-review-v1.json').open('x') as stream:
    json.dump(result,stream,indent=2,ensure_ascii=False)
    stream.write('\n')
print(json.dumps({'paired_chapters_reviewed':len(rows),'remaining_frozen_topics':6,'status':'G9_PENDING_NO_PROMOTION'}))
