"""Requirement-by-requirement evidence registry; completion/time remain explicitly pending."""
from pathlib import Path
import datetime,hashlib,json
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
rows=[]

def add(id,requirement,evidence,outcome,status='ADDRESSED_WITH_STATED_LIMITS'):
 refs=[]
 for name in evidence:
  path=P/name
  if not path.is_file():raise ValueError('Missing evidence: '+name)
  refs.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 rows.append({'id':id,'requirement':requirement,'status':status,'evidence':refs,'observed_outcome':outcome})

add('1.01','Locate and verify42repositories32Portfolio+10VivaBem',['baseline-verification-v1.json','campaign-closing-integrity-v1.json'],
    '42currentHEADschecked; ownHEAD164ae1f differs from prior campaign7dbc before this run,2340research-only paths explained separately. All42HEADs unchanged during current run; all41external statuses unchanged, including preexisting cocos2d-x changes.')
add('1.02','Recover four root reports and prior evidence rather than assume state',['prior-recovery-integrity-v1.json','root-report-history-preservation-audit-v2.json'],
    'Rootreportsinitiallyabsent; exactpriorarchivebytes restored and append-onlyextended. 2341priorfiles matched again at closing integrity. Original checkpoint history retained; no attribution of interveningHEAD to this campaign.')
add('1.03','Retain historical0/9and0/13 denominators and raw outcomes',['historical-output-failure-audit-v1.json'],
    'All22historicalrawbindingschecked. No rerun, original0/9and0/13unchanged/separate; currentcategorizationusesretainedsemanticreviews and isnotnewindependentadjudication.')
add('1.04','Verify11topics10families22files11of20editorialversions',['manual-population-and-head-reverification-v2.json','campaign-closing-integrity-v1.json'],
    'Counts/statuses/22hashesconfirmed. This is historical editorial population, not11currentstrictpasses. Onlythree selected chapterpairs semanticallyreviewed under current protocol; unselected topics integrity-only.')
add('1.05','Verify305recordsGold0updates0andNO-GO',['dataset-quality-audit-v1.json','campaign-closing-integrity-v1.json','fine-tuning-nine-gate-review-v6.json'],
    'Seven originalfiles unchanged; all305retained,398directrefs match; owner/training/Goldflags0 and no optimization. NinegatesNO_GO.')
add('1.06','Verify versionscaller/planner/retrieval/maintenance',['campaign-closing-integrity-v1.json'],
    'Caller1.9.43,planner0.3.6,retrieval0.1.5,maintenance0.1.5exactdeclarations unchanged.')
add('1.07','Execute approved existing regressions and retain failures',['existing-agent-suite-v1.json','ruby-documentation-suite-v1.json','frontend-existing-suite-summary-v2.json'],
    'ActualexistingPython312pass;Ruby242runs1699assertions0fail/error/skip;frontend102tests100pass2fail. Rawlogsretained. Suites executedonce, no unchangedreruns or permanenttestedits.')
add('2.01','Separate allnineacceptance/approvallayers',['acceptance-protocol-v2.json'],
    'Retrieval,factualsupport,semanticproof,context,lifecycle,bilingual,wholeunit,independentownerapproval,Gold separate. Structure/citations/identifiers alone neverpasssemanticgate.')
add('2.02','Separate manual authoring, neural contribution and historical studies',['acceptance-metric-catalog-v3.json'],
    'Eachmethodretainsrequestedunit/cohort. Kprovidedfactcopy andTmanualtemplates separate fromsource-derivedprose. No pooled generalmodelaccuracy.')
add('3.A.01','Version and freeze atomic reference/provenance fields',['acceptance-protocol-v2.json','atomic-reference-ledger-v2.json','atomic-property-granularity-results-v2.json'],
    '28requiredrelation slots+3unknowncontrols retained; complexslots not28independentatoms. Post-output12singleproperties in6pairs normalizeall14requiredprovenancefields; explicitlynotprospectivebenchmark.')
