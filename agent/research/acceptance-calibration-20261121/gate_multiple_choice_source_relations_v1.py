"""Research-only finite reference gate and deterministic manual-prose renderer."""
from pathlib import Path
import json,hashlib,datetime,argparse
from frozen_schema_subset_v2 import unique_object,validate
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def frozen():
 protocol=json.loads((P/'multiple-choice-source-relations-protocol-v1.json').read_text());raw=(P/protocol['references']).read_bytes();assert sha(raw)==protocol['references_sha256'];reference=json.loads(raw);lr=(P/'atomic-reference-ledger-v2.json').read_bytes();assert sha(lr)==reference['reference_ledger_sha256'];ledger={r['claim_id']:r for r in json.loads(lr)['claims']};return protocol,reference,ledger

def evaluate(task,raw):
 protocol,reference,ledger=frozen();item=next(c for c in protocol['calls'] if c['task']==task);request=ROOT/item['request'];assert sha(request.read_bytes())==item['request_sha256'];schema=json.loads(request.read_text())['format'];reasons=[];predicted=None
 try:
  predicted=json.loads(raw,object_pairs_hook=unique_object);errors=validate(predicted,schema)
  if errors:reasons.append({'schema_errors':errors})
 except (ValueError,TypeError) as exc:reasons.append({'parse_error':type(exc).__name__})
 expected=reference['by_task'][task];comparisons=[]
 if predicted is not None and not reasons:
  for cid,correct in expected['expected'].items():
   actual=predicted['relations'][cid];comparisons.append({'id':cid,'original_relation':actual,'expected_relation':correct,'correct':actual==correct,'kind':'SCOPE_UNKNOWN' if cid==expected['unknown_id'] else 'SOURCE_RELATION'})
   if actual!=correct:reasons.append({'incorrect_relation':cid})
 sources=[]
 for cid in expected['required_source_ids']:
  r=ledger[cid];f=P/'frozen-public-sources'/task/r['source_path'];rawsource=f.read_bytes();assert sha(rawsource)==r['source_file_sha256'];lines=rawsource.decode().splitlines();assert '\n'.join(lines[r['source_lines'][0]-1:r['source_lines'][1]])==r['exact_source_evidence'];sources.append({'id':cid,'path':r['source_path'],'sha256':sha(rawsource),'source_lines':r['source_lines'],'source_revision':r['source_revision']})
 return {'accepted':not reasons,'reasons':reasons,'comparisons':comparisons,'sources':sources,'input_sha256':sha(raw.encode() if isinstance(raw,str) else raw)}

def render(task,decision):
 assert decision['accepted'];protocol,reference,ledger=frozen();meta=protocol['manual_metadata'][task];output={}
 for lang in ['en','pt-BR']:
  parts=[meta['scope'][lang],meta['error_boundaries'][lang]]
  for cid in reference['by_task'][task]['required_source_ids']:
   r=ledger[cid];parts.append(cid+': '+r['expected_interpretation'][lang]);parts.append('Source: '+r['source_path']+':'+str(r['source_lines'])+' @ '+r['source_revision'])
  parts.extend([meta['faq_question'][lang],ledger[meta['faq_fact_id']]['expected_interpretation'][lang],meta['limitations'][lang]])
  output[lang]='\n\n'.join(parts)+'\n'
 return output

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--task',choices=['fastapi','cobra','zod'],required=True);args=parser.parse_args();task=args.task;folder=P/'multiple-choice-source-relations-v1'/task/'Q';outcome=json.loads((folder/'outcome.json').read_text());assert outcome['exit_code']==0 and outcome['done_reason']=='stop' and outcome.get('content_json_valid');raw=(folder/'model-content.txt').read_bytes();decision=evaluate(task,raw);result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'task':task,'method':'Q','gate_decision':decision,'status':'ASSEMBLED_PENDING_COMPLETE_DIMENSION_REVIEW' if decision['accepted'] else 'REFUSED_INCORRECT_OR_INCOMPLETE_RELATION','neural_role':'Selects normalized source relations from finite alternatives; no bilingual prose authored by model','prose_role':'Manually source-reviewed reference facts and manually frozen metadata; deterministic renderer only. Not repaired/generated model prose or fact discovery.','owner_approved':False,'training_gold':False,'optimizer_updates':0}
 if decision['accepted']:result['notes']=render(task,decision)
 with (folder/'reference-gate-and-render-v1.json').open('x') as f:json.dump(result,f,indent=2,ensure_ascii=False);f.write('\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ['notes','gate_decision']},indent=2))
