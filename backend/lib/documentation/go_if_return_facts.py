"""Bounded Go if-return/fallthrough syntax; no type/helper/runtime inference."""
import json,sys
from go_return_facts import inline,describe
PROFILE='go-if-return-fallthrough-syntax-v2'


def render_chain(unit, contract, lang):
 if not isinstance(contract,dict):raise ValueError('ordered guard-chain object required')
 guards=contract.get('guards')
 if (not isinstance(guards,list) or not 2<=len(guards)<=3
     or contract.get('kind')!='if-return-chain-fallthrough-expressions'
     or contract.get('source_statement_order')!=['if-return']*len(guards)+['return']
     or contract.get('types_resolved') is not False
     or contract.get('runtime_completion_verified') is not False):
  raise ValueError('outside bounded ordered guard-chain profile')
 symbol=inline(unit.get('symbol'));signature=inline(unit.get('function_type'))
 text=(symbol+' has declaration syntax '+signature+'. ' if lang=='en' else
       symbol+' tem sintaxe de declaração '+signature+'. ')
 if unit.get('receiver_type'):
  text+=('Its receiver type is written as ' if lang=='en' else 'O tipo de seu receptor está escrito como ')+inline(unit['receiver_type'])+'. '
 text+=('The body contains ordered if-return guards followed by one final return. ' if lang=='en' else
        'O corpo contém guardas if-return ordenadas, seguidas de um retorno final. ')
 prior_line=unit.get('start_line')
 end_line=unit.get('end_line')
 if type(prior_line) is not int or type(end_line) is not int:
  raise ValueError('missing source range')
 for index,guard in enumerate(guards):
  if (not isinstance(guard,dict) or guard.get('initializer_absent') is not True
      or guard.get('else_absent') is not True or type(guard.get('line')) is not int
      or not prior_line<=guard['line']<=end_line):
   raise ValueError('invalid ordered guard provenance')
  prior_line=guard['line']
  condition=inline(guard.get('condition'));returned=guard.get('true_return_contract')
  if not isinstance(returned,dict) or returned.get('kind')!='sole-return-expressions':
   raise ValueError('guard must have explicit return expressions')
  describe(returned,lang)
  expressions=', '.join(inline(expr) for expr in returned['expressions'])
  if lang=='en':
   text+=('First, ' if index==0 else 'Only if preceding tests complete false, ')
   text+='the source tests '+condition+'; its true branch contains a return with written expressions '+expressions+'. '
  else:
   text+=('Primeiro, ' if index==0 else 'Somente se os testes anteriores terminarem falsos, ')
   text+='a fonte testa '+condition+'; seu ramo verdadeiro contém um retorno com as expressões escritas '+expressions+'. '
 final=contract.get('fallthrough_return_contract')
 if not isinstance(final,dict) or final.get('kind')!='sole-return-expressions':
  raise ValueError('final explicit return required')
 describe(final,lang)
 expressions=', '.join(inline(expr) for expr in final['expressions'])
 text+=('If all tests complete false, the final return has written expressions '+expressions+'. No guard has an initializer or else. Written expressions do not prove name bindings, helper behavior, the number of returned values or normal completion.' if lang=='en' else
        'Se todos os testes terminarem falsos, o retorno final tem as expressões escritas '+expressions+'. Nenhuma guarda tem inicializador ou else. Expressões escritas não provam vínculos de nomes, comportamento de auxiliares, quantidade de valores retornados ou conclusão normal.')
 if not 20<=len(text)<=1600:raise ValueError('bounded paragraph size exceeded')
 return text


def render(unit,lang):
 if unit.get('declaration_kind') not in ['function','method']:raise ValueError('function/method required')
 if unit.get('if_return_chain_contract') is not None:
  return render_chain(unit,unit['if_return_chain_contract'],lang)
 contract=unit.get('if_return_contract')
 if not isinstance(contract,dict) or contract.get('kind')!='if-return-fallthrough-expressions' or contract.get('source_statement_order')!=['if-return','return'] or contract.get('initializer_absent') is not True or contract.get('else_absent') is not True or contract.get('runtime_completion_verified') is not False:raise ValueError('outside bounded if-return/fallthrough profile')
 branches=[]
 for key in ['true_return_contract','fallthrough_return_contract']:
  result=contract.get(key)
  if not isinstance(result,dict) or result.get('kind')!='sole-return-expressions':raise ValueError('bounded explicit return expressions required')
  describe(result,lang);branches.append(', '.join(inline(expr) for expr in result['expressions']))
 condition=inline(contract.get('condition'));symbol=inline(unit.get('symbol'));signature=inline(unit.get('function_type'))
 text=(symbol+' has declaration syntax '+signature+'. ' if lang=='en' else symbol+' tem sintaxe de declaração '+signature+'. ')
 if unit.get('receiver_type'):text+=('Its receiver type is written as ' if lang=='en' else 'O tipo de seu receptor está escrito como ')+inline(unit['receiver_type'])+'. '
 if lang=='en':
  text+='Its body has exactly two statements: an if with condition '+condition+' and a return. The if has no initializer or else. Its true branch contains only a return with these written expressions in source order: '+branches[0]+'. If the test completes false, the following return has these written expressions in source order: '+branches[1]+'. '
  text+='Written expressions do not establish the number of values returned by a helper call. Type validity, helper behavior, side effects and normal runtime completion remain unverified.'
 else:
  text+='Seu corpo tem exatamente duas instruções: um if com condição '+condition+' e um retorno. O if não tem inicializador nem else. Seu ramo verdadeiro contém apenas um retorno com estas expressões escritas na ordem da fonte: '+branches[0]+'. Se o teste terminar falso, o retorno seguinte tem estas expressões escritas na ordem da fonte: '+branches[1]+'. '
  text+='Expressões escritas não estabelecem a quantidade de valores retornados por uma chamada auxiliar. Validade de tipos, comportamento de auxiliares, efeitos colaterais e conclusão normal em execução permanecem sem verificação.'
 if not 20<=len(text)<=1600:raise ValueError('bounded paragraph size exceeded')
 return text
if __name__=='__main__':
 try:
  unit=json.load(sys.stdin);print(json.dumps({'profile':PROFILE,'explanations':{lang:render(unit,lang) for lang in ['en','pt-br']},'model_inference':False},ensure_ascii=False))
 except (ValueError,TypeError,KeyError) as error:
  print(json.dumps({'profile':PROFILE,'reason':str(error)}));sys.exit(2)
