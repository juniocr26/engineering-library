"""Private source syntax renderer; no mutex/type or runtime behavior inference."""
import sys,json
from pathlib import Path
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
from go_return_facts import inline,describe
PROFILE='go-call-defer-return-syntax-v1'
def render(unit,lang):
 if unit.get('declaration_kind') not in ['function','method']:raise ValueError('function/method required')
 contract=unit.get('deferred_return_contract')
 if not isinstance(contract,dict) or contract.get('kind')!='call-defer-return-expressions' or contract.get('source_statement_order')!=['call','defer','return'] or contract.get('type_or_mutex_behavior_verified') is not False or contract.get('runtime_completion_verified') is not False or contract.get('defer_is_not_an_immediate_call') is not True:raise ValueError('outside bounded call/defer/return profile')
 nested=contract.get('return_contract')
 if not isinstance(nested,dict) or nested.get('kind')!='sole-return-expressions':raise ValueError('bounded return expressions required')
 # Reuse verified inline/expression validation, never its sole-body wording.
 describe(nested,lang)
 symbol=inline(unit.get('symbol'));signature=inline(unit.get('function_type'))
 text=(symbol+' has declaration syntax '+signature+'. ' if lang=='en' else symbol+' tem sintaxe de declaração '+signature+'. ')
 if unit.get('receiver_type'):text+=('Its receiver type is written as ' if lang=='en' else 'O tipo de seu receptor está escrito como ')+inline(unit['receiver_type'])+'. '
 expressions=', '.join(inline(expr) for expr in nested['expressions'])
 if lang=='en':
  text+='Its body has exactly three statements in written order: call '+inline(contract.get('call'))+'; defer '+inline(contract.get('deferred_call'))+'; return with these expressions in source order: '+expressions+'. '
  text+='This records written statement order; the deferred invocation is not an immediate second invocation. Operand evaluation, helper behavior, imports/types, normal completion, concurrency safety and runtime effects remain unverified.'
 else:
  text+='Seu corpo tem exatamente três instruções na ordem escrita: chamada '+inline(contract.get('call'))+'; defer '+inline(contract.get('deferred_call'))+'; retorno com estas expressões na ordem da fonte: '+expressions+'. '
  text+='Isso registra a ordem escrita das instruções; a invocação adiada não é uma segunda invocação imediata. Avaliação dos operandos, comportamento de auxiliares, importações/tipos, conclusão normal, segurança de concorrência e efeitos em execução permanecem sem verificação.'
 if not 20<=len(text)<=1600:raise ValueError('bounded paragraph size exceeded')
 return text
if __name__=='__main__':
 try:
  unit=json.load(sys.stdin);print(json.dumps({'profile':PROFILE,'explanations':{lang:render(unit,lang) for lang in ['en','pt-br']},'model_inference':False},ensure_ascii=False))
 except (ValueError,TypeError,KeyError) as error:
  print(json.dumps({'profile':PROFILE,'reason':str(error)}));sys.exit(2)
