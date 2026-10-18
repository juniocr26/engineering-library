# Direção futura e questões de projeto

## Status

São requisitos e propostas exploratórias para próximos marcos, sem implementação ou comprovação de uma arquitetura detalhada aprovada. O scaffold e o catálogo Markdown atuais estão no [estado atual](current-state.md). O guia de desenvolvimento existente apresenta uma primeira API de coleção/capítulo somente leitura como trabalho futuro.

## Interface de leitura

A experiência pretendida de livro técnico começa pela seleção de projeto, seguida de idioma, índice de capítulos e documento. Uma futura API precisa definir identificadores estáveis, resolução segura de caminhos, renderização Markdown, navegação e contratos de erro antes do consumo pelo Next.js. Títulos e caminhos existentes podem fornecer navegação; nenhuma busca, estrutura de banco ou funcionalidade de frontend foi adicionada aqui. Acessibilidade, renderização de código/diagramas e tratamento de links quebrados precisam de critérios de aceite explícitos.

## IA local e geração incremental

Um fluxo proposto é: descobrir repositórios públicos permitidos → inspecionar documentação segura e código relevante → identificar entradas alteradas → propor mudanças documentais com evidências → validar equivalência/navegação → revisar e publicar deliberadamente. É um esboço, não um agente instalado nem framework de automação. Hashes de fontes e revisões inspecionadas podem apoiar detecção de mudanças; um hash diferente não determina sozinho o impacto semântico. Preservar notas humanas e IDs de perguntas/ADRs; comparar antes de reescrever.

Inferência local oferece proximidade dos dados e operação offline, mas consome CPU/RAM e exige gestão de modelo/runtime. APIs comerciais podem reduzir processamento local, ao custo de transferência externa, cobrança e dependência de serviço. Nenhum provedor está integrado. Modelo, quantização, tamanho de contexto, velocidade de inferência e hardware mínimo não foram escolhidos nem medidos. Pesos, KV cache, contexto, concorrência e overhead influenciam memória. Medir tarefas seguras representativas no host real antes de escolher um modelo.

## Consistência e separação pública/privada

Um adaptador de ingestão deve impor raízes permitidas sem atravessar symlinks externos, excluir credenciais/dados/backups e distinguir código implementado, evidência datada, justificativa documentada e melhoria proposta. São proteções propostas, não uma fronteira de segurança implantada. Separar entradas, saídas e política de acesso privadas do catálogo público; não presumir que um modelo consegue remover segredos de forma confiável. Uma citação permite rastrear, mas não estabelece veracidade por si só.

Desafios abertos: divergência entre código e documentação; marcos históricos conflitantes; significado da tradução além da equivalência de caminhos; links/âncoras Markdown robustos; revisão de alucinações; preservação de material autoral; recursos limitados de inferência; publicação segura. Ordem sugerida: manutenção do catálogo → contrato documental somente leitura → interface de livro → experimentos de ingestão/inferência com escopo separado. São pré-requisitos, não marcos concluídos nem compromissos de lançamento.
