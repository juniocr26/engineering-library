import json
from pathlib import Path
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2]
common='''

### Progresso intensivo 042 — qualidade JPEG aceita no escopo técnico; comparação de metadados não executada

O capítulo original completo de qualidade JPEG, em inglês e português, passou pelos nove critérios congelados após a recuperação efetiva do checkpoint 030. O arquivo restaurou 3.884 arquivos regulares com hashes e modos conferidos e reproduziu 31 grupos de consumidores. O consumidor específico verificou seis trechos de fonte, dois lotes do parser existente, duas respostas históricas e seis linhas de exemplos estáticos nas duas línguas. O procedimento arquivado de pós-nota reconstruiu os quatro relatórios com seus recibos laterais. Isso não comprova execução de codecs, tipagem integral do pacote, recuperação de pesos ou aprovação humana.

O inventário de métricas v9 registra 22 pares relacionados de versões documentais: 19 aceitos tecnicamente, um inconclusivo por lacuna de citação e dois com falha de atribuição histórica. O par de manutenção interna continua separado. Essas contagens descrevem revisões manuais de versões; não são uma taxa de sucesso neural nem uma amostra de 22 tarefas independentes. O registro v8 contempla as 16 métricas solicitadas e preserva taxas gerais desconhecidas e denominador zero para novos ensaios neurais locais. O lote de revisão v9 contém três pares públicos principais e nove complementares, 12 no total, além do par interno restrito. Publicação, treinamento e Gold continuam sem aprovação.

Uma auditoria distinta começou no capítulo original de dimensões do backend. As duas línguas e a fonte fixada foram lidas; o parser existente preserva a guarda com OR, a comparação estrita por divisão e os retornos distintos. As respostas históricas mostram quatro entradas inventadas para um wrapper com dois parâmetros e metadados do parser apresentados como contrato da aplicação. A revisão completa e a recuperação desse segundo alvo ainda não foram concluídas. As verificações do frontend permanecem um contrato separado, sem garantia inventada de integração.

O diagnóstico source-preparation-metadata-leakage-diagnostic-v1.json preserva uma resposta histórica e dois envelopes de entrada, com os mesmos trechos de código. Um mantém os metadados do parser; o outro guarda apenas os campos de fonte selecionados, mantendo a proveniência completa fora do envelope destinado ao modelo. A comparação está preparada e não executada. A presença de texto semelhante nos metadados e na resposta não demonstra causalidade; proibir lexicalmente palavras como parser também poderia recusar explicações legítimas. Nenhum prompt de produção, verificador ou peso foi alterado.

A campanha continua ativa. Novas chamadas, tokens e segundos de geração do modelo local permanecem em zero; atualizações de otimizador também. O uso de GPT/Codex é distinto e não é zero; o custo monetário total é desconhecido. A duração aproximada de 12 horas e a consolidação final ainda estão pendentes. Todos os originais, resultados anteriores e limites de aprovação permanecem preservados.
'''
j=p/'root-report-bundle-progress-042';prepare(root,j,{n:common.encode() for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
with (p/'root-report-append-receipt-v42.json').open('x') as f:json.dump({'bundle':str(j.relative_to(root)),'outcome':out},f,indent=2);f.write('\n')
print(out['status'])
