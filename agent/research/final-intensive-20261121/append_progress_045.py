import json
from pathlib import Path
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2]
common='''

### Progresso intensivo 045 — recuperação corrigida de dimensões e limites da análise Ruby

O checkpoint 032 restaurou 3.969 arquivos regulares com hashes e modos conferidos e reproduziu 33 grupos finitos. O recibo preserva os dois aliases lexicais dos links de dimensões e seus destinos canônicos dentro da raiz. Os controles de caminhos e o consumidor específico de dimensões passaram; a extração manteve sua proteção contra nomes inseguros. A falha anterior do checkpoint 031 continua preservada e não foi contada como recuperação bem-sucedida. Os quatro relatórios de pós-nota foram reconstruídos com o script arquivado e os recibos laterais.

A revisão v2 de dimensões fecha G9 e registra os nove critérios técnicos aprovados para o par original, sem alterar seus bytes. O inventário v10 descreve 23 pares relacionados de versões: 20 aceitos tecnicamente, um inconclusivo por citação e dois com falha de atribuição histórica. A manutenção interna continua separada. O lote v10 mantém três pares públicos principais e dez complementares, 13 no total, com aprovação de publicação, treinamento e Gold ainda ausente. O registro v9 cobre as 16 métricas solicitadas e distingue a recuperação de 032 da falha de 031. Nenhuma dessas contagens é uma taxa de sucesso de novos modelos.

Para o próximo alvo Rails, foram preservados request.rb, a licença MIT e o gemspec público de actionpack 8.1.4. O checksum de request.rb coincide com o pacote imutável original. Nenhum gemspec foi avaliado e nenhuma dependência foi carregada como aplicação. O Ripper disponível, de Ruby 2.6.10, analisou o arquivo inteiro e encontrou uma definição de cada um dos cinco métodos selecionados, sem diagnósticos. Essa análise sintática não valida a compatibilidade de execução do actionpack, cujo gemspec exige Ruby >= 3.2, nem executa métodos de requisição. A revisão completa de fonte, atribuição histórica, duas línguas e recuperação desse alvo segue pendente.

A campanha continua ativa. Duração aproximada de 12 horas, atualização final das 22 respostas, inventário e estado final de escopo continuam pendentes. Modelos locais não geraram novos tokens ou respostas, e não houve atualização de otimizador. O uso de GPT/Codex permanece separado e não nulo; custo monetário total desconhecido. Não houve alteração de produção, UI, testes permanentes, repositórios externos ou histórico Git.
'''
j=p/'root-report-bundle-progress-045';prepare(root,j,{n:common.encode() for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
with (p/'root-report-append-receipt-v45.json').open('x') as f:json.dump({'bundle':str(j.relative_to(root)),'outcome':out},f,indent=2);f.write('\n')
print(out['status'])
