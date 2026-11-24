from pathlib import Path
import json,hashlib,datetime,re
p=Path(__file__).resolve().parent;root=p.parents[2];sha=lambda b:hashlib.sha256(b).hexdigest();pre=json.loads((p/'prometheus-original-targets-preflight-v1.json').read_text());deps={};obs=json.loads((p/'prometheus-targets-source-binding-observations-v1.json').read_text())
def dep(f):deps[str(f.relative_to(root))]=sha(f.read_bytes())
for n in ['prometheus-original-targets-preflight-v1.json','prometheus-targets-source-protocol-v1.json','prometheus-targets-source-binding-observations-v1.json','prometheus-targets-syntax-observations-v1.json','prometheus-variant-path-discovery-v1.json','prometheus-builder-historical-origins-v1.json','prometheus-keep-original-target-review-v1.json','prometheus-keep-attribution-correction-v1.json']:dep(p/n)
for v in [1,2]:
 f=p/f'prometheus-targets-source-acquisition-v{v}.json';dep(f);d=json.loads(f.read_text())
 for e in d['records']:
  if e['exit_code']==0:
   f=root/e['saved_path'];assert sha(f.read_bytes())==e['sha256'];dep(f)
 if 'installed_dependency' in d:dep(root/d['installed_dependency']['saved_path'])
for e in json.loads((p/'prometheus-builder-historical-origins-v1.json').read_text())['records']:
 for a in e['artifacts']:dep(root/a['path'])
b=root/'agent/research/acceptance-calibration-20261121/original-public-chapter-provenance-captures-v1/prometheus-keep-bookkeeping'
for n in ['origin.json','raw-response.json','model-content.txt','recorded-request.json']:dep(b/n)
for t in pre['topics']:
 for e in t['files']:dep(root/e['path']);dep(root/e['original_path'])
