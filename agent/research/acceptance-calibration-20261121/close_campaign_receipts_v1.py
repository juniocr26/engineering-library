"""Close only after final reports, inventory and actual checkpoint restoration exist."""
from pathlib import Path
from collections import Counter
import datetime,hashlib,json,os,stat
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
B=ROOT/'.local-backups/acceptance-calibration-20261121'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(name):return json.loads((P/name).read_text())
def write(name,data):
 with(P/name).open('x')as stream:json.dump(data,stream,indent=2,ensure_ascii=False);stream.write('\n')
 return {'path':str((P/name).relative_to(ROOT)),'sha256':sha(P/name)}
cut=read('root-report-final-cut-v1.json')
integrity=read('campaign-closing-integrity-v2.json')
history=read('root-report-history-preservation-audit-v3.json')
inventory=read('file-inventory-v15.json')
recovery=read('recovery-checkpoint-016.json')
assert history['all_historical_bytes_are_current_prefixes']and history['all_successive_versions_append_only']
assert history['available_append_receipt_hash_checks_all_match']
assert recovery['common_file_members_restored_and_verified']>2792
assert recovery['regular_file_modes_preserved_and_verified']and not recovery['open_worker_files_excluded']
assert recovery['owned_parser_restored_replay']['exact_original_observer_output_reproduced']
assert recovery['owned_identity_parser_restored_replay']['exact_original_observer_output_reproduced']
assert sha(ROOT/recovery['archive'])==recovery['archive_sha256']
assert sha(ROOT/recovery['manifest'])==recovery['manifest_sha256']
assert sha(ROOT/recovery['restricted_supporting_archive'])==recovery['restricted_supporting_archive_sha256']
assert stat.S_IMODE((ROOT/recovery['archive']).stat().st_mode)==0o600
assert stat.S_IMODE((ROOT/recovery['restricted_supporting_archive']).stat().st_mode)==0o600
assert stat.S_IMODE((ROOT/recovery['archive']).parent.stat().st_mode)==0o700
assert stat.S_IMODE(P.stat().st_mode)==stat.S_IMODE(B.stat().st_mode)==0o700
assert not inventory['open_worker_files']
assert all(integrity[k]for k in ['all_heads_unchanged_since_current_campaign_start','all_41_external_statuses_unchanged','all_commands_successful','git_index_matches_start','all_input_hashes_match','all_versions_match'])
assert sha(ROOT/'.git/index')==integrity['git_index_sha256']
assert integrity['own_tracked_diff']['stdout']==integrity['own_staged_diff']['stdout']==''
assert read('current-campaign-inference-ledger-v2.json')['active_started_without_terminal']==0
assert set(read('fine-tuning-nine-gate-review-v7.json')['all_nine_gates'].values())=={'NO_GO'}
inventory_reports={row['path']:row for row in inventory['canonical_root_reports']}
manifest=json.loads((ROOT/recovery['manifest']).read_text())
manifest_rows={r['path']:r for r in manifest['files']}
reports=[]
for row in cut['reports']:
 path=ROOT/row['path'];observed=sha(path)
 assert observed==row['post_sha256']==inventory_reports[row['path']]['sha256']==manifest_rows[row['path']]['sha256']
 lines=path.read_text().splitlines();assert lines[row['final_section_start_line']-1].startswith('## Fechamento da pesquisa')
 reports.append({'path':row['path'],'sha256':observed,'bytes':path.stat().st_size,
                 'final_section_start_line':row['final_section_start_line'],
                 'matches_final_report_cut_inventory_and_restored_archive':True})
