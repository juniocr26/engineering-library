# Fronteiras de confiança — Criptografia Lib

[English](../../en/security/boundaries.md) | [Português brasileiro](boundaries.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `dae407f6be676365babe3c21ba133ca2c8cc6bab`.

<!-- reading-section: mechanisms -->

## Mecanismos e limites

RS256 é um rótulo/requisito de validação da configuração; os payloads não são JWTs cifrados por RSA. No formato atual, o HMAC cobre o IV. A autenticação dos bytes não comprova identidade do ator, propriedade do registro, atualidade ou prevenção de replay. Não normalize bytes da chave nem gere uma substituta para reparar dados ilegíveis.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
