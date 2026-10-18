# Payment Reconciliation Lab

[English](README.md) | [Português brasileiro](README.pt-BR.md)

Laboratório de backend em transição para reconciliação de pagamentos com Java, Spring Boot, Angular, PostgreSQL e Stripe. Identidade da infraestrutura atualizada; o catálogo somente leitura ainda é a interface atual. Reconciliação e integração Stripe seguem planejadas. Descontos de compra e seed de catálogo foram removidos.

## Catálogo de documentação e percurso de leitura

- [Catálogo completo por categoria](docs/pt-BR/index.md)
- [Checklist da revisão e lacunas](docs/pt-BR/operations/completion-checklist.md)

Leia propósito/setup, arquitetura e contratos, segurança/falhas, testes/evidência e implantação/recuperação local. Este projeto é independente no portfólio; procedimentos runtime documentados não foram executados na revisão de 2026-10-10.

## Documentação

- [Decisões de arquitetura](docs/pt-BR/adr/architecture-decisions.md)
- [Arquitetura](docs/pt-BR/architecture/overview.md)
- [Dependências de desenvolvimento e recuperação](docs/pt-BR/docker/development.md)
- [Docker e configuração](docs/pt-BR/docker/runtime.md)
- [Relatório histórico da reestruturação](docs/pt-BR/operations/historical-refactor-report.md)
- [Escopo e próximos passos](docs/pt-BR/architecture/roadmap.md)
- [Instalação e execução](docs/pt-BR/guides/setup.md)
- [Testes](docs/pt-BR/testing/strategy.md)
- [Resultados de validação](docs/pt-BR/testing/verification.md)
- [Ferramentas](docs/pt-BR/guides/toolchain.md)

[Licença](../../../../payment-reconciliation-lab/LICENSE)

## Início rápido e escopo

Em clone novo, instale Docker/Compose, copie o exemplo e configure senha privada do banco antes de iniciar:

```sh
cp .env.example .env
# Configure private local credentials before starting.
docker compose up --build -d --wait --wait-timeout 180
```

UI: http://localhost:4200/products; API: http://localhost:8080/api/v1/products. Preserve DEV_SEED_ENABLED=false. Armazenamento existente exige a transição documentada; startup aplica migrations. O escopo atual continua sendo catálogo; pagamentos são planejados.

Em checkout existente, atualize a configuração deliberadamente sem sobrescrever o arquivo local.

[Instalação, fluxo de execução, limites operacionais e entrevista do projeto](docs/pt-BR/guides/implementation-study.md). Comandos são orientação; esta manutenção documental não executou testes da aplicação.

<!-- collection entry -->
## Coleção Engineering Library

[Biblioteca](../../index.md) | [English](docs/en/index.md) | [Português brasileiro](docs/pt-BR/index.md) | [Entrevista](docs/pt-BR/technical-interview/index.md) | [Proveniência](docs/pt-BR/operations/source-review.md)

Base Spring Boot/Angular/PostgreSQL com catálogo legado somente leitura; conciliação e Stripe não estão implementados.