groups={
'prometheus-builder':[
('B01','Set v empty delegates and returns Delresult, not n empty or existingbase','Wrongguard/continueafterhelper: refused'),('B02','Firstmatching pendingadd value updated,returnb; elseappendLabel andreturnb','Directbasesearch/sort or return omitted: refused'),('B03','Del suppliednames order, rangedadd slice removalexpression,appenddel regardlessmatch','Dedupdeletionrequests or guarantee allmalformedduplicate states safe: refused'),('B04','No args Del skipsouter andreturnsb; Setnonempty doesnotremove delmarkers','No immediatebase/db deletion ormarkerpurge'),('B05','Get additionsfirst thendel thenbase; Range copiedadd/del thenfilteredbase andoriginaladd','Universalcurrentbase mutation orcallback writes changealreadycopiedstate: refused'),('B06','Actualcallersonly writerexit1 missingselectedname, helperexit0 citesS1only noDel/return','Structuralacceptance notfullcontract improvement; callerreturncorrectfact preserved'),('B07','Threebuildvariants/sourcefields reviewed, defaulttag notproofusedruntime; LabelName/Value strings','Globalbackend/concurrency/alloc/nil/slicevalidity guarantees refused'),('B08','OriginalENPT/3FAQs/source semantics andApache notice match','Manualchapter notneural orpublication/Gold')],
'prometheus-keep-bookkeeping':[
('K01','ns variadicstring names,inclusion true callbackreturn; nonmatchappenddel','Namespace registry or providednames deleted: unsupported'),('K02','Callbackbare return notouterreturn; afterbaseRange normalcompletion returnb','Oneincludedlabel terminatestraversal/returnsnewbuilder/bool: refused'),('K03','Old delmarkers preserved, no dedup/clear/add/base assignment','Includedname restoresoldmarker orfiltersallpendingadd: refused'),('K04','Emptyname list Indexreturns-1/Containsfalse understandardcontract; duplicate suppliedname notextracallback','Emptylistkeepsallbase orduplicatescauseextratraversal: refused'),('K05','Get additionsprecedence; copiedRange basefilterthenadditions','Bookkeeping equalsallfinalmaterialization withoutbuildvariant: refused'),('K06','Actualbaseline unsupportednamespace andmissinginclusion, callback/outerreturn; presentwording notexplicitnsbinding','Originalreversal attributionFAILpreserved; correctedonesentence/language saysomission'),('K07','Full originalFAQ/sourcecontract retained; correctionexactdiff nootherprose/code changes','Not reduced/easierdocument, not erasedfailure'),('K08','RelevantbaseRangevariants callbackvoid vsValidateerrorreturn, field/type/buildguards inspected','Nopanic/concurrency/alloc/performance/globalvalidity notcertified'),('K09','CompleteENPT/3FAQs meanings andcode/IDs matched','Sameagentmanualreview notindependenthuman orneuralgain')]}
for t in pre['topics']:
 topic=t['topic'];docs=[]
 if topic=='prometheus-builder':
  for i,e in enumerate(t['files'][:2]):docs.append({'language':['en','pt-br'][i],'path':e['path'],'sha256':e['sha256'],'readable_original_path':e['original_path']})
  version='original_dataset_target';outname='prometheus-builder-complete-review-v1.json'
 else:
  docs=json.loads((p/'prometheus-keep-attribution-correction-v1.json').read_text())['documents'];version='separate_complete_attribution_correction_v1';outname='prometheus-keep-corrected-complete-review-v1.json'
  for e in docs:dep(root/e['path'])
  dep(p/'prometheus-keep-attribution-candidate-v1/source-excerpts.json')
 texts=[(root/e['path']).read_text() for e in docs];codes=lambda t:re.findall(r'(?<!`)`([^`\n]+)`(?!`)',t);ids=lambda t:re.findall(r'<!-- reading-section: faq:([^ ]+) -->',t);assert codes(texts[0])==codes(texts[1]);assert ids(texts[0])==ids(texts[1]) and len(ids(texts[0]))==3
 gates={g:{'status':'PASS','basis':v} for g,v in zip(['G1','G2','G3','G4','G5','G6','G7','G8'],['ExactGitpin/sourcebytes/originalranges/candidatehashes andhistoricalresponseidentities','FullENPT/FAQs/source/historicalattributionreview; originalKeepFAILseparatefromcorrectedpair','Selectedmethods/caller/lookup/range/type/buildvariant/dependencycontext covered, no actualruntimevariant claim','Fulloriginalrequirementsretained; correctedpair onlyoneattributionsentence/language','ExistingGo1.27gofmt4fullfiles0diagnostics,ownedbadsyntaxrefused; noimports/type/build/targetruntime','CompleteENPT predicates/negations/IDs/FAQ matched pluscodeparity','NOOPoriginalfixedpinBuilder; MODIFYmanualattributionforcorrectedKeep only,notapplicationorupstreamlifecycle','SeparateGit/span/history/syntaxprocedures andadversemannualgroups; sameagentnotindependenthuman'])};gates['G9']={'status':'INCONCLUSIVE','basis':'Actualnewconsumerrecoverypending'}
 d={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'topic':topic,'version':version,'documents':docs,'gates':gates,'technical_status':'INCONCLUSIVE_RECOVERY_PENDING','authorship':'Manual Codex chapter, not current neural output','source_claim_groups':[{'id':i,'meaning':m,'adverse_challenge':c,'verdict':'SUPPORTED_SCOPED_STATIC','reviewer':'Same campaign agent'} for i,m,c in groups[topic]],'exact_source_range_bindings':[e for e in obs['bindings'] if e['topic']==topic],'FAQ_ids':ids(texts[0]),'external_dependency_edges':[{'path':k,'sha256':v} for k,v in sorted(deps.items())],'Prometheus_typecheck_build_or_execution':False,'new_model_calls':0,'publication_approved':False,'owner_gold':False,'training_approved':False}
 with (p/outname).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
 print(json.dumps({'topic':topic,'groups':len(groups[topic]),'G1_G8':'PASS','G9':'PENDING'}))
