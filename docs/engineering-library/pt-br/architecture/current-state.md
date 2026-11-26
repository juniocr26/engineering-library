# Engineering Library: arquitetura atual

[Índice de arquitetura](index.md) · [Implementação detalhada](current-implementation.md)

<!-- reading-section: current-state-1 -->
## Estrutura documental

Referência atual: 26/11/2026, código `246f58be`. Engineering Library é repositório privado da Viva Bem para uso interno autorizado. Afirmações históricas de scaffold ou anteriores ao Ollama não descrevem a implementação atual.

| Conteúdo | Caminho relativo ao checkout |
| --- | --- |
| Capítulos ingleses | `docs/<slug>/en/` |
| Capítulos em português brasileiro | `docs/<slug>/pt-br/` |
| Imagens comuns / localizadas | `docs/<slug>/img/`, diretórios `img/` por idioma |
| Catálogo aprovado de referências de código | `docs/<slug>/en/links/` |
| Metadados de cadastro | `docs/.catalog.json` e bios localizadas |
| Operação/recuperação privada | `backend/storage/makedocs/` |

O idioma de API `pt-BR` corresponde ao diretório `pt-br`. PostgreSQL armazena metadados/anotações compartilhadas; Markdown contém os capítulos. Rails e Next usam `/docs` no Compose, atualmente gravável nos dois serviços. Identidades de anotações são lógicas, não páginas físicas.

<!-- reading-section: current-state-2 -->
## Base implementada

Next.js fornece catálogo, paginação física, capítulos, busca, diagramas e referências aprovadas de código. Rails fornece metadados paginados, notas/destaques/marcadores compartilhados e gerenciamento protegido em desenvolvimento. PostgreSQL persiste esses registros. Não existem contas pessoais nem conjuntos privados de anotações por usuário.

Estão implementados pipeline Ollama local, cadastro explícito, relocação verificada, retries idempotentes, remoção preservadora, adapter supervisionado no host e publicação recuperável de rascunhos em dois destinos. UI e CLI normais reutilizam o mesmo comando. `/up` verifica resposta Rails e adapter obrigatório; não certifica integridade do banco ou qualidade semântica.

<!-- reading-section: current-state-3 -->
## Evidências e limites abertos

MakeDocs está operacional; cobertura, redação factual e tradução ainda têm limitações e exigem revisão. Não implica aceitação integral do livro, endurecimento de produção, RAG universal ou fine-tuning neural concluído. Esta revisão analisa código e não reexecuta geração ou treinamento.

Consulte [arquitetura detalhada](current-implementation.md), [desenvolvimento](../guides/application-development.md), [pipeline MakeDocs](../training/local-documentation-command.md), [recuperação](../operations/runtime-and-recovery.md), [decisões](decisions.md) e [FAQ](../faq/application-and-catalog.md). Auditorias datadas permanecem em [operações](../operations/index.md).

<!-- reading-section: shared-annotation-migration -->
## Migração de anotações compartilhadas

Registro histórico preservado da revisão anterior; as contagens não são nova medição do banco.


Em 20/10/2026, o banco local manteve 60 notas, 60 destaques e 12 marcações durante a migração em duas fases. IDs, corpos, trechos e chaves estrangeiras são preservados. Em conflitos de chave de seed, o menor ID mantém a chave canônica; os seguintes recebem o prefixo determinístico `__legacy_demo__<id>:`. Continuam identificados para limpeza, sem mesclar notas distintas. A migração é irreversível porque a propriedade removida não pode ser reconstruída. Faça backup restrito antes de aplicá-la. Notas sem destaque mantêm âncoras independentes; listas combinadas usam chaves estrangeiras explícitas, sem inferir vínculos por texto idêntico.
