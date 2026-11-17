# Raciocínio sobre falhas — Criptografia Lib

[English](../../en/faq/failure-scenarios.md) | [Português brasileiro](failure-scenarios.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `dae407f6be676365babe3c21ba133ca2c8cc6bab`.

<!-- reading-section: q004 -->

## Q004 — Onde termina a consistência?

Não há banco nem armazenamento persistente de chaves em `src/`. Os bytes exatos do PEM participam do HKDF: a mesma chave RSA serializada de outra forma pode gerar subchaves diferentes. Não existem ID de chave, registro de rotação nem leitor legado automático. A restauração precisa preservar as chaves originais e a compatibilidade da versão do envelope.

<!-- reading-section: q005 -->

## Q005 — Como conduzir a investigação?

Leia `composer.json`, depois `Configuration::validate`, `Crypto::__construct`, `encrypt` e `decrypt`. Em consumidor descartável autorizado separadamente, use chave RSA sintética efêmera e faça roundtrip de `synthetic-message`; altere IV, cabeçalho e tag separadamente e espere rejeição. São verificações propostas, não executadas aqui. Coordene pacote/versão e migração do formato entre consumidores antes do deploy.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
