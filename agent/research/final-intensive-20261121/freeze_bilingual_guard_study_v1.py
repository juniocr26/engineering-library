"""Freeze development-only screening controls before executing the screen."""
import json,hashlib,datetime
from pathlib import Path
p=Path(__file__).resolve().parent;source=p/'source-claim-reacquisition-results-v1.json';rows=json.loads(source.read_text())['claims'];by={r['claim_id']:r for r in rows};cases=[]
def add(ident,claim,pt,category,semantic):
 r=by[claim];cases.append({'id':ident,'claim_id':claim,'en':r['expected_interpretation']['en'],'pt-BR':pt,'category':category,'manual_reference_pair_equivalence':semantic,'source_bound_reference':r,'reference_method':'Same-agent comparison to prior exact source-grounded proposition; not independent human labels.'})
for c in ('F07','C02','Z03'):
 add(c+'-intact',c,by[c]['expected_interpretation']['pt-BR'],'INTACT',True)
add('F07-negation-drop','F07','A condição selecionada de escrita testa use_cache.','NEGATION_CHANGE',False)
add('F07-valid-paraphrase','F07','A condição selecionada de escrita deixa de testar use_cache.','VALID_PARAPHRASE',True)
add('C02-condition-inversion','C02','OnlyValidArgs faz a validação de pertencimento somente dentro de len(cmd.ValidArgs) == 0.','CONDITION_OPERATOR_CHANGE',False)
add('C02-identifier-change','C02','OnlyValidArgs faz a validação de pertencimento somente dentro de len(cmd.Args) > 0.','IDENTIFIER_CHANGE',False)
add('C02-condition-erasure','C02','OnlyValidArgs faz a validação de pertencimento em todas as chamadas, independentemente da configuração.','CONDITION_ERASURE',False)
add('Z03-wrong-action','Z03','A arrow síncrona retorna explicitamente core.$ZodAsyncError sob result instanceof Promise.','ACTION_SEMANTIC_BLIND',False)
add('Z03-valid-word-order','Z03','Sob result instanceof Promise, a arrow síncrona lança explicitamente core.$ZodAsyncError.','VALID_PARAPHRASE',True)
# A second false pair with unchanged symbols and negation demonstrates an intentionally unaddressed semantic layer.
add('F07-wrong-subject','F07','A condição selecionada de leitura não testa use_cache.','SUBJECT_SEMANTIC_BLIND',False)
protocol={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hypothesis':'A bounded lexical bilingual guard can flag selected negation/condition/identifier changes but cannot certify action/subject equivalence and can reject valid paraphrases.','reference_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'cases':cases,'frozen_policy':{'identifiers':{'F07':['use_cache'],'C02':['OnlyValidArgs','len(cmd.ValidArgs) > 0'],'Z03':['core.$ZodAsyncError','result instanceof Promise']},'en_negation_pattern':r'\b(?:not|never|no)\b','pt_negation_pattern':r'\b(?:não|nunca|sem)\b','condition_policy':'Exact registered condition expression is an identifier-like protected literal, not a Boolean solver.','verdict':'FLAG if any protected literal missing from either language or negation-presence differs; otherwise SCREEN_CLEAR, never semantic PASS.'},'population':'11 owned, correlated development controls from three previously exposed proposition pairs; never train/eval holdout.','prohibited_claims':['No semantic FAR/FRR or independent bilingual accuracy estimate.','No production integration, Gold, publication or model improvement.'],'model_calls':0}
with (p/'bilingual-guard-study-protocol-v1.json').open('x') as f:json.dump(protocol,f,indent=2,ensure_ascii=False);f.write('\n')
print('Frozen 11 cases; no screen executed')
