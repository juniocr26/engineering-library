# url-shortener

[English](../en/README.md) | [Português brasileiro](README.md)

Portfólio FastAPI com criação autenticada de URLs e redirecionamentos permanentes públicos. Redis gera IDs; Cassandra persiste associações; Base62 e ofuscação reversível produzem códigos curtos. Explora decisões de sistemas sem alegar capacidade de produção medida.

## Catálogo de documentação e percurso de leitura

- [Catálogo completo por categoria](index.md)
- [Checklist da revisão e lacunas](operations/completion-checklist.md)

Leia propósito/setup, arquitetura e contratos, segurança/falhas, testes/evidência e implantação/recuperação local. Este projeto é independente no portfólio; procedimentos runtime documentados não foram executados na revisão de 2026-10-10.

## Documentação

- [Arquitetura](architecture/overview.md)
- [Dependências de desenvolvimento e recuperação](docker/development.md)
- [Docker e configuração](docker/runtime.md)
- [Guia do projeto](guides/project-guide.md)
- [Coleção Postman](api/postman.md)
- [Testes](testing/strategy.md)
- [Resultados de validação](testing/verification.md)

[Licença](../../../../../Portifo%CC%81lio/url-shortener/LICENSE)

## Início rápido e escopo

Em clone novo, instale Docker/Compose, copie o exemplo e configure privadamente Basic Auth, ofuscação e credenciais do banco:

```sh
cp .env.example .env
# Configure private local credentials before starting.
docker compose build
docker compose up -d
```

API: http://localhost:8000. Startup inclui três nós Cassandra e bootstrap de roles/schema. POST /urls exige Basic Auth; GET /{short_code} é público. Coordene recuperação de contador e mapeamentos; não há transação conjunta.

Em checkout existente, atualize a configuração deliberadamente sem sobrescrever o arquivo local.

[Instalação, fluxo de execução, limites operacionais e entrevista do projeto](guides/implementation-study.md). Comandos são orientação; esta manutenção documental não executou testes da aplicação.
