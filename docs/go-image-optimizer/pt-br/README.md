# go-image-optimizer

[English](../en/README.md) | [Português brasileiro](README.md)

Aplicação Go e Next.js para compressão, redimensionamento, conversão de formatos e fallback de prévia. O processamento ocorre por requisição, sem banco nem persistência de uploads.

## Catálogo de documentação e percurso de leitura

- [Catálogo completo por categoria](index.md)
- [Checklist da revisão e lacunas](operations/completion-checklist.md)

Leia propósito/setup, arquitetura e contratos, segurança/falhas, testes/evidência e implantação/recuperação local. Este projeto é independente no portfólio; procedimentos runtime documentados não foram executados na revisão de 2026-10-10.

## Documentação

- [001 native image codecs](adr/001-native-image-codecs.md)
- [Arquitetura](architecture/overview.md)
- [Dependências de desenvolvimento e recuperação](docker/development.md)
- [Docker e configuração](docker/runtime.md)
- [Guia do projeto](guides/project-guide.md)
- [Testes](testing/strategy.md)
- [Resultados de validação](testing/verification.md)

[Licença](../../../../../Portifo%CC%81lio/go-image-optimizer/LICENSE)

## Início rápido e escopo

Instale Docker com Compose v2 e execute neste repositório:

```sh
docker compose up --build backend frontend
```

UI: http://localhost:3000; API: http://localhost:8080. Dockerfiles constroem codecs nativos. Não há banco ou histórico persistente de uploads.

[Instalação, fluxo de execução, limites operacionais e entrevista do projeto](guides/implementation-study.md). Comandos são orientação; esta manutenção documental não executou testes da aplicação.