assert len(reports)==4
colocated=read('final-colocated-source-recovery-v1.json')
assert colocated['combined_distinct_selected_inputs']==431
assert len(colocated['restored_own_module_import_observation']['module_paths'])==6
now=datetime.datetime.now(datetime.timezone.utc)
start=datetime.datetime.fromisoformat('2026-11-21T13:27:15.678298+00:00')
wall=(now-start).total_seconds()
assert wall>=8*3600,'Do not close before approximately eight elapsed hours; continue authorized substantive work, never sleep/fill.'
defects=read('remaining-defects-and-boundaries-v2.json')
defects['extends']='remaining-defects-and-boundaries-v2.json';defects['prior_sha256']=sha(P/defects['extends']);defects['at']=now.isoformat()
for item in defects['items']:
 if item['id']=='TIME-AND-FINALIZATION':
  item['status']='RESEARCH_CAMPAIGN_COMPLETE_VERIFIED'
  item['observable_finding']='Finalcanonicalreportcut/inventory/actualcheckpoint016restorationverified; allstartedrequests terminal. Endtimeandwallintervalincompletionreceipt. Thisclosesexecution/preservationonly; production/research/native/rights/frontendlimitsremain.'
  item['evidence']=[{'path':name,'sha256':sha(P/name)}for name in ['root-report-final-cut-v1.json','file-inventory-v15.json','recovery-checkpoint-016.json','root-report-history-preservation-audit-v3.json']]
defects['time_item_still_active_until_final_receipt']=False
defects['no_production_defects_automatically_closed']=True
defect_ref=write('remaining-defects-and-boundaries-v3.json',defects)
audit=read('requirement-coverage-audit-v1.json');audit['extends']='requirement-coverage-audit-v1.json';audit['prior_sha256']=sha(P/audit['extends']);audit['at']=now.isoformat()
current={'acceptance-metric-catalog-v3.json':'acceptance-metric-catalog-v5.json',
 'lifecycle-matrix-and-rate-audit-v6.json':'lifecycle-matrix-and-rate-audit-v8.json',
 'fine-tuning-nine-gate-review-v6.json':'fine-tuning-nine-gate-review-v7.json',
 'proposed-fixes-for-owner-review-v5.json':'proposed-fixes-for-owner-review-v6.json',
 'remaining-defects-and-boundaries-v1.json':'remaining-defects-and-boundaries-v3.json',
 'campaign-closing-integrity-v1.json':'campaign-closing-integrity-v2.json',
 'file-inventory-v13.json':'file-inventory-v15.json',
 'root-report-history-preservation-audit-v2.json':'root-report-history-preservation-audit-v3.json',
 'root-report-append-v15.json':'root-report-append-v17.json',
 'recovery-checkpoint-014.json':'recovery-checkpoint-016.json'}
for item in audit['items']:
 for ref in item['evidence']:
  original=Path(ref['path']).name
  if original in current:
   name=current[original];ref['path']=str((P/name).relative_to(ROOT));ref['sha256']=sha(P/name)
 if item['id']=='10.03':item['observed_outcome']+=' Final16colocates420foundationinputsand13ownsource/testsnapshotswith2matches/nooverwrite:431distinctselectedinputs,6restoredownmodulesimported,noruntimehelper/suitererun/fulltransitiveclaim.'
 if item['id']=='3.C.01':item['observed_outcome']='84uniqueownedcases11cohorts85currentmatrices/ratesrecomputed;8historicalcohortsseparate. V1availability18,V4=46,othercurrentconditions84; no fabricatedpredictions/pooledaccuracy.'
 if item['id']=='3.C.02':item['observed_outcome']+=' NewV7reachabilityfalseR4/4;V8blocksall4butkeeps1/4freshlegitR,loses4additionalpriorlegitR. Genericremovalproofnotachieved.'
 if item['id']=='11.01':
  item['status']='EXECUTION_COMPLETED_WITH_TIMING_LIMITS';item['observed_outcome']=f'Actualstart{start.isoformat()},researchend{cut["research_end_utc"]},preservationend{now.isoformat()},wall{wall:.6f}s.Twoownerpause/resumeevents,exactproductive/pausedurationnotinstrumented; prior12hnotcounted, no artificialsleep.'
 elif item['id']=='13.01':
  item['status']='FINAL_CANONICAL_REPORTS_PRESERVED_AND_VERIFIED';item['observed_outcome']='Exactlyfourcanonicalrootreports,finalappendv17and68preimagesverifiedasappend-onlyprefixes; finalhashesmatchinventory15/archive016.'
 elif item['id']=='15.01':
  item['status']='FINAL_REPORTS_AND_RECOVERY_VERIFIED';item['observed_outcome']='Fourcanonicalreportscontainresults/limits/tests/defects/approval/nextstep; actualresearchtimeincut, laterpreservationtimeandclosureincompletionreceipt. Researchlimitsnotmistakenforproduction/nativefixes.'
 elif item['id']=='15.02':
  item['status']='FINAL_FILE_INVENTORY_AND_REPOSITORY_DISPOSITIONS_VERIFIED';item['observed_outcome']='42repositorydispositions/69Git-pinnedclonefiles+1installedRailsidentity/13ownselectedexistingpaths,per-filepurpose/hash/commandsinfinalinventory15. External41statusesunchanged,tracked/stageddiffsempty/indexunchanged. Lateclosurereceiptslistedoutsideownarchivewithredundantcopies.'
 elif item['id']=='15.03':
  item['status']='FINAL_RESPONSE_FORMAT_PREPARED_FOR_DELIVERY';item['observed_outcome']='ExactProjeto/EnglishandProjeto/Portuguêsblocks forengineering-libraryprepared; no commitexecuted. Finalmessageitselfisdelivery,notlocallyattestedbeforeitissent.'
