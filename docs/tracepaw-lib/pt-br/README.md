# TracePaw

[Contents](index.md)

Biblioteca privada PHP documentada aqui por contratos e padrões seguros para publicação. Identidade canônica `tracepaw-lib`, pacote `parceiro-vivabem/tracepaw-lib`, namespace `TracePaw`, PHP `^8.2`, release local `0.2.0`. Não é servidor central de logs nem plataforma de tracing distribuído.

A coleção única é `docs/tracepaw-lib/{en,pt-br}`. Substitui a antiga identidade Datadog Lib sem manter entrada canônica duplicada. Os capítulos abaixo preservam contratos públicos do pacote e exemplos sintéticos; não publicam fonte privada, logs ou configuração efetiva.

[Architecture](architecture/overview.md) · [API](api/contracts.md) · [Installation](guides/installation.md) · [Security](security/context-and-diagnostics.md) · [Reliability](operations/reliability.md) · [Verification](testing/verification.md)

Revisão de 11/11/2026: declaração, lockfile e metadados locais de instalação dos três consumidores Laravel confirmam `0.2.0`; imagem/implantação e publicação remota permanecem não verificadas. A consulta ao endpoint público de metadados não produziu resposta utilizável. Não houve alteração de metadados no banco; a mudança de slug não migra automaticamente bookmarks, notas ou highlights existentes. Preserve esses dados para migração operacional autorizada.
