# Catálogo do workspace e roteiros de estudo

2026-10-18. Seis repositórios Git imediatos; todos inicialmente limpos. Não foi encontrado repositório arquivado/de referência no diretório pai. Frontend/backend internos são componentes. Caches, builds, fixtures e evidências não são projetos.

| Repository | Revision | Responsabilidade | Estudo |
| --- | --- | --- | --- |
| engineering-library | `0eb8085e4461` | Referência bilíngue autossuficiente, entrevistas e validação documental somente leitura. | [Entrevista da coleção](../interviews/engineering-library.md) |
| env-auditor | `000949ff926f` | Sincronização literal local de chaves; blocos ordenados, planos e substituição por arquivo. | [Dossier](env-auditor.md) / [Q&A](../interviews/env-auditor.md) |
| go-image-optimizer | `2c9a27f40a2a` | Processamento síncrono Go com proxy Next.js e codecs nativos; sem jobs duráveis. | [Dossier](go-image-optimizer.md) / [Q&A](../interviews/go-image-optimizer.md) |
| payment-reconciliation-lab | `71b8b8f22d38` | Catálogo somente leitura retido; Spring/JPA/Flyway e Angular. Conciliação/Stripe planejados. | [Dossier](payment-reconciliation-lab.md) / [Q&A](../interviews/payment-reconciliation-lab.md) |
| rust-event-relay | `6e5e64fbffea` | Escopo local final aceito com produtor/outbox/AMQP/consumidor/UI, cenários reais limitados e simulações explícitas. | [Dossier](rust-event-relay.md) / [Q&A](../interviews/rust-event-relay.md) |
| url-shortener | `40e4ea05d6e4` | Criação/resolução 301 FastAPI; IDs Redis e mapeamentos Cassandra; sem transação conjunta. | [Dossier](url-shortener.md) / [Q&A](../interviews/url-shortener.md) |

## Roteiros

Executar: abra README e setup do próprio projeto; repositórios irmãos são referências opcionais. Arquitetura: leia dossiê e acompanhe registros/chamadas. Testar/diagnosticar: siga estratégia/operação, separando execução histórica de instrução atual. Entrevista: pratique propósito, mecanismo, falha, alternativa e limite de evidência.

Ordem sugerida: ENV Auditor (representação/filesystem), Go (HTTP/recursos), URL Shortener (falhas entre stores), Payment Lab (DTO/SQL/transição), Rust (autoridade durável/incerteza/efeitos) e [fundamentos](../interviews/foundations.md). [Relações verificadas](../integrations/verified-flows.md) e [revisão de conclusão/evidência](../operations/workspace-review-2026-10-18.md) delimitam escopo. Nenhuma aplicação depende da Engineering Library.
