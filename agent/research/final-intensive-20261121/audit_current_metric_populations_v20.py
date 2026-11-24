"""Recompute current receipt accounting without inventing semantic denominators."""
from pathlib import Path
import collections
import datetime
import hashlib
import json

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
evidence=[]


def read(name):
    path=P/name
    raw=path.read_bytes()
    evidence.append({'path':str(path.relative_to(ROOT)),'sha256':sha(raw)})
    return json.loads(raw)


metrics=[]


def metric(ident,numerator,denominator,population,method,baseline,limits,kind):
    if denominator is not None:
        assert type(denominator) is int and denominator>=0
        assert numerator is None or type(numerator) is int and 0<=numerator<=denominator
    metrics.append({'id':ident,'numerator':numerator,'denominator':denominator,
                    'ratio':None if numerator is None or not denominator else numerator/denominator,
                    'population':population,'method':method,'baseline':baseline,
                    'confidence_limitations':limits,'assessment_kind':kind,
                    'independent_human_review':False,'pool_with_other_populations':False})


binding=read('binding-study-results-v1.json')
negative=[r for r in binding['records'] if r['expected']!='VALID']
positive=[r for r in binding['records'] if r['expected']=='VALID']
fa=sum(r['observed']=='VALID' for r in negative)
fr=sum(r['observed']!='VALID' for r in positive)
assert {'numerator':fa,'denominator':len(negative)}==binding['integrity_false_admission']
assert {'numerator':fr,'denominator':len(positive)}==binding['integrity_false_refusal']
metric('envelope-integrity-false-admission',fa,len(negative),'Frozen dependency/identity mutations',
       'Recomputed actual envelope verdicts','Three intact preserved bundles',
       'Integrity protection only; trusted anchor and filesystem assumptions, not semantic truth.','INTEGRITY')
metric('envelope-integrity-false-refusal',fr,len(positive),'Intact dependency bundles',
       'Recomputed actual envelope verdicts','Same three development bundles',
       'One bounded identity profile, not a general semantic false-rejection rate.','INTEGRITY')

renderer=read('renderer-recovery-results-v1.json')
groups=[('baseline_exact_semantic_payload_replays',{'baseline'},'baseline_payload_equal_except_timestamp'),
        ('missing_or_stale_inputs_prevent_assembly',{'missing-schema-module','missing-source','missing-review','stale-content'},None),
        ('tampered_dependency_unsafe_assembly',{'wrong-reference-revision','invented-metadata-test-claim'},'unsafe_marker_in_assembled_notes'),
        ('dependency_envelope_refuses_tampering',{'wrong-reference-revision','invented-metadata-test-claim'},'frozen_dependency_envelope_refuses_mutation')]
for key,kinds,flag in groups:
    rows=[r for r in renderer['records'] if r['kind'] in kinds]
    n=sum(not r['assembled'] if flag is None else r[flag] is True for r in rows)
    assert {'numerator':n,'denominator':len(rows)}==renderer[key]
    metric('renderer-'+key,n,len(rows),sorted(kinds),'Actual restored research renderer observations',
           'Exact original dependency payload except timestamp',
           'Assembly is not technical acceptance. Corrupted trusted inputs are deliberate controls, not compromised originals.','ASSEMBLY_AND_BINDING')

faq=read('faq-question-binding-results-v1.json')
categories={'literal_violation_admissions':('LITERAL_VIOLATION',True),
            'literal_positive_refusals':('LITERAL_POSITIVE',False),
            'semantic_negative_binding_passes':('SEMANTIC_NEGATIVE_BINDING_BLIND',True),
            'legitimate_paraphrase_refused':('SEMANTIC_POSITIVE_OUTSIDE_LITERAL_POLICY',False)}