add('3.A.02','Measure precision, unsupported claims, false support/rejection/abstention',['acceptance-metric-catalog-v3.json','semantic-verifier-label-only-results-v2.json','actual-generated-claim-verifier-results-v1.json'],
    'Selectedgeneratedproposition/pairmetrics andcriticconfusion/rates recorded separately. Correctedlabel-onlyV/R each4/9;negativefalseS4/6vs1/6, RtrueSabstention2/3. StrictfalseS-to-C0/3both doesnot hideRfalseabstentions. Rationale validitynullwhennotrequested. Full95responseproseprecisionnotuniversallymeasured; no invented denominator.')
add('3.A.03','Do not treat bilingual occurrences/composite groups as independentclaims',['atomic-property-granularity-results-v2.json','paired-intervention-tradeoff-audit-v1.json'],
    'Language/excerptoccurrencesattachedtounderlyingclaims; source role wrongentitynotcredited asindependentcorrectparams. Relation-slot coverage/pairclassification/atomicpropertyunits explicitlydifferent.')
add('3.B.01','Report all11dimensions and finalcompleteoutcomes',['complete-document-dimension-index-v1.json','complete-note-dimension-reporting-supplement-v1.json'],
    '11explicitdimensions for34newboundednoteworkflows,3existingselectedownerpairs,23originalpublicpairs,1owned-adapterpair. Overlap/nonindependent; ten reporting-only supplements do not change verdicts. Missingunit0 not false factual proposition; FAQ/claims/copy/critics retain own units.')
add('3.B.02','Critical unsupported fact must block completeacceptance',['acceptance-protocol-v2.json','acceptance-metric-catalog-v3.json'],
    'Allrequiredfacts/bothlanguages/all11applicabledims2/no unreviewedcriticalcontent. C/Zod10/10factcoverage stillfailsfalseFAQ; validJSON doesnotrescueCobra/wrongguards. K3/3copiedfactmixednotes isqualifiedpass, not autonomousdiscovery.')
add('3.C.01','Five lifecycle labels, confusion matrices and separate risks',['lifecycle-matrix-and-rate-audit-v6.json'],
    'ADD/MODIFY/REMOVE/NO-OP/INCONCLUSIVE5x5matrices bycohort/condition;76uniqueownedcases10cohorts plus8historicalcohortsseparate. ADD/NOOPunsupporteddenominatorsnullinnewcohorts; actualconditionavailability preserved.')
add('3.C.02','Independent scope evidence before REMOVE',['scope-retirement-filter-results-v7.json','lifecycle-matrix-and-rate-audit-v6.json'],
    'Declaredcompleteness/selectedabsenceinsufficient. Independentlyacquiredsource stillvulnerableto namespace/lifetimeauthority:V6falseR6/6and4/4;V7blocksallbutretains1/4freshlegitimateR. Finiteprototype, no genericresolver/productionfix.')
add('4.01','Classify original9+13rejections without rerunning',['historical-output-failure-audit-v1.json'],
    'Observablewrongsource/behavior/identifier/language/sections/FAQ/negativeevidence/abstention/truncationmechanismsretained. No capacity/tokenizer/attentionrootcause claimed from outputalone.')
add('4.02','Preserve errors and distinguish operational failures from semantic failure',['inference-error-preservation-supplement-v2.json','current-campaign-inference-ledger-v2.json'],
    '98terminalattempts95returned87normal8length3transportfailures. FirstA500bodyunavailableandnotinvented; latererrorbodiespreserved. Failedtransporthasnowholeoutputsemanticprecisiondenominator.')
