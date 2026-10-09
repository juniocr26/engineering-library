# tecnical-interview

[English](README.md) | [Português brasileiro](README.pt-BR.md)

Guias de estudo para entrevistas técnicas sobre ENV Auditor, Go Image Optimizer, URL Shortener, Rust Event Relay e Payment Reconciliation Lab. Explicam comportamento implementado, alternativas e limitações; adapte as respostas à experiência que consegue demonstrar.

## Documentação

- [env auditor](docs/pt-BR/env-auditor.md)
- [go image optimizer](docs/pt-BR/go-image-optimizer.md)
- [Instalação e execução](docs/pt-BR/setup.md)
- [url shortener](docs/pt-BR/url-shortener.md)
- [Resultados de validação](docs/pt-BR/verification.md)
- [Rust Event Relay](docs/pt-BR/rust-event-relay.md)
- [Payment Reconciliation Lab](docs/pt-BR/payment-reconciliation-lab.md)

## Ordem de estudo

Comece pelo ENV Auditor para descoberta/parsing/falhas locais, depois Go Image Optimizer para HTTP, interfaces e recursos. Siga URL Shortener para falhas entre stores, encoding e consistência; use o catálogo legado do Payment Reconciliation Lab para comparar DTO/JPA/segurança e separar transição de domínio de fluxos entregues. Termine em Rust Event Relay para estado durável, incerteza de broker e contratos de ownership. Cada guia ordena seus pré-requisitos/aprofundamentos. São sugestões, sem marcar assuntos concluídos.