for key,(category,count_pass) in categories.items():
    rows=[r for r in faq['records'] if r['category']==category]
    n=sum((r['diagnostic']['status']=='LITERAL_BINDINGS_VALID')==count_pass for r in rows)
    declared=faq['metrics'][key]
    assert (n,len(rows))==(declared['numerator'],declared['denominator'])
    metric('faq-'+key,n,len(rows),declared['population'],declared['method'],declared['baseline'],
           declared['confidence_limitations'],'LITERAL_IDENTITY_WITH_SEPARATE_MANUAL_SEMANTIC_LABELS')

helper=read('helper-admission-results-v1.json')
admitted=sum(r['actual']=='ADMITTED_LEXICAL_UNIT' for r in helper['records'])
covered=set().union(*(set(r['admitted_quote_covers_reference_ids']) for r in helper['records']))
assert admitted==helper['admitted_requests']['numerator']
assert len(covered)==helper['exact_required_evidence_span_coverage']['numerator']
metric('helper-lexical-request-admission',admitted,len(helper['records']),
       'Eight source extraction requests covering 28 existing fact references','Actual extract and validate_unit, no job/journal',
       'Existing helper source and unchanged default budgets','Request admission is not semantic correctness or cause of historical neural failures.','LEXICAL_ACQUISITION')
metric('helper-physical-reference-span-coverage',len(covered),28,'Existing registered source spans',
       'Exact admitted quote coverage','28 required reference IDs',
       'Physical coverage, not whole-note acceptance or independent source facts.','LEXICAL_ACQUISITION')

source=read('source-claim-reacquisition-results-v1.json')
n=sum(r['whole_file_identity_matches'] and r['exact_span_matches'] for r in source['claims'])
assert n==source['source_identity_and_exact_span']['numerator']
metric('registered-source-pair-span-reacquisition',n,len(source['claims']),
       'Previously registered bilingual fact pairs','Separate Git object acquisition and exact span comparison',
       'Existing development-exposed source ledger','No new independent atomic total; contextual meanings were reviewed by the same campaign agent, not proved by hashes.','SOURCE_IDENTITY')

chapter_records=[*read('remaining-chapters-complete-recovery-review-v1.json')['records'],
                 *read('priority-pairs-complete-review-v2.json')['records']]
zod=read('zod-complete-review-v3.json')
chapter_records.append(dict(zod,topic='zod-core-safeparse',version='isolated_provenance_clarification_v3'))
chi=read('chi-revision-context-complete-review-v2.json')
chapter_records.append(dict(chi,topic='chi-wrap-response-writer',version='explicit_current_pin_maintenance_v1'))
original_gio=read('go-image-animation-original-target-review-v2.json')
chapter_records.append(dict(original_gio,topic='go-image-animation',version='original_dataset_target'))
chapter_records.append(read('go-image-animation-corrected-complete-review-v2.json'))
chapter_records.append(read('go-image-compression-original-target-review-v1.json'))
chapter_records.append(read('go-image-compression-corrected-complete-review-v3.json'))
chapter_records.append(read('go-image-configuration-complete-review-v2.json'))
chapter_records.append(read('starlette-server-error-complete-review-v2.json'))
chapter_records.append(read('frontend-dimensions-complete-review-v3.json'))
chapter_records.append(read('starlette-task-iteration-complete-review-v2.json'))
chapter_records.append(read('go-image-quality-complete-review-v2.json'))
chapter_records.append(read('go-image-dimensions-complete-review-v2.json'))
chapter_records.append(read('rails-request-complete-review-v2.json'))
chapter_records.append(read('redis-expiry-original-target-review-v1.json'))
chapter_records.append(read('redis-expiry-corrected-complete-review-v2.json'))
chapter_records.append(read('redis-ttl-complete-review-v2.json'))
chapter_records.append(read('ruff-target-complete-review-v3.json'))
chapter_records.append(read('opencv-depth-coercion-complete-review-v2.json'))
chapter_records.append(read('opencv-shape-contract-complete-review-v2.json'))
chapter_records.append(read('duckdb-target-complete-review-v2.json'))
chapter_records.append(read('prometheus-builder-complete-review-v2.json'))
chapter_records.append(read('prometheus-keep-original-target-review-v2.json'))
chapter_records.append(read('prometheus-keep-corrected-complete-review-v2.json'))
chapter_records.append(read('fastify-target-complete-review-v2.json'))
chapter_records.append(read('sqlx-in-expansion-complete-review-v2.json'))
chapter_records.append(read('sqlx-map-argument-binding-complete-review-v2.json'))
chapter_records.append(read('sdk-retry-original-target-review-v2.json'))
chapter_records.append(read('sdk-retry-corrected-complete-review-v2.json'))
chapter_records.append(read('chi-middleware-complete-review-v2.json'))
chapter_records.append(read('chi-throttle-workflow-complete-review-v2.json'))
by_bytes={}
for row in chapter_records:
    pair=sorted((d['path'],d['sha256']) for d in row['documents'])
    key=sha(json.dumps(pair).encode())
    assert key not in by_bytes,'Repeated gate-state update must not be counted as a new candidate'
    for d in row['documents']:
        assert sha((ROOT/d['path']).read_bytes())==d['sha256']
    if row['technical_status']=='TECHNICALLY_ACCEPTED':
        assert all(g['status']=='PASS' for g in row['gates'].values())
    by_bytes[key]={'topic':row['topic'],'version':row.get('version','original_frozen_pair'),
                  'documents':row['documents'],'technical_status':row['technical_status'],
                  'neural_contribution':False,'independent_task':False,
                  'accounting_unit':'Exact bilingual candidate pair, not translations or review-state transitions'}
