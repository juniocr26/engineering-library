"""Bounded Go AST syntax-to-prose profile. Does not execute inspected source."""
import json
import sys

PROFILE = 'go-sole-return-syntax-v1'


def inline(text):
    if not isinstance(text, str) or not text or len(text) > 700 or any(c in text for c in '`\r\n\0'):
        raise ValueError('unsupported code expression for a bounded prose span')
    return '`' + text + '`'


def describe(contract, lang, depth=0):
    if not isinstance(contract, dict) or depth > 2:
        raise ValueError('unit outside sole-return syntax profile')
    if contract.get('kind') == 'sole-return-expressions':
        expressions = contract.get('expressions')
        if not isinstance(expressions, list) or not 1 <= len(expressions) <= 4:
            raise ValueError('invalid sole-return expressions')
        joined = ', '.join(inline(expr) for expr in expressions)
        return ('Its sole body statement is a return with these expressions in source order: ' + joined + '. ' if lang == 'en' else
                'Seu corpo consiste em uma instrução de retorno com estas expressões na ordem da fonte: ' + joined + '. ')
    if contract.get('kind') == 'sole-return-function-literal':
        signature = inline(contract.get('literal_signature'))
        text = ('Its sole body statement returns a function literal with syntax ' + signature + '. Returning this literal does not execute its body. ' if lang == 'en' else
                'Seu corpo consiste em uma instrução que retorna uma função literal com a sintaxe ' + signature + '. Retornar esse literal não executa seu corpo. ')
        if contract.get('callback_body_analyzed') is True:
            nested = describe(contract.get('callback_contract'), lang, depth + 1)
            text += ('For that returned function: ' if lang == 'en' else 'Para essa função retornada: ') + nested
        elif contract.get('callback_body_analyzed') is False:
            text += ('That callback body is outside this profile and remains unanalyzed. ' if lang == 'en' else
                     'O corpo desse callback está fora deste perfil e permanece sem análise. ')
        else:
            raise ValueError('missing callback analysis boundary')
        return text
    raise ValueError('unsupported return contract kind')


def render(unit, lang):
    symbol = inline(unit.get('symbol'))
    signature = inline(unit.get('function_type'))
    text = (symbol + ' has the declaration syntax ' + signature + '. ' if lang == 'en' else
            symbol + ' tem a sintaxe de declaração ' + signature + '. ')
    if unit.get('receiver_type'):
        text += ('Its receiver type is written as ' if lang == 'en' else 'O tipo de seu receptor está escrito como ') + inline(unit['receiver_type']) + '. '
    text += describe(unit.get('return_contract'), lang)
    text += ('These are syntax facts only: imports and types were not resolved; helper behavior, normal completion and runtime safety were not verified.' if lang == 'en' else
             'São apenas fatos sintáticos: importações e tipos não foram resolvidos; comportamento de auxiliares, conclusão normal e segurança em execução não foram verificados.')
    if not 20 <= len(text) <= 1600:
        raise ValueError('source explanation exceeds paragraph limit')
    return text


if __name__ == '__main__':
    try:
        unit = json.load(sys.stdin)
        print(json.dumps({'profile': PROFILE, 'explanations': {lang: render(unit, lang) for lang in ['en', 'pt-br']}, 'model_inference': False}, ensure_ascii=False))
    except (ValueError, TypeError, KeyError) as error:
        print(json.dumps({'profile': PROFILE, 'reason': str(error)}))
        sys.exit(2)