add('5.A','Complete bounded document generation',['generation-A-G-comparison-v1.json'],'A0/3requestednotes;2returned,1length,1transportfailure. Not whole-project chapter accuracy.')
add('5.B','Small-section generation and assembly',['generation-A-G-comparison-v1.json'],'B10sectioncalls,0/3assembledrequestednotes; larger/differentper-taskresourcespreventisolatedcausalspeed/accuracyclaim.')
add('5.C','Verified facts followed by bilingualprose',['generation-A-G-comparison-v1.json'],'C0/3completeboundednotes; sourcefacts supplied. C/CobraJSONvalidbutnoactualPTobject; C/ZodfalseextraFAQblocks pass.')
add('5.D','Structuredclaims followed bydeterministicrendering',['generation-A-G-comparison-v1.json'],'D0/3completeclaimsets; eachreturnsfirstfactonly, not completecoverage. Rendererrefuses; no manualfill.')
add('5.E','Source-backed FAQ',['generation-A-G-comparison-v1.json'],'E0/3completeFAQunits; validformatdoesnotfixguard/defined-type/deprecation/gettererrors.')
add('5.F','Separate claimverification beforeassembly',['generation-A-G-comparison-v1.json','semantic-verifier-label-only-results-v2.json'],
    'FreusesexactDoutputs,0newcalls,0/3assemblies. No completefalseDdocumentavailable: whole-docfalseacceptancenegativedenominator0/null. Gateisaseparatecodepath, not independenthumanreview; same-agentsemanticreferences and same-modelcritics cannot certifyGold.')
add('5.G','Explicituncertainty andabstention',['generation-A-G-comparison-v1.json'],'G0/3completeunits; explicitabstentioninstructiondoesnoteliminatewrongscope/guards/missinglanguage. Gdimensionv2retainedcorrection.')
add('5.08','Bounded falsifiable interventions afterA–G',['request-field-difference-audit-v3.json','protocol-freeze-and-exposure-audit-v1.json'],
    '98requestsboundto14protocols,eachrecordedfreezeprecedesstartandhashmatches.38actualrequestcomparisonscheckintendedchanges. K/Lanswerbank+guidance,Psource/guidance/keepalive,W/Xinputrepresentation+localizationnotisolatedinternalcauses.')
add('5.09','Do not tune on evaluation-onlysources or claim independent success',['protocol-freeze-and-exposure-audit-v1.json'],
    'Current31Cobra/39FastAPI/28Zodattempts allDEV-exposed/training-excluded; reservesnotusedascurrentmodeltasks. Historicalcachetoolsdiagnostic meansnotfreshsemanticfamilyholdout. Localtimestampsareprovenance,nottrustedtimestampattestation.')
add('6.01','Selectively use actual corpus withread-onlyexternalrepos',['repository-inspected-files-v2.json','selected-source-git-binding-audit-v1.json','campaign-closing-integrity-v1.json'],
    '14Portfolio publicrepos/69pinnedGitfileidentities,1existingRailsinstalledsourceoutside42.69snapshotSHA256match exactGitblobs/revisions. Other9VivaBemHEAD/statusonly; ownELsource/tests/researchused. Externalrepossem alterações.')
add('6.02','Keep privatecode/data/credentials awayfrommodels/publicreports/training',['protocol-freeze-and-exposure-audit-v1.json','dataset-quality-audit-v1.json'],
    'Private8recordssemanticbodiesexcluded; preserved/hashcheckedopaquelyonly. Noother9privateVivaBembodyreads, no privateDB/credentials/patientaccess, no externalmodels/upload. Onlypinnedpublicsourceinexistinglocalmodelrequests.')
add('6.03','Do not execute upstream apps/tests/installers',['repository-inspected-files-v2.json','selected-source-git-binding-audit-v1.json'],
    'Upstreamsourceparsed/readonly. ExistingELsuitesandownGo/TSobserversprocesscontrols executed; externalprograms/migrations/test suites/installers0.')
