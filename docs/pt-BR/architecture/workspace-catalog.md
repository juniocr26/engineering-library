# Catálogo do workspace e percursos de estudo

Este workspace pai contém seis repositórios Git independentes. Inspeção estática em 2026-10-10 não encontrou integração runtime de uma aplicação do portfólio com outra. Compartilhar Docker, HTTP, Python ou PostgreSQL é sobreposição conceitual, não grafo de chamadas de ecossistema. ENV Auditor pode percorrer diretórios irmãos como entradas de filesystem; não é cliente de rede dessas aplicações. Engineering Library é coleção documental/com ferramentas, não dependência de aplicação.

| Repositório | Responsabilidade atual | Representação / fronteira principal | Início |
| --- | --- | --- | --- |
| env-auditor | Sincronização literal de chaves de ambiente | Blocos ordenados, arquivos, substituição por arquivo | [Dossiê](env-auditor.md), [entrevista](../interviews/env-auditor.md) |
| go-image-optimizer | Compressão/resize/conversão/preview síncronos | Multipart, pixels, codecs nativos, blobs | [Dossiê](go-image-optimizer.md), [entrevista](../interviews/go-image-optimizer.md) |
| url-shortener | Criação autenticada, resolução pública 301 | ID Redis, código Base62 afim, mapeamento Cassandra | [Dossiê](url-shortener.md), [entrevista](../interviews/url-shortener.md) |
| payment-reconciliation-lab | Catálogo somente leitura durante transição | Entidades JPA, DTOs, schema PostgreSQL com constraints | [Dossiê](payment-reconciliation-lab.md), [entrevista](../interviews/payment-reconciliation-lab.md) |
| rust-event-relay | Liveness HTTP e leitor/publisher/modelos separados | Envelope, snapshot, confirmação, ports de autoridade futuros | [Dossiê](rust-event-relay.md), [entrevista](../interviews/rust-event-relay.md) |
| engineering-library | Explicações autossuficientes e entrevistas | Markdown bilíngue e validador somente leitura | [Entrevista da coleção](../interviews/engineering-library.md), [validador](../guides/documentation-validator.md) |

No primeiro percurso, siga parse/plano/gravação do ENV Auditor, HTTP/pixels do Go, falhas dos dois bancos do Shortener, DTO/transação do Payment Lab e snapshot/autoridade/broker do Rust. Depois, ensaie explicação introdutória, defenda mecanismo com código, responda cenário de falha e compare alternativa. [Entrevista transversal](../interviews/foundations.md) fornece conceitos; [fluxos verificados](../integrations/verified-flows.md) explica caminhos reais completos. Nada marca estudo como concluído.

Verificações runtime registradas continuam históricas. Esta revisão executou apenas validação documental e testes isolados do validador. Nenhuma aplicação, contêiner, migração, benchmark, chamada de rede ou implantação foi executada. [Relatório de conclusão](../operations/workspace-completion.md) registra repositórios e lacunas de evidência.
