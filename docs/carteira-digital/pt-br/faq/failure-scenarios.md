# Raciocínio sobre falhas — Carteira Digital

[English](../../en/faq/failure-scenarios.md) | [Português brasileiro](failure-scenarios.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `9a6b795b6ebc16f0390e0fbdbf711f257e42fa2a`.

<!-- reading-section: q004 -->

## Q004 — Onde termina a consistência?

A migration transacao define nove campos: oid_transacao (chave primária de 36 caracteres com default UUID), oid_usuario, chave_idempotencia obrigatória globalmente única, tipo_transacao, inteiro unsigned valor_centavos, moeda com default brl, situacao_transacao, data_transacao e JSON metadados anulável. O índice usuário/data auxilia consultas, sem autorizar acesso. Migrations consolidadas de banco novo não são upgrade in-place de instalação existente. Uma chave única evita identidades armazenadas repetidas, sem implementar execução ou conciliação no provedor.

<!-- reading-section: q005 -->

## Q005 — Como conduzir a investigação?

Rastreie cliente específico de saldo do Portal, middleware e leitor da carteira antes de diagnosticar o dashboard. Preserve a diferença entre exists=false e falha. Para aceitação isolada futura, use schema descartável e titular sintético; verifique saldo existente, ausente, duplicado, sub/hash incorretos, envelope malformado e banco indisponível. Não reproduza filas antigas do provedor, aplique migrations sobre dados existentes nem inicie workers financeiros a partir de instruções históricas.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
