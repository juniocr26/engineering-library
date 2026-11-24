import json
from pathlib import Path
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2]
common='''

### Progresso intensivo 043 — revisão do alvo original de dimensões, com recuperação pendente

O par original completo de dimensões do backend, linhas 17/18 do conjunto preservado, foi revisto nas duas línguas com três FAQs. A fonte limits.go já adquirida por Git na revisão 48476de6e4450294b7769ab7af90805100bb21b5 foi reutilizada com seu recibo; não houve nova aquisição desnecessária dos mesmos bytes. O parser existente 1.6.1 preservou as três funções selecionadas, incluindo os dois trechos do pacote original, a delegação do wrapper e a cadeia de retornos do helper.

A declaração do wrapper recebe configuração e orçamento. Width e Height são expressões de argumentos da chamada ao helper, não parâmetros adicionais. O primeiro retorno rejeita qualquer dimensão não positiva com OR; só depois ocorre a comparação estrita width > maxPixels/height. A igualdade com o quociente evita esse ramo; orçamento zero com dimensões positivas ainda é rejeitado. O wrapper encaminha o orçamento recebido, enquanto o validador de animação seleciona explicitamente o padrão estático. Pixels não são bytes nem uma garantia de memória residente.

As requisições e respostas históricas confirmam as atribuições do capítulo: o braço caller inventou quatro entradas e tratou metadados do parser como contrato da aplicação. O braço com helper mencionou positividade, mas não preservou o quociente, os erros distintos ou nil e usou a citação do wrapper. Dois links bilíngues de animação resolvem os bytes esperados; a falha de atribuição histórica daquele artigo vinculado continua registrada e não é aprovada pela simples existência do link. Também não há garantia inferida de integração com o frontend.

Onze grupos compostos de fonte e onze contestações foram adjudicados pelo mesmo agente, sem alegação de contagem atômica independente. G1 a G8 passaram no escopo congelado; G9 continua inconclusivo até a restauração efetiva do checkpoint 031. O consumidor local conferiu fontes, respostas, sintaxe, FAQs e links. Nenhum programa-alvo, teste de aplicação ou modelo local foi executado. Os originais, a produção, a UI e os testes permanentes permanecem intactos. A campanha continua ativa e a duração aproximada de 12 horas ainda não foi atingida.
'''
j=p/'root-report-bundle-progress-043';prepare(root,j,{n:common.encode() for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
with (p/'root-report-append-receipt-v43.json').open('x') as f:json.dump({'bundle':str(j.relative_to(root)),'outcome':out},f,indent=2);f.write('\n')
print(out['status'])