audit['status_counts']=dict(Counter(r['status']for r in audit['items']))
audit['final_campaign_completion_asserted']=True
audit['remaining_work']='Finaluserresponsedeliveryonly; allauthorizedresearch/preservationworkclosed. Technicaldefects/approvals/nativegatesremainexplicitlyunresolved/outsidecurrentimplementationauthorization.'
audit['closing_evidence']=[{'path':name,'sha256':sha(P/name)}for name in ['root-report-final-cut-v1.json','file-inventory-v15.json','recovery-checkpoint-016.json','root-report-history-preservation-audit-v3.json','own-selected-inspected-files-v1.json','lifecycle-matrix-and-rate-audit-v8.json','future-first-learning-task-proposal-v1.json']]
audit_ref=write('requirement-coverage-audit-v2.json',audit)
state={'at':now.isoformat(),'status':'COMPLETE_VERIFIED','campaign_start_utc':start.isoformat(),
       'research_end_utc':cut['research_end_utc'],'preservation_end_utc':now.isoformat(),
       'active_inference_workers':0,'terminal_inference_attempts':98,'latest_verified_checkpoint':16,
       'canonical_report_count':4,'fine_tuning':'NO_GO_ALL_NINE','owner_approved':0,'gold':0,'optimizer_updates':0,
       'completion_receipt':'campaign-completion-receipt-v1.json','restart_or_autoreplay_authorized':False}
