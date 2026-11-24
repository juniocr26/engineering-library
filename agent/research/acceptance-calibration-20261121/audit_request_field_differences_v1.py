"""Audit actual request differences; no inference or reference edits."""
from pathlib import Path
import json,hashlib,datetime
P=Path(__file__).resolve().parent
pairs=[]
for task in ['fastapi','cobra','zod']:
 for label,a,b,allowed in [('A_vs_G',f'generation-v1/{task}/A',f'generation-v1/{task}/G',['messages']),('A_vs_H',f'generation-v1/{task}/A',f'schema-comparison-v1/{task}/H',['format']),('C_vs_J',f'generation-v1/{task}/C',f'schema-comparison-v1/{task}/J',['format']),('K_vs_L',f'verified-fact-render-v1/{task}/K',f'source-only-fact-render-v1/{task}/L',['messages'])]:pairs.append((label,task,a,b,allowed))
pairs.extend([('L_vs_M','cobra','source-only-fact-render-v1/cobra/L','source-question-repair-v1/cobra/M',['messages']),('L_vs_P','fastapi','source-only-fact-render-v1/fastapi/L','mechanical-source-prose-v1/fastapi/P',['messages','keep_alive'])])
for top in ['actual-generated-claim-verifier-v1','semantic-verifier-label-only-v2']:
 for folder in sorted((P/top).iterdir()):
  if folder.is_dir():pairs.append((top+'_V_vs_R',folder.name,str(folder.relative_to(P))+'/V',str(folder.relative_to(P))+'/R',['messages']))
for method,allowed in [('USER_REVERSED',['messages']),('SCHEMA_REVERSED',['format']),('BOTH_REVERSED',['messages','format'])]:pairs.append(('Q_vs_'+method,'fastapi','multiple-choice-source-relations-v1/fastapi/Q','relation-option-order-v1/fastapi/'+method,allowed))
def differences(a,b,prefix='$'):
 if type(a)!=type(b):return [prefix]
 if isinstance(a,dict):
  result=[]
  for k in sorted(set(a)|set(b)):
   if k not in a or k not in b:result.append(prefix+'.'+k)
   else:result.extend(differences(a[k],b[k],prefix+'.'+k))
  return result
 if isinstance(a,list):
  if len(a)!=len(b):return [prefix+'.length']
  return [p for i,(x,y) in enumerate(zip(a,b)) for p in differences(x,y,prefix+'['+str(i)+']')]
 return [] if a==b else [prefix]
def payload(message):
 for part in reversed(message.split('\n\n')):
  try:
   value=json.loads(part)
   if isinstance(value,dict):return value
  except (ValueError,TypeError):pass
 return None
rows=[]
for label,task,a,b,allowed in pairs:
 fa=P/a/'request.json';fb=P/b/'request.json';ra=json.loads(fa.read_text());rb=json.loads(fb.read_text());changed=sorted(k for k in set(ra)|set(rb) if ra.get(k)!=rb.get(k));pa=payload(ra['messages'][-1]['content']);pb=payload(rb['messages'][-1]['content']);payloadchanges=differences(pa,pb) if pa is not None and pb is not None else None
 row={'comparison':label,'task_or_case':task,'left':str(fa),'right':str(fb),'left_sha256':hashlib.sha256(fa.read_bytes()).hexdigest(),'right_sha256':hashlib.sha256(fb.read_bytes()).hexdigest(),'changed_top_level_fields':changed,'expected_changed_top_level_fields':sorted(allowed),'matches_expected_top_level_intervention':changed==sorted(allowed),'exact_field_differences':differences(ra,rb),'payload_field_differences':payloadchanges,'same_model':ra['model']==rb['model'],'same_options':ra['options']==rb['options'],'same_keep_alive':ra.get('keep_alive')==rb.get('keep_alive'),'same_response_schema':ra['format']==rb['format'],'same_source_cards_if_both_present':pa['source_cards']==pb['source_cards'] if pa and pb and 'source_cards' in pa and 'source_cards' in pb else None}
 rows.append(row)
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':rows,'comparisons':len(rows),'all_expected_top_level_interventions_match':all(r['matches_expected_top_level_intervention'] for r in rows),'interpretation':['A/H andC/J change only responseformat in all3tasks; A/Gchangesonly user instruction while pinnedpayload/options/schema stayequal.','K/Lchanges answerbank availability and prompting; equal resources/sourcecards/schema doesnot isolate factbank removal from instruction changes.','L/MchangesC01question only in payload, not source/options/schema. No acceptedcompleteMnote and otheranswersalsochange.','L/Pchanges prompt/source representation/questionwording andkeep_alive; no single-cause ASTassistance effect claimed.','Within each actual/label V/Rpair, source/claims/options/schema are matched and verifier instruction differs; across criticstudies, resources/schema/sourceheaders differ, so no pooled causal gain.','Qordering contrast isolatesuseralternatives/schemaenumorder as frozen; singlefamily/cell, no repeated unchangedbaseline.','Exactfield equality is an input-design check, not outputsemantic correctness, global causal accuracy, deterministic hardware replay or independent evaluation.'],'source_or_model_execution':False,'reference_answers_changed':False,'gold':0,'optimizer_updates':0}
with (P/'request-field-difference-audit-v1.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'comparisons':len(rows),'all_expected_fields_match':result['all_expected_top_level_interventions_match'],'L_M':[x['payload_field_differences'] for x in rows if x['comparison']=='L_vs_M'],'L_P':[x['payload_field_differences'] for x in rows if x['comparison']=='L_vs_P'],'unexpected':[x for x in rows if not x['matches_expected_top_level_intervention']]},indent=2))
