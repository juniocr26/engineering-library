# Engineering Library

[English](README.md) | [Português brasileiro](README.pt-BR.md)

Coleção técnica bilíngue autossuficiente e preparação para entrevistas sobre ENV Auditor, Go Image Optimizer, URL Shortener, Rust Event Relay e Payment Reconciliation Lab. Explica mecanismos implementados, alternativas e limites; adapte respostas à experiência demonstrável.

## Catálogo de documentação e percurso de leitura

- [Catálogo completo por categoria](docs/pt-BR/index.md)
- [Checklist da revisão e lacunas](docs/pt-BR/operations/completion-checklist.md)

Leia propósito/setup, arquitetura e contratos, segurança/falhas, testes/evidência e implantação/recuperação local. Este projeto é independente no portfólio; procedimentos runtime documentados não foram executados na revisão de 2026-10-10.

Preparação para entrevistas é responsabilidade central: preserve e ensaie respostas substanciais com aprofundamentos respondidos e limites nos dois idiomas. A coleção também fornece dossiês completos e fundamentos conceituais.

## Documentação

- [env auditor](docs/pt-BR/interviews/env-auditor.md)
- [go image optimizer](docs/pt-BR/interviews/go-image-optimizer.md)
- [Instalação e execução](docs/pt-BR/guides/setup.md)
- [url shortener](docs/pt-BR/interviews/url-shortener.md)
- [Resultados de validação](docs/pt-BR/testing/verification.md)
- [Rust Event Relay](docs/pt-BR/interviews/rust-event-relay.md)
- [Payment Reconciliation Lab](docs/pt-BR/interviews/payment-reconciliation-lab.md)

## Ordem de estudo

Comece pelo ENV Auditor para descoberta/parsing/falhas locais, depois Go Image Optimizer para HTTP, interfaces e recursos. Siga URL Shortener para falhas entre stores, encoding e consistência; use o catálogo legado do Payment Reconciliation Lab para comparar DTO/JPA/segurança e separar transição de domínio de fluxos entregues. Termine em Rust Event Relay para estado durável, incerteza de broker e contratos de ownership. Cada guia ordena seus pré-requisitos/aprofundamentos. São sugestões, sem marcar assuntos concluídos.

[Composição e lições operacionais do worker Rust](docs/pt-BR/architecture/rust-event-relay.md).

[Recuperação Rust e limites de confiabilidade](docs/pt-BR/architecture/rust-event-relay.md).

## Workspace atual e validação

Comece pelo [catálogo](docs/pt-BR/architecture/workspace-catalog.md), siga um dossiê até as respostas de entrevista e compare fundamentos/fluxos verificados. Rust cobre escopo local final aceito com produtor/consumidor/UI; marcos anteriores são históricos. Execute no diretório pai:

```sh
python3 -B engineering-library/tools/check_docs.py --workspace .
python3 -B -m unittest discover -s engineering-library/tools -p test_check_docs.py -v
```

Somente Python 3.10+ é necessário para validar documentação local; não é preciso instalar aplicações. [Revisão de 2026-10-18 e lacunas](docs/pt-BR/operations/workspace-review-2026-10-18.md).