state_ref=write('campaign-state-v19.json',state)
late=[defect_ref,audit_ref,state_ref]+[{'path':str((P/name).relative_to(ROOT)),'sha256':sha(P/name)}for name in ['foundation-colocated-recovery-checkpoint-016-v1.json','final-colocated-source-recovery-v1.json']]
receipt={'at':now.isoformat(),'status':'COMPLETE_VERIFIED','objective':'Authorizedapproximatelyeight-hourdocumentationacceptanceresearchcampaign; notproductionfixes/neuraltraining/Goldapproval.',
 'campaign_start_utc':start.isoformat(),'research_end_utc':cut['research_end_utc'],
 'final_checkpoint_restored_at':recovery['at'],'preservation_end_utc':now.isoformat(),
 'elapsed_wall_seconds_to_research_end':cut['research_elapsed_wall_seconds'],'elapsed_wall_seconds_to_preservation_end':wall,
 'owner_pause_resume_events':2,'productive_time_limit':'Exactproductive/pausedurationnotinstrumented; serviceactive-timeobservationsandserversecondsarenotCPUfocusmeasurements. Approximateeight-hourcampaign,priorcampaign12hnotcounted.',
 'canonical_reports':reports,'final_inventory':{'path':'file-inventory-v15.json','sha256':sha(P/'file-inventory-v15.json'),'regular_technical_files_at_cut':inventory['technical_file_count'],'symlinks_at_cut':inventory['technical_symlink_count']},
 'final_checkpoint':recovery,'final_checkpoint_receipt_sha256':sha(P/'recovery-checkpoint-016.json'),
 'colocated_selected_inputs':{'path':'final-colocated-source-recovery-v1.json','sha256':sha(P/'final-colocated-source-recovery-v1.json'),'distinct_inputs':431,'restored_own_modules_imported':6},
 'root_history':{'path':'root-report-history-preservation-audit-v3.json','sha256':sha(P/'root-report-history-preservation-audit-v3.json'),'preimages':history['preserved_root_preimages'],'all_prefixes_and_available_hashes_match':True},
 'late_closure_evidence_outside_final_archive':late,
 'self_cut':'Inventoryexcludesitself/laterwrites. Checkpointreceipt/manifestareoutsideownarchivewithredundantcopies. Thiscompletionreceipt,finalaudit/defect/stateandclosureindexwrittenafterrestoreareoutsidefinalarchiveandcopiedredundantlyunderrestrictedB. Indexbindscompletionreceipthash; no self-hash/infiniteclosureclaim.',
 'protected_integrity':{'path':'campaign-closing-integrity-v2.json','sha256':sha(P/'campaign-closing-integrity-v2.json'),'repository_count':42,'external_repositories_unchanged':41,'index_sha256':integrity['git_index_sha256'],'tracked_and_staged_diffs_empty':True,'datasets':7,'records':305,'immutable_references':398,'prior_preserved_files':2341,'manual_docs':22},
 'inference':{'attempts':98,'returned':95,'normal':87,'length':8,'transport_failures':3,'active':0,'not_general_accuracy':True},
 'tests':{'python_pass':312,'ruby_runs_pass':242,'ruby_assertions':1699,'frontend_pass':100,'frontend_total':102,'frontend_failures':2,'unchanged_suites_rerun':False},
 'limits':['Same-agentsemanticreviewnotindependenthumanapproval.','No exhaustivewhole-proseatomicprecisionforall95responses.','No autonomouscompletechapterorweightimprovementdemonstrated.','No genericsource/lifecycleverifierorproductionfix.','No cleanclone/remote/powerloss/Windows/nativeadapterfullstaterecovery.'],
 'git_writes':0,'external_mutations':0,'framework_installations':0,'weights_downloaded':0,'adapters_created':0,'optimizer_updates':0,'owner_approved':0,'gold':0}
receipt_ref=write('campaign-completion-receipt-v1.json',receipt)
for name in ['remaining-defects-and-boundaries-v3.json','requirement-coverage-audit-v2.json','campaign-state-v19.json','campaign-completion-receipt-v1.json','foundation-colocated-recovery-checkpoint-016-v1.json','final-colocated-source-recovery-v1.json']:
 destination=B/('final-'+name)
 with destination.open('xb')as stream:stream.write((P/name).read_bytes())
 os.chmod(destination,0o600);assert sha(destination)==sha(P/name)
index={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'FINAL_CLOSURE_INDEX','completion_receipt':receipt_ref,
       'late_evidence':late,'canonical_reports':reports,'redundant_copies_verified':True,
       'index_self_hash_not_embedded':True,'scope':'Indexanditsredundantcopyarelastclosurefiles,outsideownhash/archive. No furthercanonicalreportwriteplanned.','gold':0,'optimizer_updates':0}
write('final-closure-index-v1.json',index)
destination=B/'final-closure-index-v1.json'
with destination.open('xb')as stream:stream.write((P/'final-closure-index-v1.json').read_bytes())
os.chmod(destination,0o600);assert sha(destination)==sha(P/'final-closure-index-v1.json')
print(json.dumps({'status':receipt['status'],'campaign_start_utc':receipt['campaign_start_utc'],
 'research_end_utc':receipt['research_end_utc'],'preservation_end_utc':receipt['preservation_end_utc'],
 'wall_seconds':wall,'reports':reports,'checkpoint_archive_sha256':recovery['archive_sha256'],
 'completion_receipt_sha256':receipt_ref['sha256'],'requirements_statuses':audit['status_counts']},indent=2))