add('7.01','Investigate lexical/citationfalseacceptance',['default-role-verifier-protocol-v1.json','cross-language-typed-relations-results-v1.json','typed-template-semantic-boundary-results-v1.json'],
    'Typedowner/roleprofilesdistinguishfiniteS/C/Iclaims;57crosslanguagecontrolledrequests match.24perturbations expose/refuseunsupportedprofiles. Fourvectorcollisionsinclude3semantictemplatecounterexamples; originalsourcepinrejectsall.')
add('7.02','Test stronger identity boundary and itscounterexamples',['owner-capsule-identity-results-v1.json','owner-capsule-dependency-boundary-results-v1.json'],
    '12identitycontrols7match5differ,allfrozenexpectationsmet; detects3knownbodychangeswhilekeepingcomments/unselectededits. Twofurtherbindingchangeskeepowneridentitybutinvalidatebehavior; stilloriginalhashmismatches. Identitynotsemanticproof.')
add('7.03','InvestigatecachedGohelperexception/jobseam',['cached-helper-job-seam-results-v1.json','job-process-interruption-results-v1.json'],
    '20baseline/wrapperobservations;3knowncachedSubprocessError becomeaccountednon-successinresearchwrapperwithouthelperretry/cachemodification.8actualchildstops+2journalforksdemonstrateREFUSED/UNKNOWN/body-integritylimits.')
add('7.04','Investigate atomicpublication without touchingproduction',['atomic-publication-process-results-v1.json','atomic-publication-alias-and-scope-supplement-v1.json'],
    '15singleprocesscases+2racers,allfrozenexpectationsmet; unchangedactualwrite_newempty/partialfinalvsownedstagedlinkabsent/full. Existingfile/symlinkrefused;onewinner,noraceoverwrite;allstagesretained. Notpowerloss/Windows/multifilejobrecovery. Archivesdonotpreservehardlinkaliasgraphs; originalgraphreceiptretained.')
add('7.05','Precise fixes, files, risks and expectedregressions, unapplied',['proposed-fixes-for-owner-review-v5.json'],
    'Semanticadmission,cachedhelper/job/delivery,independentREMOVEauthorityproposalshashexactsourceandexistingtestpaths. Proposedtextclarificationsandnativeapprovalchecklistseparate; no production/permanenttest/UI/schema/internaldocedits.')
add('8.01','Read/reviewthreeexistingbilingualchapterpairs andthreeFAQpairs',['owner-review-package-v3.json','owner-whole-prose-and-provenance-review-v3.json','owner-citation-physical-integrity-v3.json'],
    'Actual6chaptertexts/3FAQpairs againstsource/test-source/provenance.116selectedsourcepropsand76physicalcitationrangeschecked, notuniversalproseprecision. FastAPI/Cobrasource-onlypass;Zodreviewer-independencewordingclarification;3FAQpairsboundedcorrect.')
add('8.02','Provide ownerreviewpackage/rights/uncertainties withoutpromotion',['owner-review-package-v3.json'],
    'Coverage/sources/verification/uncertainty/proposedwording/rightsconditions explicit. Sameagentseparatequerypathisnotindependentreviewer. OWNER_APPROVED/Gold0, no catalogpublication.')
add('8.03','Audit expanded originalcandidatepopulation byrole',['original-public-chapter-body-review-results-v2.json','original-remaining-candidate-reference-review-results-v1.json'],
    '23publicchapterpairs20source-onlypass/3revision;69publicFAQpairsreviewedseparately.12ownedadapterrows source-onlyreview,24syntheticlifecycleconsistentwithdeclaredpremises,9stdlib6FOUND/3INCONCLUSIVE.229auditedDEVcandidate/referencerowsnot229approvedsemanticexamples.')
add('9.01','Reassess allninegates and compatiblebasemodel/tokenizer',['fine-tuning-nine-gate-review-v6.json','native-candidate-metadata-readiness-review-v1.json','runtime-identity-closure-v1.json'],
    'AllnineNO_GO. ExistingOllamaGGUFdigestunchangednotmatchednativetrainablebase. OneunselectedMLXcandidatepinnedmetadataonly; weights/tokenizeractualbytes/nativeexecutionnotvalidated.')
