import json,hashlib,datetime
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[2];sha=lambda b:hashlib.sha256(b).hexdigest();old=p/'repository-exposure-matrix-v4.json';d=json.loads(old.read_text());ledger_path=p/'repository-action-ledger-v20.json';ledger=json.loads(ledger_path.read_text());by={r['repository']:r for r in ledger['records']};counts={'current_campaign_source_path_acquisition_records':0,'metadata_only_records':0,'private_external_metadata_only':0}
for row in d['records']:
 record=by[row['repository']];paths=record['source_paths_acquired_for_selected_scope_review'];own=row['repository']=='engineering-library';isprivate=row['current_role'].startswith('PRIVATE_')
 if isprivate:assert not paths and not record.get('private_source_body_read');counts['private_external_metadata_only']+=1
 row['legacy_catalog_metadata_only_now_scope']='Catalogmetadata lookup performed byoldmatrixbuilder, not a claim the entirecampaignneverreadsource. Fieldretainedasdatedlegacyobservation.'
 row['current_campaign_metadata_only']=not bool(paths) and not own
 row['current_campaign_selected_source_paths']=list(paths)
 row['current_campaign_source_scope']='Selectedpublicsourceacquisition/referencepreparationorownresearchreinspection; not wholefilesemanticcoverage, not localmodelinference.' if paths or own else 'No currentselectedsourceacquisitioninledger; privatepolicy/earlierexposure/unresolvedstatus retained.'
 row['current_action_ledger']={'path':str(ledger_path.relative_to(root)),'sha256':sha(ledger_path.read_bytes())}
 row['current_local_model_source_delivery_confirmed']=False
 if row['current_campaign_metadata_only']:counts['metadata_only_records']+=1
 else:counts['current_campaign_source_path_acquisition_records']+=1
 if 'PROSPECTIVE_EVALUATION_ONLY' in row['current_role']:row['evaluation_scope_clarification']='Task/referencepreparationhasinspectedsource; stillEVALONLYNOTRUN, no independenthuman/model/pretrainingcertification andno trainingeligibility.'
 if own:row['own_internal_source_review']='Datedfullagentchapter/helpercontractsandhistoricalsource/receiptsread; bothacceptedinternalpairsareownfamilyDEV, no independentholdout.'
assert len(d['records'])==42 and counts['private_external_metadata_only']==9
extras=[('tkem/cachetools','EXPOSED_REAL_REVISION_DEVELOPMENT_AND_TEST_ONLY_STRUCTURAL','agent-contracts-additional-source-receipt-closure-v1.json','Eightphysicalquotationscurrentreview; original12TEST_ONLY_STRUCTURALrowsremainquarantined, realrevisiontasksnotindependentneuralholdout.'),('Python installed standard library','HASH_PINNED_EXISTING_STDLIB_DEVELOPMENT_CONTEXT','agent-contracts-additional-source-receipt-closure-v1.json','Exactcontextlib/decoderbytesfrominstalled3.14.7historicalcopies; no CPythonGitidentityoreverytargetcontaminationinferred.'),('rails/rails installed actionpack8.1.4','PUBLIC_INSTALLED_DEPENDENCY_STATIC_CHAPTER_CONTEXT','rails-request-complete-review-v2.json','InstalledRubypublicsource/Ripperparse only, notRailsframeworkruntimeornewGitcheckout.'),('golang/x/net/httpguts vendored SDK snapshot','PROVISIONAL_EVALUATION_ONLY_UPSTREAM_IDENTITY_INCONCLUSIVE','go-vendored-httpguts-upstream-identity-query-observations-v1.json','LocalexactvendoredbytesandAPIexposureknown; inaccessibleupstreammetadataquerydoesnotestablishfullcommit/byteequivalence/independence.')]
# Locate exact historical query receipt name without inventing an upstream identity.
for i,(family,role,receipt,limit) in enumerate(extras):
 if not (p/receipt).is_file() and family.startswith('golang/x/net'):
  candidates=sorted(p.glob('go-vendored-httpguts-upstream*json'));assert candidates
  receipt=next((f.name for f in candidates if 'observ' in f.name or 'result' in f.name),candidates[0].name)
 f=p/receipt;assert f.is_file();d['external_public_families_without_local_checkout'].append({'family':family,'role':role,'receipt':receipt,'receipt_sha256':sha(f.read_bytes()),'scope':limit,'current_manual_reinspection_not_new_model':True,'no_new_local_model_delivery':True,'training_eligible':False,'independent_evaluation_certified':False})
d.update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),extends={'path':str(old.relative_to(root)),'sha256':sha(old.read_bytes())},current_exposure_observation_counts=counts,refinement='Historicalroles/metadatafieldretained; currentcampaignsourceusageexplicitlyboundledger20, withadditionalpublicdependencyfamilies. Newnameoroldmetadataonlyfieldisnotcertifiedindependence.',certified_independent_families=0,new_model_calls=0,optimizer_updates=0,gold=0)
with (p/'repository-exposure-matrix-v5.json').open('x') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'repositories':42,**counts,'certified_independent_families':0,'outside42_entries':len(d['external_public_families_without_local_checkout'])}))
