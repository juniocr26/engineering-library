"""Preserve rubric-based model rejection; no retry and no generated-code execution."""
import collections,datetime,hashlib,json,re,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent;OUT=P/'totalist-model-chapter-v1';outcome=json.loads((OUT/'outcome.json').read_text());raw=json.loads((OUT/'response.json').read_text());content=raw['message']['content']
def strict(pairs):
 d={}
 for k,v in pairs:
  if k in d:raise ValueError('duplicate JSON key')
  d[k]=v
 return d
body=json.loads(content,object_pairs_hook=strict);assert set(body)=={'chapters'}and len(body['chapters'])==2
chapters={r['language']:r['markdown']for r in body['chapters']};assert set(chapters)=={'en','pt-br'}and all(set(r)=={'language','markdown'}for r in body['chapters'])
# Parse only. Never run the generated snippets, their imports or the proposed npm command.
syntax=[]
for language,text in chapters.items():
 snippets=re.findall(r'```(?:javascript|js)\n(.*?)\n```',text,re.S);assert len(snippets)==1
 r=subprocess.run(['docker','exec','-i','engineering-library-frontend-1','node','--input-type=module','--check'],input=snippets[0],text=True,capture_output=True,timeout=30)
 syntax.append({'language':language,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'snippet_sha256':hashlib.sha256(snippets[0].encode()).hexdigest(),'executed':False})
script="""const { promisify } = require('node:util');
(async () => {
 let callbackWasCalled=false;
 const owned=(value,callback)=>{callbackWasCalled=true;callback(null,value);};
 const result=promisify(owned)(7);
 const isPromise=typeof result.then==='function';
 const value=await result;
 console.log(JSON.stringify({node:process.version,inputStyle:'owned error-first callback',returnsPromise:isPromise,observedValue:value,ownedCallbackCalled:callbackWasCalled,totalistImported:false,filesystemAccessed:false}));
})().catch(error=>{process.stderr.write(String(error));process.exitCode=1;});
"""
r=subprocess.run(['docker','exec','engineering-library-frontend-1','node','-e',script],text=True,capture_output=True,timeout=30);assert r.returncode==0,r.stderr;util_observation=json.loads(r.stdout);assert util_observation['returnsPromise']and util_observation['observedValue']==7
criteria=[
 ('complete-two-language-structure','PASS','Two unique languages, valid bounded JSON and requested headings/table/twoFAQ structures are present. Structural completeness does not imply factual acceptance.'),
 ('old-current-export-change','FAIL','Neither chapter explains the earlier default list export versus current named totalist export, despite T8-T10 and explicit task instructions.'),
 ('source-versus-package-artifacts','FAIL','Generated distribution targets, export-map/package-source distinction and unauthenticated artifact status are omitted. Source ID T1 is not included in the model source list.'),
 ('async-sync-return-contract','FAIL','Inputs/Outputs describes a promise return without a synchronous-mode exception; it omits the supplied Promise<void>/void declaration distinction. The default async example calls totalist without await and immediately logs.'),
 ('callback-branch-and-unknowns','PARTIAL','The generic traversal purpose is present; explicit directory-versus-callback branching and symlink/cycle/order/concurrency limits are not established. No positive cycle/order guarantee is attributed to the model.'),
 ('node-requirements-disagreement','PARTIAL','The table copies README async>=8.x and sync>=6.x, but omits the manifest>=6 disagreement and source-versus-tested compatibility distinction.'),
 ('bilingual-identifier-and-meaning','FAIL','The example changes local identifier styles to estilos, contrary to the exact-identifier instruction. Portuguese changes traversal to permissao in outputs/limitations, altering the meaning.'),
 ('examples-and-commands','FAIL','npm run tsc is absent from the pinned package scripts. A copied README output comment is reproduced as example output despite no execution, and the async import is used without await before logging. Both snippets parse, which does not verify these semantics.'),
 ('faq-relevance-and-citations','PARTIAL','The two generic FAQ answers do address their purpose/architecture questions. They omit revision-specific changes and have no question-specific evidence attribution; a flat source-ID list is not claim alignment.'),
 ('unsupported-factual-assertions','FAIL','Both chapters reverse promisify into promises-to-callbacks, contrary to the observed Node utility behavior and official API. Relying on fs to handle errors internally is unsupported by the selected no-catch source. No owner/training/deployment approval was invented.')]
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'REJECTED_FACTUAL_AND_BILINGUAL_CHAPTER','protocol_sha256':hashlib.sha256((OUT/'protocol.json').read_bytes()).hexdigest(),'response_sha256':hashlib.sha256((OUT/'response.json').read_bytes()).hexdigest(),'transport_completed':outcome['done']is True and outcome['done_reason']=='stop','truncated':False,'model_seconds':outcome['model_seconds'],'generated_tokens':outcome['generated_tokens'],'prompt_tokens':outcome['prompt_tokens'],'schema_and_unique_languages_valid':True,'accepted_complete_bilingual_chapter_pairs':0,'requested_complete_bilingual_chapter_pairs':1,'rubric':[{'criterion':id,'status':status,'finding':finding}for id,status,finding in criteria],'rubric_counts':dict(collections.Counter(status for _,status,_ in criteria)),'generated_snippet_static_syntax':syntax,'owned_node_utility_observation':util_observation,'owned_node_observation_script_sha256':hashlib.sha256(script.encode()).hexdigest(),'official_api_reference':'https://nodejs.org/download/release/v22.8.0/docs/api/util.html#utilpromisifyoriginal','official_api_interpretation':'Callback-style function to Promise-returning function, not the inverse; this stable API direction was also observed in the existing Node24 runtime using owned code only.','deterministic_comparator':{'ledger':'totalist-chapter-ledger-v2.json','physical_code_checks':47,'supplemental_receipt':'totalist-chapter-supplemental-verification-v2.json','verified_scope':'Source-reviewed fixed chapter with explicit limits, not automatic full-prose semantic certification or general benchmark accuracy.','comparison_limit':'Same preserved source files; deterministic candidate authored/reviewed by Codex, is longer and has six FAQs versus two. No equal authoring-effort claim, independent human grading or causal neural improvement estimate.'},'source_family':'lukeed/totalist','development_exposed':True,'certified_neural_holdout':False,'totalist_source_imported_or_executed':False,'generated_example_executed':False,'model_command_executed':False,'new_neural_model_calls_during_review':0,'automatic_retry':False,'owner_approved':False,'training_gold':False,'training_use_approved':False,'evaluation_only':True,'manual_review_author':'Codex; no independent human certification'}
with(OUT/'review.json').open('x')as f:f.write(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
with(OUT/'parsed-response.json').open('x')as f:f.write(json.dumps(body,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':record['status'],'criteria_counts':record['rubric_counts'],'complete_pairs_accepted':0,'syntax_exits':[r['exit_code']for r in syntax],'node_utility':util_observation}))
