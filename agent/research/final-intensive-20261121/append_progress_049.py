import json
from pathlib import Path
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2]
common='''

### Progresso intensivo 049 — Redis recuperado, três originais falhos e escopo reconferido

O checkpoint 034 restaurou 4.127 arquivos regulares com hashes e modos conferidos e reproduziu 35 grupos finitos. O consumidor Redis preservou a falha do original de expiração e verificou a versão corrigida, o original TTL, nove vínculos de trechos e dois baselines. A pós-nota reconstruiu os quatro relatórios com script e recibos laterais. As duas versões positivas fecham G9; o original de expiração continua FAIL_HISTORICAL_ATTRIBUTION, sem alteração retroativa de seus bytes ou labels.

O inventário de métricas v12 registra 27 pares relacionados de versões: 23 aceitos tecnicamente, um inconclusivo por citação e três com falha de atribuição histórica. A manutenção interna permanece separada. O lote v12 conserva três pares públicos principais e treze complementares, 16 no total, mantendo fora da seleção os três originais falhos. A licença Redis foi preservada com suas alternativas declaradas; nenhuma opção foi escolhida e nenhum direito de treinamento ou publicação foi aprovado. Todas essas contagens continuam manuais e correlacionadas, sem taxa nova de desempenho neural.

A correspondência v5 comparou 46 hashes de documentos aceitos aos 297 registros não privados: 64 referências diretas coincidem, 132 apontam para documentos diferentes e 101 não possuem os campos diretos selecionados. Oito registros privados continuam excluídos. Os sete arquivos originais foram conferidos e permanecem intactos. Coincidência com bytes de um documento pai não aprova o registro, sua resposta FAQ, sua licença, treinamento ou Gold. O registro de métricas v11 mantém as 16 métricas solicitadas com suas populações e desconhecidos explícitos.

A observação v5 reconferiu os 42 HEADs e os estados dos 41 repositórios externos, todos iguais à linha de base. No Engineering Library, os diffs rastreados e staged estão vazios; os únicos itens não rastreados são os quatro relatórios e a árvore isolada de pesquisa. Isso não foi usado para inferir identidade de todo cache ignorado. O inventário cut014 contém 3.813 arquivos nesse corte, incluindo os artefatos ignorados de pesquisa e backups; o próprio inventário e os arquivos posteriores ficam fora do seu autocorte declarado.

O ledger v14 agora vincula essa observação e o inventário real, além das ações Redis, leituras públicas de actionpack e tentativa de metadados do tokenizer. A atualização inline v13 falhou antes de gravar por misturar caminhos relativos e absolutos; um produtor separado resolveu os caminhos de modo consistente. Também foi corrigida a descrição anterior do corte de inventário: um campo antigo ainda apontava para cut010, embora seu texto mencionasse cut011. As versões e falhas anteriores foram preservadas.

A próxima auditoria delimitada será o alvo original Ruff target-version em Rust, sem presumir que sua versão original já esteja aprovada por revisões de versões enriquecidas. A campanha continua ativa, com aproximadamente 12 horas e a consolidação final ainda pendentes. Não houve nova geração local, treinamento, aprovação Gold, mudança de produção, UI, testes permanentes ou Git.
'''
j=p/'root-report-bundle-progress-049';prepare(root,j,{n:common.encode() for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
with (p/'root-report-append-receipt-v49.json').open('x') as f:json.dump({'bundle':str(j.relative_to(root)),'outcome':out},f,indent=2);f.write('\n')
print(out['status'])
