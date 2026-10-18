# ENV — go-image-optimizer

[Project index](../index.md)

Referência verificada em 2026-10-18 a partir dos arquivos locais seguros. Valores reais de `.env` não foram usados nesta referência. Exemplos com segredos usam `<secret>`. Não publique senhas, tokens ou URLs com credenciais; preserve credenciais do cluster existente. Variáveis do shell podem sobrepor o arquivo de ambiente do Compose.

## Entradas do Docker Compose

Cada linha descreve o comportamento **na interpolação Compose**, antes da aplicação. `:-` aplica o padrão tanto na ausência como no vazio; `:?` rejeita ambos. Um padrão vazio é intencionalmente permitido nessa camada. A aceitação final pelo consumidor é detalhada abaixo.

[Configuração fonte](../../../../../../../go-image-optimizer/docker-compose.yml)

| Variável | Responsabilidade / consumidor | Obrigatória | Ausente | Vazia | Exemplo seguro / padrão | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| `BACKEND_PORT` | Porta de rede / Compose e serviço correspondente | não | padrão | padrão | `8080` | L9 |
| `BACKEND_URL` | backend url | não | padrão | padrão | `http://backend:8080` | L32 |
| `FRONTEND_PORT` | Porta de rede / Compose e serviço correspondente | não | padrão | padrão | `3000` | L36 |

## Comportamento da aplicação

`PORT` é opcional no Go: ausente ou vazio usa `8080`; valores não numéricos ou fora de 1–65535 falham. Compose fixa `8080` no backend e `3000` no Next. `BACKEND_URL` na execução direta usa `??`: ausência usa `http://localhost:8080`, vazio é preservado e pode produzir URL inválida; no Compose ambos usam `http://backend:8080`. Não coloque credenciais nessa URL. `HOSTNAME=0.0.0.0` permite acesso no container. `NODE_ENV=development` e `NEXT_TELEMETRY_DISABLED=1` são fixos no perfil dev. `CGO_ENABLED=1` habilita codecs no backend-test. `REAL_IMAGE_FIXTURES_DIR` é opcional nos testes: vazio/ausente procura fixtures nos caminhos do teste; `TESTDATA_DIR` é outra entrada opcional de fixtures em preview_test.go; vazio/ausente usa a busca local. Não são segredos nem entradas de produção.

[Go config](../../../../../../../go-image-optimizer/backend/internal/config/config.go) · [Next proxy](../../../../../../../go-image-optimizer/frontend/app/api/images/forward-image-request.ts)
