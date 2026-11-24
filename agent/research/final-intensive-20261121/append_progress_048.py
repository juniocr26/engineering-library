import json
from pathlib import Path
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2]
common='''

### Progresso intensivo 048 — terceira falha de atribuição manual e revisão Redis TTL

A fonte Redis na revisão 1a9eb051aa243f9d0e5a8a8afa6c4801bf52a9fb foi adquirida por Git somente para leitura: expire.c, server.c, server.h e a licença. Os hashes coincidem com os pacotes originais. Foram lidos o predicado, o prefixo e os ramos do chamador, o corpo TTL e quatro wrappers, o getter de snapshot e as declarações relevantes do cabeçalho. O lexer bruto Clang 21 percorreu expire.c, produzindo 6.329 linhas de tokens; isso não é AST, tipagem, build ou execução Redis. As regras de operadores foram conferidas no documento primário WG14 N1570.

O baseline correto do predicado é REDIS-EXPIRED-GUARD, não os estudos distintos de activeExpireCycleTryExpire. A resposta realmente omite a guarda CLIENT_MASTER e os operadores e condições exatos. Porém, ela repete a justificativa como uma ideia de política; não afirma explicitamente que o predicado executa inserção, exclusão ou espera. Também menciona carregamento e papel mestre. O alvo manual original exagerava essas atribuições. Ele foi preservado como FAIL_HISTORICAL_ATTRIBUTION; duas cópias bilíngues completas corrigem somente as duas formulações excessivas em cada língua. Os originais, labels e escores anteriores não foram reescritos.

O capítulo TTL original passou pela revisão de conteúdo sem mudança. A resposta histórica confundiu chamadas de resposta com retorno C e descreveu 500 segundos. A fonte void separa a resposta -2 com saída antecipada, a sentinela -1, a base relativa ou absoluta, o clamp zero e a seleção independente de unidade com (ttl+500)/1000. A afirmação de arredondamento continua limitada ao intervalo aritmético representável, sem garantia de overflow, lookup sem efeitos, relógio novo ou entrega pela rede. Quatro linhas de tabela e três FAQs conferem nas duas línguas.

As versões corrigida de expiração e original TTL passaram por G1 a G8 no escopo declarado; G9 ainda aguarda o checkpoint 034. O consumidor local verifica três versões documentais, preserva a falha original e confere fontes, nove vínculos de trechos nos dois alvos positivos, dois baselines e tokens, sem executar comandos ou servidor Redis. A licença capturada declara alternativas de licenciamento, não uma aprovação automática de direitos. Nenhum treinamento, modelo local, produção, UI, teste permanente ou Git foi alterado. A campanha segue ativa, ainda antes das aproximadamente 12 horas solicitadas.
'''
j=p/'root-report-bundle-progress-048';prepare(root,j,{n:common.encode() for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
with (p/'root-report-append-receipt-v48.json').open('x') as f:json.dump({'bundle':str(j.relative_to(root)),'outcome':out},f,indent=2);f.write('\n')
print(out['status'])
