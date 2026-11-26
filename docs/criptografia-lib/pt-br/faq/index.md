# FAQ técnica — Criptografia Lib

[English](../../en/faq/index.md) | [Português brasileiro](index.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `dae407f6be676365babe3c21ba133ca2c8cc6bab`.

<!-- reading-section: q001 -->

## Q001 — RS256 cifra os dados?

Não. A validade do PEM RSA é verificada, mas AES-256-CBC cifra o payload e HMAC-SHA256 o autentica. Confundir o rótulo com cifra assimétrica oculta a fronteira de custódia do segredo compartilhado.

<!-- reading-section: q002 -->

## Q002 — É possível substituir por PEM com formatação equivalente?

Sem validação, não: o HKDF usa os bytes exatos da entrada. O reenquadramento para validação não altera os bytes de derivação. Preserve a representação original e teste restauração com o formato/versão efetivo.

<!-- reading-section: q003 -->

## Q003 — Quais afirmações permanecem sem validação?

Permanecem pendentes revisão criptográfica independente, procedimento de migração legada, rotação, aceitação de restauração e verificação das dependências instaladas nos consumidores. Nenhuma suíte de runtime/segurança foi executada.

[Evidence and limits / Evidências e limites](../operations/source-review.md)

[Failure scenarios / Cenários de falha](failure-scenarios.md)
