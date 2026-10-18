# Catálogo de documentação: payment-reconciliation-lab

[Introdução do projeto](../../README.pt-BR.md) | [Outro idioma](../en/index.md)

Percurso: propósito/setup → arquitetura/contratos → segurança/falhas → testes/evidência → operações. Na biblioteca: catálogo/dossiê → entrevista por projeto → fundamentos → falhas. Marcos/refactors/handoff históricos descrevem datas originais; revisão/checklist explica escopo atual.

## architecture

Componentes, fluxos e fronteiras implementadas.

- [Arquitetura e domínio](architecture/overview.md)
- [Escopo e estado da implementação](architecture/roadmap.md)

## adr

Decisões e consequências; IDs/histórico preservados.

- [Decisões de Arquitetura e Trade-offs](adr/architecture-decisions.md)

## guides

Setup, pré-requisitos e procedimentos de leitura.

- [Instalação e execução](guides/setup.md)
- [Ferramentas e versões](guides/toolchain.md)

## testing

Estratégia, inventários e evidências datadas.

- [Testes](testing/strategy.md)
- [Verificação da reestruturação — 2026-10-05](testing/verification.md)

## docker

Imagens, serviços, mounts e configuração local.

- [Desenvolvimento Docker e recuperação](docker/development.md)
- [Ambiente Docker de desenvolvimento](docker/runtime.md)

## database

Modelos, constraints, migrações e consistência.

- [Schema de catálogo e transição de domínio](database/catalog-and-transition.md)

## api

Contratos expostos e comportamento de clientes.

- [API e UI de catálogo implementadas](api/catalog-contract.md)

## operations

Diagnóstico, recuperação, checklists e registros históricos.

- [payment-reconciliation-lab: Checklist de conclusão do repositório](operations/completion-checklist.md)
- [Startup, implantação e fronteiras dos testes](operations/deployment-and-evidence.md)
- [Relatório da reestruturação Aurora Bakery](operations/historical-refactor-report.md)

## security

Autenticação, autorização, dados e recursos.

- [Segurança da API de leitura e futuras fronteiras de pagamento](security/read-api-boundaries.md)

Aplicabilidade e omissões estão justificadas no [checklist](operations/completion-checklist.md). Não há categorias vazias.

## Roteiro prático de implementação e entrevista

[Acompanhe uma requisição, examine falhas e pratique respostas](guides/implementation-study.md).

<!-- project-first catalog -->
## Capítulos completos da coleção

[Biblioteca](../../../../index.md) | [English](../en/index.md)

Ordem sugerida: propósito no README → guias → arquitetura e ADRs → contratos, dados e integrações → segurança → testes → operações → entrevista. Capítulos ausentes não possuem conteúdo mantido; não são funcionalidades prometidas. Cada capítulo lista todas as suas páginas.

- [adr](adr/index.md)
- [api](api/index.md)
- [architecture](architecture/index.md)
- [database](database/index.md)
- [docker](docker/index.md)
- [guides](guides/index.md)
- [operations](operations/index.md)
- [security](security/index.md)
- [faq](faq/index.md)
- [testing](testing/index.md)

- [env](env/index.md)
