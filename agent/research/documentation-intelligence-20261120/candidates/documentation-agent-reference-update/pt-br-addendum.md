
## Suplemento de manutenção de referências de fonte — 20/11/2026

As afirmações anteriores sobre o recorte atual descrevem a campanha anterior preservada. Este suplemento separado de pesquisa observa o planejador `0.3.6` e a manutenção de workspace `0.1.5`; não substitui recibos anteriores, soma novamente testes antigos nem implica que o escritor Ruby comum passou a consumir essas ferramentas opcionais.

O planejador aceita apenas uma identidade canônica e limitada, relativa ao repositório, nos campos de caminho de referências de fonte. Caminhos vazios, segmentos `.` ou `..`, caminhos absolutos e caracteres não suportados exigem revisão. Se as afirmações dos dois idiomas já nomeiam o caminho atual declarado, recomenda `NO-OP`; um caminho anterior positivamente identificado que difere do atual pode recomendar `MODIFY`. Isso continua sendo um protocolo de fonte/afirmação declarado pelo operador, sem provar que um caminho arbitrário exista em uma revisão Git.

A camada de preparação no sistema de arquivos acrescenta uma conferência independente de identidade: os metadados `current_path` e `previous_path` fornecidos devem corresponder aos arquivos atual e anterior registrados na operação. Bytes iguais na fonte do pacote não podem certificar outro caminho. A nova proteção recusa um `NO-OP` com caminho atual falso e uma relocação com caminho anterior falso antes de gravar candidatos. Uma relocação válida continua preparando um candidato EN/PT isolado; uma referência já atual preserva bytes e metadados originais sem criar uma raiz de candidato.

Os doze controles do planejador passaram de 9/12 para 12/12, e os quatro controles de identidade física de 2/4 para 4/4, somente em desenvolvimento. A avaliação pública Boltons congelada permanece com 0/8 ações exatas e oito abstenções; a matriz antiga permanece em 22/24. São denominadores separados. Nenhum arquivo permanente de teste, documentação ativa, permissão de publicação ou peso do modelo mudou.
