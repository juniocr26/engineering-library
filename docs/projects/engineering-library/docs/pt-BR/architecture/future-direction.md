# Direção futura e questões de projeto

## Status

API de catálogo somente leitura, livro Markdown interno, busca no projeto e favoritos anônimos estão implementados. O [estado atual](current-state.md) descreve suas fronteiras. Propostas remanescentes tratam de geração documental automatizada, inferência e política de acesso público/privado; o roadmap antigo do scaffold é histórico.

## Interface de leitura

Seleção de projeto, capítulos bilíngues, páginas medidas, expansões de código e favoritos lógicos já existem. Próximos passos devem partir de comportamento concreto e evidências, sem propor reconstruir todo o leitor como funcionalidade ausente. A arquitetura atual dispensa API Rails separada de Markdown bruto: Next lê a coleção local delimitada. A implementação não comprova implantação em produção nem certificação completa de acessibilidade.

## IA local e geração incremental

Um fluxo proposto é: descobrir repositórios públicos permitidos → inspecionar documentação segura e código relevante → identificar entradas alteradas → propor mudanças documentais com evidências → validar equivalência/navegação → revisar e publicar deliberadamente. É um esboço, não um agente instalado nem framework de automação. Hashes de fontes e revisões inspecionadas podem apoiar detecção de mudanças; um hash diferente não determina sozinho o impacto semântico. Preservar notas humanas e IDs de perguntas/ADRs; comparar antes de reescrever.

Inferência local oferece proximidade dos dados e operação offline, mas consome CPU/RAM e exige gestão de modelo/runtime. APIs comerciais podem reduzir processamento local, ao custo de transferência externa, cobrança e dependência de serviço. Nenhum provedor está integrado. Modelo, quantização, tamanho de contexto, velocidade de inferência e hardware mínimo não foram escolhidos nem medidos. Pesos, KV cache, contexto, concorrência e overhead influenciam memória. Medir tarefas seguras representativas no host real antes de escolher um modelo.

## Consistência e separação pública/privada

Um adaptador de ingestão deve impor raízes permitidas sem atravessar symlinks externos, excluir credenciais/dados/backups e distinguir código implementado, evidência datada, justificativa documentada e melhoria proposta. São proteções propostas, não uma fronteira de segurança implantada. Separar entradas, saídas e política de acesso privadas do catálogo público; não presumir que um modelo consegue remover segredos de forma confiável. Uma citação permite rastrear, mas não estabelece veracidade por si só.

Desafios abertos: divergência entre código e documentação; marcos históricos conflitantes; significado da tradução além da equivalência de caminhos; links/âncoras Markdown robustos; revisão de alucinações; preservação de material autoral; recursos limitados de inferência; publicação segura. Próxima ordem sugerida: manter catálogo/leitor existentes → resolver lacunas observadas de uso/evidência → delimitar experimentos de ingestão/inferência. É planejamento, sem compromisso de lançamento.
