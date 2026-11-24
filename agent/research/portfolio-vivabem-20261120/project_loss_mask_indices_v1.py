"""Pure owned index arithmetic; never imports or executes the MLX framework."""
from pathlib import Path
import datetime
import hashlib
import json

P=Path(__file__).resolve().parent
protocol=P/'owned-loss-mask-index-protocol-v1.json'
data=json.loads(protocol.read_text())
results=[]
for case in data['frozen_cases']:
    n=case['original_length']
    offset=case['offset']
    cap=case['max_sequence']
    width=min(1+32*((n+31)//32),cap)
    retained=min(n,cap)
    # Source-derived index predicate; not execution of default_loss or batching.
    selected=[j for j in range(1,width) if offset<=j<=retained]
    # Independently defined real causal targets exclude positions beyond tokens.
    real=[j for j in range(1,retained) if j>=offset]
    original=[j for j in range(1,n) if j>=offset]
    padding=[j for j in selected if j>=retained]
    lost=[j for j in original if j not in real]
    assert selected==case['expected_source_positions']
    assert real==case['expected_real_target_positions']
    synthetic_tokens=list(range(100,100+n))
    padded=synthetic_tokens[:retained]+[0]*(width-retained)
    results.append({'id':case['id'],'original_length':n,'offset':offset,'max_sequence':cap,'projected_batch_width':width,'retained_length':retained,'source_mask_positions':selected,'real_valid_target_positions':real,'padding_positions_admitted_by_source_predicate':padding,'selected_target_token_ids':[padded[j] for j in selected],'projected_ntoks':len(selected),'real_supervised_token_count':len(real),'original_target_positions_lost':lost,'whole_original_target_preserved':not lost,'positive_count_but_only_padding':bool(selected) and not real,'zero_denominator_possible_if_this_shape_reaches_selected_default_loss':len(selected)==0,'matches_frozen_hand_oracles':True,'not_actual_tokenizer_or_framework_result':True})
report={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':hashlib.sha256(protocol.read_bytes()).hexdigest(),'method':'Owned Python integer/index projection only;source batching/loss functions,MLX,model,tokenizer and optimizer not executed.','cases':results,'scope':'Six handpicked conditions,not a framework failure rate or actual training/NaN observation. Source predicate versus real-token target oracle are kept distinct.','projection_checks':{'numerator':6,'denominator':6},'framework_imports':0,'framework_functions_executed':0,'optimizer_steps':0,'owner_approved':False,'training_eligible':False}
out=P/'owned-loss-mask-index-observations-v1.json'
assert not out.exists()
out.write_text(json.dumps(report,indent=2)+'\n')
for row in results:
    print(row['id'],'source_count',row['projected_ntoks'],'real_count',row['real_supervised_token_count'],'padding',row['padding_positions_admitted_by_source_predicate'],'lost',len(row['original_target_positions_lost']))
