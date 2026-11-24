"""Owned metadata/integer projections only; never imports or executes nativeframework."""
from pathlib import Path
import json,hashlib,datetime
P=Path(__file__).resolve().parent
protocol_path=P/'native-target-selection-metadata-protocol-v1.json';r=json.loads(protocol_path.read_text());assert hashlib.sha256(Path(r['source']).read_bytes()).hexdigest()==r['source_sha256'];model=r['virtual_model_metadata'];rows=[];layers=list(range(model['layer_count']));local=model['per_layer_linear_module_names'];allnames={i:['model.layers.'+str(i)+'.'+name for name in local] for i in layers}
for c in r['cases']:
 keys=set(local) if c['keys'] is None else set(c['keys']);selected=[];events=[]
 for i in layers[-max(c['num_layers'],0):]:
  for name in local:
   if name in keys:events.append({'loop':'per_selected_layer_relative_key','full_name':'model.layers.'+str(i)+'.'+name,'layer':i});selected.append((i,'model.layers.'+str(i)+'.'+name))
 for i in layers:
  for name in allnames[i]:
   if name in keys:events.append({'loop':'whole_model_full_key','full_name':name,'layer':i});selected.append((i,name))
 unique=sorted({name for i,name in selected});actual_layers=sorted({i for i,name in selected});matched=len(unique)==c['expected_selected_unique_modules'] and actual_layers==c['expected_layer_ids'];rows.append({'id':c['id'],'num_layers':c['num_layers'],'keys':c['keys'],'selected_unique_full_names':unique,'selected_layer_ids':actual_layers,'loop_events':events,'matches_frozen_reference':matched,'unknown_key_validation_performed':False,'actual_native_module_conversion':False})
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':protocol_path.name,'protocol_sha256':hashlib.sha256(protocol_path.read_bytes()).hexdigest(),'records':rows,'cases':len(rows),'matches':sum(x['matches_frozen_reference'] for x in rows),'finding':'Relative keys follow final-layer slicing, but zero/negative means all in this helper source. Full qualified names are also selected in a separate wholemodel loop, so num_layers is not a universal intersection restriction. Empty/unmatched sets yield zero selections in this projection with no selector validation in those loops. Future preflight must compare exact expected and actual trainable inventories, not just rank/layercount/keys fields.','limitations':r['limits'],'native_framework_imports':0,'tensors_or_adapters_created':0,'gold':0,'optimizer_updates':0}
with (P/'native-target-selection-metadata-results-v1.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
mp=P/'native-real-target-mask-protocol-v2.json';r=json.loads(mp.read_text());assert hashlib.sha256(Path(r['source']).read_bytes()).hexdigest()==r['source_sha256'];rows=[]
for c in r['cases']:
 length,offset,cap=c['length'],c['offset'],c['max_sequence_length'];width=min(1+32*((length+31)//32),cap);effective=min(length,cap);positions=[i for i in range(1,width) if offset<=i<=effective];real=[i for i in range(1,width) if offset<=i<effective];padding=[i for i in positions if i>=effective];matched=positions==c['expected_source_supervised_positions'] and real==c['expected_real_assistant_positions'];rows.append({'id':c['id'],'batch_width':width,'effective_length':effective,'source_supervised_positions':positions,'real_assistant_positions':real,'padding_positions_counted_by_source_mask':padding,'source_ntoks_positive':bool(positions),'real_assistant_token_count':len(real),'matches_frozen_reference':matched})
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':mp.name,'protocol_sha256':hashlib.sha256(mp.read_bytes()).hexdigest(),'records':rows,'cases':len(rows),'matches':sum(x['matches_frozen_reference'] for x in rows),'finding':'The short offset-at-end case has1source-masktoken but0realassistanttokens; positive ntoks alone is not sufficient. Actual approved-tokenizer prefix/assistant boundaries, shift, EOS and padding must be audited. No native execution or actualexample tokenization.','actual_framework_or_tokenizer_executed':False,'actual_training_examples_created':0,'gold':0,'optimizer_updates':0}
with (P/'native-real-target-mask-results-v2.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({'selector_cases':8,'selector_matches':sum(x['matches_frozen_reference'] for x in json.loads((P/'native-target-selection-metadata-results-v1.json').read_text())['records']),'mask_records':rows},indent=2))
