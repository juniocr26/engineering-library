"""Cross-check final report numerators/units against terminal evidence, no experiment rerun."""
from pathlib import Path
from collections import Counter
import datetime,hashlib,json
P=Path(__file__).resolve().parent
checks=[];inputs=set()
def read(name):inputs.add(name);return json.loads((P/name).read_text())
def check(id,observed,expected,scope):
 assert observed==expected,(id,observed,expected)
 checks.append({'id':id,'observed':observed,'expected':expected,'matches':True,'scope':scope})
ledger=read('current-campaign-inference-ledger-v2.json');rows=ledger['attempts']
check('attempts',len(rows),98,'Terminaltransportattempts, notdocumentaccuracy')
returned=[r for r in rows if r['exit_code']==0]
check('returned',len(returned),95,'ReturnedHTTPoutputs, notsemanticpasses')
check('normal',sum(r['done_reason']=='stop'for r in returned),87,'Generationstopreason')
check('length',sum(r['done_reason']=='length'for r in returned),8,'Truncationoperationalcount')
check('transport',sum(r['exit_code']!=0 for r in rows),3,'Nooutputsemanticprecisionfortransportfailure')
check('tokens',sum(r['reported_generated_tokens']or 0 for r in rows),31911,'Heterogeneousoperationalsumonly')
check('request_options',all(r['requested_options']['temperature']==0 and r['requested_options']['seed']==11621 and r['requested_options']['num_thread']==4 for r in rows),True,'Frozenrequestidentity, notmatchedalloutputbudgets')
check('contexts',sorted({r['requested_options']['num_ctx']for r in rows}),[4096,8192],'Resourceconditionseparatefromstandard8192')
catalog=read('acceptance-metric-catalog-v5.json');strategy={r['method']:r for r in catalog['strategy_rows']}
expected={'A':(0,3),'B':(0,3),'C':(0,3),'D':(0,3),'E':(0,3),'F':(0,3),'G':(0,3),'H':(0,3),'J':(0,3),'K':(3,3),'L':(0,3),'M':(0,1),'P':(0,1),'Q':(0,3),'T':(2,2)}
for method,pair in expected.items():
 result=strategy[method]['complete_requested_unit_acceptance'];check('strategy-'+method,[result['numerator'],result['denominator']],list(pair),'Eachownrequestedunit; no pooledmodelaccuracy')
check('A-Gcalls',sum(strategy[m]['actual_inference_requests']for m in 'ABCDEFG'),25,'FreusesD; not3additionalmodelcalls')
check('Fnewcalls',strategy['F']['actual_inference_requests'],0,'Independentcodepathnotindependenthuman')
for method in ['W','X','Q-option-order']:check('no-document-denominator-'+method,strategy[method]['complete_requested_unit_acceptance'],None,'Line/choicecontrolnotcompletenotetrial')
dimensions=read('complete-document-dimension-index-v1.json');records=dimensions['new_bounded_note_workflows']+dimensions['preexisting_selected_owner_chapter_pairs']+dimensions['original_dataset_public_chapter_pairs']+[dimensions['original_dataset_owned_adapter_pair']]
check('dimension-records',len(records),61,'Overlappingscopes, not61independenttrials')
required=read('acceptance-protocol-v2.json')['document_level']['dimensions']
check('all11dimensions',all([r['dimension']for r in row['dimensions']]==required for row in records),True,'Explicitordered11dimensionarrays')
check('dimension-counts',dimensions['record_counts'],{'bounded_note_workflows':34,'selected_preexisting_owner_pairs':3,'original_public_pairs':23,'original_owned_adapter_pairs':1},'Granularitykeptseparate')
for task,expected_counts in [('fastapi',[5,2,3,10]),('cobra',[7,3,0,10])]:
 d=read('source-only-fact-render-v1/'+task+'/L/semantic-review-v2.json')['selected_generated_proposition_metrics']
 check('selected-L-'+task,[d.get(k,0)for k in ['supported','contradicted','insufficient','total']],expected_counts,'Selectedpropositionsnotwhole-proseprecision')
zod=read('source-only-fact-render-v1/zod/L/semantic-review-v2.json')
for field,want in [('english_selected_proposition_metrics',[5,4,1,10]),('bilingual_pair_metrics',[2,4,4,10])]:
 d=zod[field];check('Zod-'+field,[d.get(k,0)for k in ['supported','contradicted','insufficient','total']],want,'ENpropositionsandbilingualpairunitsaredifferent')
lifecycle=read('lifecycle-matrix-and-rate-audit-v8.json')
check('lifecycle-cases',lifecycle['new_owned_unique_cases'],84,'Owneddevelopmentcases')
check('lifecycle-cohorts',len(lifecycle['new_owned_cohorts']),11,'No pooledgenericaccuracy')
check('matrix-count',lifecycle['matrix_rate_invariants_verified'],85,'Allcurrentmatrix/ratevaluesrecomputed')
new=next(c for c in lifecycle['new_owned_cohorts']if c['cohort']=='new-retirement-reachability-challenge-8')
for condition,wrong,recall in [('v7_action',[4,4],[4,4]),('v8_action',[0,4],[1,4])]:
 for metric,want in [('false_remove',wrong),('remove_recall',recall)]:
  value=new['conditions'][condition][metric];check(condition+'-'+metric,[value['numerator'],value['denominator']],want,'Newreachabilitycohortonly')
check('readiness-gates',read('fine-tuning-nine-gate-review-v7.json')['all_nine_gates'],{str(i):'NO_GO'for i in range(1,10)},'Nolaunchauthorized')
source=read('selected-source-git-binding-audit-v1.json');check('public-git-files',source['selected_local_git_file_identities'],69,'Selected14publicclones; Railsoutside42separate')
check('public-git-hashes',source['all_retained_snapshot_hashes_match_exact_git_revision_blobs'],True,'Identitynotsemantictruth')
own=read('own-selected-inspected-files-v1.json');check('own-existing-files',own['preexisting_own_paths'],13,'Selectedsource/testscope, notfullrepoinspection')
integrity=read('campaign-closing-integrity-v2.json');check('original-input-counts',integrity['counts'],{'datasets':7,'records_unchanged':305,'immutable_references':398,'prior_files':2341,'manual_files':22},'Hashreadingnotprivatebodysemanticreview')
check('all-inputs-match',integrity['all_input_hashes_match'],True,'Originalbytespreserved')
check('external-statuses',integrity['all_41_external_statuses_unchanged'],True,'Cocosbaselinechangesretained')
check('report-catalog-lifecycle-metadata',[catalog['lifecycle']['new_owned_unique_cases'],catalog['lifecycle']['new_owned_cohorts'],catalog['lifecycle']['source']],[84,11,'lifecycle-matrix-and-rate-audit-v8.json'],'Currentcuratedmetadata, oldversionretainedashistory')
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'check_count':len(checks),
 'all_match':True,'input_files':[{'path':name,'sha256':hashlib.sha256((P/name).read_bytes()).hexdigest()}for name in sorted(inputs)],
 'scope':'Finalnumerator/unit/reportconsistencyaudit. No newpredictions, sourceadjudication, permanenttestsorunchangedsuitereruns. Doesnotproveallfreeprosesemantics.',
 'gold':0,'optimizer_updates':0}
with(P/'final-reporting-metric-consistency-v1.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps({k:v for k,v in result.items()if k not in ['checks','input_files']},indent=2))