chapter_counts=collections.Counter(r['technical_status'] for r in by_bytes.values())
maintenance=read('helper-candidate-complete-review-v2.json')
assert maintenance['technical_status']=='TECHNICALLY_ACCEPTED'
metric('new-neural-complete-output-acceptance',0,0,'Current campaign local model requests',
       'No new model request executed','Historical populations retained separately',
       'Zero denominator: no current neural acceptance rate or gain can be inferred.','NEURAL_CURRENT')
metric('new-neural-inference-tokens',0,None,'Current campaign local model requests','No request executed',
       'Historical inference receipts unchanged','Count zero, not a performance comparison.','COST')
for ident in ['global-atomic-supported-claim-precision','independent-bilingual-semantic-agreement',
              'independent-technical-identifier-preservation','independent-lifecycle-decision-accuracy',
              'new-autonomous-unsafe-REMOVE-rate']:
    metric(ident,None,None,'No sufficient new independent eligible population',
           'Not measured as a generalized performance statistic','Historical/scoped measurements stay in separate receipts',
           'Review groups, translations, source hashes, manual topic selection and no-action cases cannot fill this denominator.','INSUFFICIENT_EVIDENCE')

result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'metrics':metrics,'source_evidence':evidence,
        'chapter_version_accounting':{'versioned_pair_count':len(by_bytes),'statuses':dict(chapter_counts),
                                    'records':list(by_bytes.values()),'performance_rate':None,
                                    'limit':'Related original/corrected versions and heterogeneous manual scopes are descriptive accounting, not independent neural trials.'},
        'maintenance_accounting_separate':{'candidate_pair_count':1,'technical_status':maintenance['technical_status'],
                                         'authorship':'Manual maintenance note','neural_contribution':False},
        'all_recomputed_receipt_counts_match':True,'new_model_calls':0,'optimizer_updates':0,'owner_gold':0,
        'model_ready':'INSUFFICIENT_EVIDENCE','approval_or_production_action':False}
with (P/'current-metric-population-audit-results-v20.json').open('x') as stream:
    json.dump(result,stream,indent=2)
    stream.write('\n')
print(json.dumps({'mechanical_metric_rows':len(metrics),'chapter_versioned_pairs':len(by_bytes),
                  'chapter_statuses':dict(chapter_counts),'helper_pair_count_separate':1,
                  'recomputed_counts_match':True,'new_neural_rate':None}))
