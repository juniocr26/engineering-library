# Fronteiras de confiança — Carteira Digital

[English](../../en/security/boundaries.md) | [Português brasileiro](boundaries.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `9a6b795b6ebc16f0390e0fbdbf711f257e42fa2a`.

<!-- reading-section: mechanisms -->

## Mecanismos e limites

CasoDeUsoConsultarSaldo exige sub igual ao titular solicitado, issuer vivabem, audience carteira-digital, scope wallet:balance:read e request_hash SHA-256 sobre POST, caminho exato e corpo cifrado. Credenciais genéricas de serviço não bastam para essa leitura. Vínculo inválido retorna 403, entrada cifrada malformada 422, ambiguidade/falha de infraestrutura 503. Autenticação ou assinatura de webhook não comprovam efeito financeiro. Não transforme indisponibilidade remota em saldo zero.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
