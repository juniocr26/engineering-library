# Engineering Library API

Rails API foundation. `GET /up` is the standard Rails boot health endpoint.

Use the repository-root Compose configuration. See [development documentation](../docs/engineering-library/en/guides/application-development.md) for setup, database preparation, testing and dependency recovery. Business services and AI integrations are future work.

## Local dependencies / Dependências locais

The existing Compose services install physical dependency sources in `frontend/node_modules` and `backend/vendor/bundle`. All runtimes and package managers stay in Docker. See [installation, refresh and VS Code limitations](../docs/engineering-library/en/guides/application-development.md#local-dependency-sources-docker-development).

Os serviços existentes do Compose instalam fontes físicas em `frontend/node_modules` e `backend/vendor/bundle`. Runtimes e gerenciadores permanecem no Docker. Consulte [instalação, atualização e limitações do VS Code](../docs/engineering-library/pt-br/guides/application-development.md#fontes-locais-das-dependências-desenvolvimento-docker).