add('9.02','Supervision, masking, tokenization and512fit',['native-real-target-mask-results-v2.json','pilot-supervision-approval-contract-v2.json'],
    'Sourcearithmeticcanaryshowspositivesource_ntoksmaycountpaddingonly; promptprefix/template/date/EOS/pad/actualassistanttargetsnotverified. Noactualapprovedtokenizer/examples/native512fit. Proposedceilingunchanged.')
add('9.03','Framework/AppleSilicon/hardwarefeasibility',['native-release-and-dependency-readiness-review-v1.json','runtime-identity-closure-v1.json'],
    'Wheel/dependency/sourcecompatibilitymetadataonly; sixnativepackagesnondiscoverableinobservedPython3.14.7. M1Pro16GiBnotmemory/throughputproof. DockerOOMhistorynotnativebenchmark; containerstillrunning/sameStartedAt.')
add('9.04','Targetselection andnativeadapter/checkpointrecovery',['native-target-selection-metadata-results-v1.json','pilot-supervision-approval-contract-v2.json'],
    '8virtualselectorcasesexposezero/negative-layerallselection andfull-key/emptymatchhazards. CurrentGit/releasedloaderdifferencesexplicit. No actualtrainableinventory/adapter/optimizer/scheduler/step/RNGrestore. Ordinaryresearchrecoveryisnotnativecheckpointrecovery.')
add('9.05','Keep16/1/1/512/rank4/QV/600s/1800sceiling andexplicitapproval',['pilot-supervision-approval-contract-v2.json'],
    'Allceilingsretainedunvalidated. Sameunadaptednativebase/frozenpairedsemanticcomparison required; postfinal-updateevalnotin-looppreupdatevalidation. No launchcommand orauthorizationrequest; install/weights/adapters/updates0.')
add('10.01','Preserve305records, provenance/rights/exclusions/evalassignments',['dataset-quality-audit-v1.json','campaign-closing-integrity-v1.json'],
    '293DEV+12TEST_ONLY,42lineages,398immutableMATCH,8privateexcluded,56diagnosticnotcorrecttargets,allapprovals/Gold0. Originalrecords/revisions/languages/prompts/rejections unchanged.')
add('10.02','Prevent derivative/related-familycontamination',['dataset-provenance-graph-results-v2.json','public-dependency-relatedness-review-v1.json','protocol-freeze-and-exposure-audit-v1.json'],
    '17strongcomponents1310strongedges;555shared-envelopeedgeskeptweak,separate. FastAPIdeclaresStarlettedependency; repositorynamealonecannotproveindependence. Currentdevelopmentrequestsandderivativesexcludedfromholdout/training. No blanketsemanticindependencecertification.')
add('10.03','Preserve historicalresearch/weights/checkpoints withoutdeletion',['recovery-checkpoint-014.json','foundation-colocated-recovery-checkpoint-013-v1.json','restricted-preservation-directory-modes-v1.json'],
    'Alloldcutsretained;nohistoricalbytesdeleted/rewritten.420foundationalinputsrestored/hash+modeverifiedcolocated; currentrestrictedP/Bdirectories0700. No newweights/adapters.')
add('11.01','Approximately eighthourssubstantiveresearch withadaptivecontinuation',['campaign-state-v16.json'],
    'ACTIVEfrom13:27:15.678298UTC aftertwoexplicitownerpause/resumes. Finalduration/preservationpending; target~21:34UTC. No artificialsleep/meaninglessrerun. Exactproductive/pausedurationnotinstrumented; serversecondsnotwalltime.',
    'PENDING_FINAL_TIME_AND_COMPLETION_RECEIPT')
