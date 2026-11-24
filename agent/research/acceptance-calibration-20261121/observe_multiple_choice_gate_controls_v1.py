"""Finite owned payload observations; no permanent tests, model calls or training data."""
from pathlib import Path
import json,datetime,hashlib
from gate_multiple_choice_source_relations_v1 import frozen,evaluate
P=Path(__file__).resolve().parent;protocol,reference,_=frozen();planned=[]
for task in ['fastapi','cobra','zod']:
 expected=reference['by_task'][task]['expected'];base={'relations':expected}
 planned.append({'id':task+'-complete-correct','task':task,'payload':json.dumps(base),'expected_admission':True})
 for cid,correct in expected.items():
  choices=reference['by_task'][task]['questions'][cid]['allowed_relations'];wrong=next(c for c in choices if c!=correct);d={'relations':{**expected,cid:wrong}};planned.append({'id':task+'-wrong-'+cid,'task':task,'payload':json.dumps(d),'expected_admission':False})
 missing=dict(expected);missing.pop(next(iter(missing)));planned.append({'id':task+'-missing','task':task,'payload':json.dumps({'relations':missing}),'expected_admission':False})
 planned.append({'id':task+'-extra','task':task,'payload':json.dumps({'relations':{**expected,'EXTRA':'UNKNOWN'}}),'expected_admission':False})
 cid=next(iter(expected));duplicate='{"relations":'+json.dumps(expected)[:-1]+','+json.dumps(cid)+':'+json.dumps(expected[cid])+'}}';planned.append({'id':task+'-duplicate-key','task':task,'payload':duplicate,'expected_admission':False})
freeze={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'before_control_observations_and_Qpredictions':True,'gate_sha256':hashlib.sha256((P/'gate_multiple_choice_source_relations_v1.py').read_bytes()).hexdigest(),'cases':planned,'limits':'Owned exact/mutated payload gate observations only; not independent public-source semantic certification, inference predictions, general language verification or permanent regression suite.'}
with (P/'multiple-choice-reference-gate-control-freeze-v1.json').open('x') as f:json.dump(freeze,f,indent=2);f.write('\n')
rows=[]
for case in planned:
 result=evaluate(case['task'],case['payload']);rows.append({'id':case['id'],'reference':case['expected_admission'],'observed':result['accepted'],'matched':case['expected_admission']==result['accepted'],'reasons':result['reasons']})
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cases':rows,'count':len(rows),'all_match':all(r['matched'] for r in rows),'new_model_calls':0,'notes_materialized':0,'gold':0,'optimizer_updates':0}
with (P/'multiple-choice-reference-gate-control-results-v1.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in result.items() if k!='cases'}));assert result['all_match']
