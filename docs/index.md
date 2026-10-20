# Engineering Library

Catálogo público local de documentação e preparação para entrevistas em inglês e português brasileiro. Selecione um projeto, escolha o idioma e siga seu índice de capítulos. Código implementado, justificativas documentadas, evidências históricas e propostas futuras têm escopos distintos.

[English](projects/engineering-library/docs/en/index.md) | [Português brasileiro](projects/engineering-library/docs/pt-BR/index.md)

| Projeto | Descrição | Documentação | FAQ | Capítulos |
| --- | --- | --- | --- | --- |
| [engineering-library](projects/engineering-library/README.pt-BR.md) | Biblioteca bilíngue com catálogo Rails/PostgreSQL, leitor Next.js e favoritos anônimos; IA permanece futura. | [EN](projects/engineering-library/docs/en/index.md) · [pt-BR](projects/engineering-library/docs/pt-BR/index.md) | [EN](projects/engineering-library/docs/en/faq/index.md) · [pt-BR](projects/engineering-library/docs/pt-BR/faq/index.md) | `architecture`, `guides`, `operations`, `faq`, `env`, `testing` |
| [env-auditor](projects/env-auditor/README.pt-BR.md) | CLI Python: sincronização literal de ambiente, prévias, backups e limites do sistema de arquivos. | [EN](projects/env-auditor/docs/en/index.md) · [pt-BR](projects/env-auditor/docs/pt-BR/index.md) | [EN](projects/env-auditor/docs/en/faq/index.md) · [pt-BR](projects/env-auditor/docs/pt-BR/faq/index.md) | `architecture`, `guides`, `operations`, `security`, `faq`, `env`, `testing` |
| [go-image-optimizer](projects/go-image-optimizer/README.pt-BR.md) | Compressão, redimensionamento, conversão e prévia síncronos de imagens Go/Next.js com codecs nativos. | [EN](projects/go-image-optimizer/docs/en/index.md) · [pt-BR](projects/go-image-optimizer/docs/pt-BR/index.md) | [EN](projects/go-image-optimizer/docs/en/faq/index.md) · [pt-BR](projects/go-image-optimizer/docs/pt-BR/faq/index.md) | `adr`, `api`, `architecture`, `docker`, `guides`, `operations`, `security`, `faq`, `env`, `testing` |
| [payment-reconciliation-lab](projects/payment-reconciliation-lab/README.pt-BR.md) | Base Spring Boot/Angular/PostgreSQL com catálogo legado somente leitura; conciliação e Stripe não estão implementados. | [EN](projects/payment-reconciliation-lab/docs/en/index.md) · [pt-BR](projects/payment-reconciliation-lab/docs/pt-BR/index.md) | [EN](projects/payment-reconciliation-lab/docs/en/faq/index.md) · [pt-BR](projects/payment-reconciliation-lab/docs/pt-BR/faq/index.md) | `adr`, `api`, `architecture`, `database`, `docker`, `guides`, `operations`, `security`, `faq`, `env`, `testing` |
| [rust-event-relay](projects/rust-event-relay/README.pt-BR.md) | Outbox transacional Rust/PostgreSQL, entrega RabbitMQ, retries, consumidor idempotente e demonstração local. | [EN](projects/rust-event-relay/docs/en/index.md) · [pt-BR](projects/rust-event-relay/docs/pt-BR/index.md) | [EN](projects/rust-event-relay/docs/en/faq/index.md) · [pt-BR](projects/rust-event-relay/docs/pt-BR/faq/index.md) | `adr`, `architecture`, `database`, `docker`, `guides`, `integrations`, `operations`, `security`, `faq`, `env`, `testing` |
| [url-shortener](projects/url-shortener/README.pt-BR.md) | Criação de URLs e redirecionamentos públicos FastAPI, IDs Redis, Base62 reversível e persistência Cassandra. | [EN](projects/url-shortener/docs/en/index.md) · [pt-BR](projects/url-shortener/docs/pt-BR/index.md) | [EN](projects/url-shortener/docs/en/faq/index.md) · [pt-BR](projects/url-shortener/docs/pt-BR/faq/index.md) | `api`, `architecture`, `database`, `docker`, `guides`, `operations`, `security`, `faq`, `env`, `testing` |

## Percursos de leitura

Em cada projeto: propósito → arquitetura → fluxo de requisição/evento → dados e integrações → segurança e testes → entrevista. Para avançar entre projetos: env-auditor (arquivos e falhas) → go-image-optimizer (HTTP e recursos) → url-shortener (consistência entre stores) → payment-reconciliation-lab (API/JPA e limites de uma transição) → rust-event-relay (entrega, posse e idempotência). A coleção engineering-library explica o catálogo, o leitor e os favoritos atuais, além das propostas futuras de IA. São sugestões de estudo, não progresso concluído.

O leitor oferece busca no projeto, incluindo snapshots de código aprovados. Não há catálogo independente por assunto nem serviço externo de busca.

[Relatório desta catalogação](catalog-review.md) · [Proveniência e mapeamento de fontes](catalog-provenance.json). Referências e fundamentos anteriores permanecem acessíveis pelos índices de idioma.

[Engineering Library — English introduction](projects/engineering-library/README.md).

[Auditoria documental de 2026-10-19](projects/engineering-library/docs/pt-BR/operations/documentation-audit-2026-10-19.md) · [Source reference verification](source-reference-verification.md) · [Contents toolbar validation](validation/contents-toolbar.md).

[Shared IMG assets / Recursos compartilhados](img/README.md)
