# Catálogo de documentação: go-image-optimizer

[Introdução do projeto](../../README.pt-BR.md) | [Outro idioma](../en/index.md)

Percurso: propósito/setup → arquitetura/contratos → segurança/falhas → testes/evidência → operações. Na biblioteca: catálogo/dossiê → entrevista por projeto → fundamentos → falhas. Marcos/refactors/handoff históricos descrevem datas originais; revisão/checklist explica escopo atual.

## architecture

Componentes, fluxos e fronteiras implementadas.

- [Arquitetura](architecture/overview.md)

## adr

Decisões e consequências; IDs/histórico preservados.

- [ADR 001: Codecs nativos de imagem](adr/001-native-image-codecs.md)

## guides

Setup, pré-requisitos e procedimentos de leitura.

- [Go Image Optimizer](guides/project-guide.md)

## testing

Estratégia, inventários e evidências datadas.

- [Documentação de Testes](testing/strategy.md)
- [Validação documental — 2026-10-06](testing/verification.md)

## docker

Imagens, serviços, mounts e configuração local.

- [Desenvolvimento Docker e recuperação](docker/development.md)
- [Docker](docker/runtime.md)

## api

Contratos expostos e comportamento de clientes.

- [API de imagens e contrato do proxy](api/contracts.md)

## operations

Diagnóstico, recuperação, checklists e registros históricos.

- [go-image-optimizer: Checklist de conclusão do repositório](operations/completion-checklist.md)
- [Implantação, diagnóstico e evidência](operations/deployment-and-diagnosis.md)

## security

Autenticação, autorização, dados e recursos.

- [Limites de recursos e código nativo](security/resource-boundaries.md)

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
- [docker](docker/index.md)
- [guides](guides/index.md)
- [operations](operations/index.md)
- [security](security/index.md)
- [technical-interview](technical-interview/index.md)
- [testing](testing/index.md)
