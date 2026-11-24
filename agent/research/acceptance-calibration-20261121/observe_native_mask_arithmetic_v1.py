"""Owned integer equations only. No MLX/numpy/tokenizer import or upstream execution."""
import datetime,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
protocol=json.loads((HERE/'native-mask-arithmetic-protocol-v1.json').read_text());rows=[]
for case in protocol['owned_cases']:
 length=case['sequence_length'];cap=case['max_seq_length'];offset=case['prompt_offset'];width=min(1+32*((length+31)//32),cap);effective=min(length,cap)
 supervised=[pos for pos in range(1,width) if offset<=pos<=effective];padding=[pos for pos in supervised if pos>=length];real_completion=list(range(max(1,offset),length));missing=[pos for pos in real_completion if pos not in supervised];row={'id':case['id'],'batch_width':width,'effective_length':effective,'supervised_target_global_positions':supervised,'padding_target_global_positions':padding,'missing_real_completion_positions':missing,'supervised_token_count':len(supervised),'zero_loss_denominator':not supervised,'matches_frozen_arithmetic_reference':supervised==case['expected_supervised_positions'] and padding==case['expected_pad_positions_supervised'] and missing==case['expected_missing_real_completion_positions'],'actual_framework_executed':False};rows.append(row)
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':'native-mask-arithmetic-protocol-v1.json','records':rows,'arithmetic_reference_matches':sum(r['matches_frozen_arithmetic_reference'] for r in rows),'cases':len(rows),'finding':'Under the selectedsourceequations shortpaddedexamples includeonezero-padding target; fullcapexampledoesnot. Truncationcanomitcompletion/EOS oryieldzero supervisedtokens. Thisisnot nativeMLXruntimevalidation anddoesnot prove futuretokenizer-boundaryaccuracy.','no_upstream_code_executed':True,'no_framework_installed_or_imported':True,'no_actual_dataset_exported':True,'no_weights_or_adapters_created':True,'optimizer_updates':0,'gold':0}
with (HERE/'native-mask-arithmetic-results-v1.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
