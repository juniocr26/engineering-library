# ENV — engineering-library

[Project index](../index.md)

Referência verificada em 2026-10-18 a partir dos arquivos locais seguros. Valores reais de `.env` não foram usados nesta referência. Exemplos com segredos usam `<secret>`. Não publique senhas, tokens ou URLs com credenciais; preserve credenciais do cluster existente. Variáveis do shell podem sobrepor o arquivo de ambiente do Compose.

## Entradas do Docker Compose

Cada linha descreve o comportamento **na interpolação Compose**, antes da aplicação. `:-` aplica o padrão tanto na ausência como no vazio; `:?` rejeita ambos. Um padrão vazio é intencionalmente permitido nessa camada. A aceitação final pelo consumidor é detalhada abaixo.

[Configuração fonte](../../../../../../compose.yaml)

| Variável | Responsabilidade / consumidor | Obrigatória | Ausente | Vazia | Exemplo seguro / padrão | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| `POSTGRES_USER` | Conexão e inicialização PostgreSQL / banco e backend | sim | erro Compose | erro Compose | `Set POSTGRES_USER` | L6 |
| `POSTGRES_PASSWORD` | Conexão e inicialização PostgreSQL / banco e backend | sim | erro Compose | erro Compose | `<secret>` | L7 |
| `POSTGRES_DB` | Conexão e inicialização PostgreSQL / banco e backend | sim | erro Compose | erro Compose | `Set POSTGRES_DB` | L8 |
| `POSTGRES_PORT` | Porta de rede / Compose e serviço correspondente | não | padrão | padrão | `5499` | L11 |
| `LOCAL_UID` | Permissões de arquivos / build ou usuário do container | não | padrão | padrão | `1000` | L21 |
| `LOCAL_GID` | Permissões de arquivos / build ou usuário do container | não | padrão | padrão | `1000` | L21 |
| `SECRET_KEY_BASE` | secret key base | sim | erro Compose | erro Compose | `<secret>` | L28 |
| `BACKEND_PORT` | Porta de rede / Compose e serviço correspondente | não | padrão | padrão | `3098` | L37 |
| `FRONTEND_PORT` | Porta de rede / Compose e serviço correspondente | não | padrão | padrão | `3099` | L59 |

## Consumidores e diferenças fora do Compose

| Variável | Consumidor | Ausente / padrão | Vazia (execução direta) | Fonte |
| --- | --- | --- | --- | --- |
| `POSTGRES_HOST` | Rails DB | postgres | host vazio passado ao adaptador; sem fallback ENV | [database.yml](../../../../../../backend/config/database.yml) |
| `POSTGRES_USER` | Rails DB | KeyError (obrigatória) | usuário vazio passado ao adaptador; autenticação pode falhar | [database.yml](../../../../../../backend/config/database.yml) |
| `POSTGRES_PASSWORD` | Rails DB | KeyError (obrigatória) | senha vazia passada ao adaptador; Compose rejeita | [database.yml](../../../../../../backend/config/database.yml) |
| `POSTGRES_DB` | Rails DB | KeyError (obrigatória) | banco vazio passado ao adaptador; Compose rejeita | [database.yml](../../../../../../backend/config/database.yml) |
| `RAILS_MAX_THREADS` | Rails/Puma | pool do banco 5; Puma 3 | vazio preservado; contagem de threads inválida | [puma.rb](../../../../../../backend/config/puma.rb) |
| `PORT` | Puma | 3000 | vazio preservado; CLI -p 3000 tem precedência no Docker | [puma.rb](../../../../../../backend/config/puma.rb) |
| `PIDFILE` | Puma | não definido | Ruby considera vazio verdadeiro; caminho vazio passado ao Puma | [puma.rb](../../../../../../backend/config/puma.rb) |
| `DATABASE_URL` | Rails production | nil; configuração compartilhada permanece | URL vazia preservada no ERB; resolução do adaptador não verificada | [database.yml](../../../../../../backend/config/database.yml) |
| `BACKEND_URL` | API de catálogo no servidor Next | http://backend:3000 | vazio é mantido; fetch falha e catálogo mostra indisponibilidade | [frontend/lib/catalog.ts](../../../../../../frontend/lib/catalog.ts) |
| `SECRET_KEY_BASE` | Rails / Compose | erro Compose | Compose error; use generated secret, never publish | [compose.yaml](../../../../../../compose.yaml) |
| `CI` | Rails tests | eager_load false | present? false; valor não vazio habilita eager loading | [environments/test.rb](../../../../../../backend/config/environments/test.rb) |
| `RAILS_ENV` | Rails runtime | Compose define development | execução direta fora do Compose: comportamento do framework não verificado | [compose.yaml](../../../../../../compose.yaml) |
| `BUNDLE_GEMFILE` | Ruby boot | backend/Gemfile | Ruby ||= preserva vazio; seleção de arquivo pode falhar | [boot.rb](../../../../../../backend/config/boot.rb) |

As variáveis sem marcação obrigatória são opcionais. Valores vazios de host/usuário/banco não têm fallback Ruby: são passados ao adaptador e podem causar falha de conexão. `BACKEND_URL` vazio causa falha da consulta e exibe indisponibilidade; sua ausência usa o endereço interno. `RAILS_MAX_THREADS` e `PORT` vazios não são suportados como números. `CI` vazio desativa eager loading. `DATABASE_URL` em produção exige validação específica do adaptador; não foi inventado um fallback.

`POSTGRES_PORT=5499` é exclusivamente a porta publicada no host; Rails usa `postgres:5432`. Compose fixa `BACKEND_URL=http://backend:3000`, `RAILS_ENV=development`, `CATALOG_ROOT=/docs/projects` (Rails), `DOCUMENTATION_ROOT=/docs/projects` (Next.js), `PGDATA=/var/lib/postgresql/18/docker`, `HOME=/tmp`, `BUNDLE_PATH=/usr/local/bundle`, `BUNDLE_APP_CONFIG=/tmp/bundle-config`, `npm_config_cache=/tmp/npm-cache` e `NEXT_TELEMETRY_DISABLED=1`; essas configurações não são novas entradas de `.env`. Dependências e cache usam diretórios graváveis. O fetch Next ocorre no servidor, portanto não exige mudança de CORS. `POSTGRES_DB` só inicializa bancos em clusters novos. Veja [migração](../operations/database-migration.md).

## Raízes dos arquivos do catálogo — 2026-10-19

`CATALOG_ROOT` seleciona opcionalmente o diretório Rails; o padrão é `../docs/projects` relativo à raiz Rails. `DOCUMENTATION_ROOT` seleciona a coleção Next; o padrão usa o mesmo caminho irmão relativo ao diretório de execução. Compose fixa esta última em `/docs/projects` e mantém a coleção somente leitura no Rails e gravável no frontend para manutenção explícita. Override vazio é mantido, sem fallback; use diretório explícito válido ou omita a variável. Os caminhos devem apontar para a mesma coleção pública pretendida. Não autorizam leitura runtime de fontes dos repositórios irmãos. `BACKEND_URL` acessa o catálogo no servidor com timeout de cinco segundos; liveness `/up` tem contrato separado.

No frontend existente, Compose define `BROWSER_BASE_URL=http://localhost:3000` e `BOOK_READER_URL=http://localhost:3000`. A imagem define `PLAYWRIGHT_MODULE=/opt/browser/node_modules/playwright` e `PLAYWRIGHT_BROWSERS_PATH=/opt/playwright`. `PLAYWRIGHT_EXECUTABLE_PATH` só é necessário para selecionar outro executável dentro do container. Essas variáveis não exigem Node ou navegador no host.