add('12.01','Report confirmedprocessgain withoutfabricatedmodelimprovement',['acceptance-metric-catalog-v3.json','paired-intervention-tradeoff-audit-v1.json','owner-capsule-dependency-boundary-results-v1.json'],
    'K3/3provided-factmixednotes/X9/9providedlines/T2/2manualnotes preservepositiveboundaries; source-derivedL/M/P/Qwhole0,criticsunsafe. Factualgates/explicitinvalidation/recoveryimproveprocess only. No weightchange/generalcapacityproof.')
add('13.01','Exactlyfourcanonicalhumanreports, append-onlyhistory',['root-report-append-v15.json','root-report-history-preservation-audit-v2.json'],
    'Onlyfourauthorizedcanonicalrootreports; technicalJSON/scripts/rawoutputsunderagentresearch. Allhistoricalpreimagesretained. Latestfinalappend/historyaudit/inventory/checkpoint stillpending.',
    'PENDING_FINAL_CANONICAL_CUT_AND_PRESERVATION')
add('14.01','No production/permanenttest/UI/schema/internaldoc/Git/externalwrites',['campaign-closing-integrity-v1.json','proposed-fixes-for-owner-review-v5.json'],
    'Emptytracked/stageddiffs,unchangedindex/HEAD andexternalstatuses; createdownfourreports/technicalresearchonly. No staging/commits/push/reset/clean/rebase/stash/historywrite, publication, frameworkinstall, weightdownload oroptimization.')
add('15.01','Finalstart/end/timing,metrics,tests,defects,recovery,approval,nextstep',['acceptance-metric-catalog-v3.json','remaining-defects-and-boundaries-v1.json','proposed-fixes-for-owner-review-v5.json'],
    'Evidencecatalogcompletewithexplicitlimits; finalfourrootconsolidations/endtimestamps andclosingcompletionreceiptpending.',
    'PENDING_FINAL_HUMAN_REPORTS_AND_COMPLETION_RECEIPT')
add('15.02','Perrepositorycreated/modified/deleted/inspectedfiles,purpose,commands,outcomes',['repository-inspected-files-v2.json','selected-source-git-binding-audit-v1.json','file-inventory-v13.json'],
    '42repositorydispositions,70selectedsourceidentitieswithpurposes/actualverificationcommands; technicalper-fileSHA/purposeinventoryandfourrootpre/posthashreceipts. Externalrepossem alterações. Finalnewartifactinventorycutpending.',
    'PENDING_FINAL_NEW_ARTIFACT_INVENTORY_CUT')
add('15.03','Bilingual ConventionalCommit suggestions only, no Gitwrite',['campaign-closing-integrity-v1.json'],
    'FinalresponsemustuseexactProjeto/EnglishandProjeto/Portuguêsblocks forengineering-libraryonly. Suggestionsmustnotbeexecuted.',
    'PENDING_FINAL_RESPONSE_FORMAT')

result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authorized_request_sha256':hashlib.sha256((P/'authorized-request.txt').read_bytes()).hexdigest(),
        'scope':'Requirementcoverageauditofauthorizedresearchcampaign,notclaimthateverygatesucceeded/genericverifierimplemented/allresponseprosefullyatomized.',
        'items':rows,'requirements':len(rows),'status_counts':{status:sum(r['status']==status for r in rows)for status in sorted({r['status']for r in rows})},
        'final_campaign_completion_asserted':False,'remaining_work':'Finishactualduration,finalfourreports/historyverification,finalfileinventory/checkpoint/completionreceiptandfinalresponse. Do not replay inference or unchanged suites.',
        'research_limitations_not_hidden':['No independenthumanownerapproval/Gold.','No completeautonomouschapterorweightimprovementdemonstrated.','No universallyexhaustiveatomicprecisionforall95returnedproseoutputs.','No genericsemantic/lifecycleverifierorfullnativecheckpointvalidation.','No clean-clone/remote/powerloss/Windowsrestoreproof.'],
        'gold':0,'optimizer_updates':0}
with(P/'requirement-coverage-audit-v1.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps({k:v for k,v in result.items()if k!='items'},indent=2))
