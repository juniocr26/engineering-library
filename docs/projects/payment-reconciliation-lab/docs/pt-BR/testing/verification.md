# Verificação da reestruturação — 2026-10-05

[English](../../en/testing/verification.md) | [Português](verification.md)

Este é o registro da verificação anterior da reestruturação, não da revisão documental atual. Foi usado Docker Desktop com Compose v2 em macOS ARM64. Java 17 do host e ausência de Node foram contornados com imagens Java 25/Node 22 do repositório. Dependências fixadas foram preservadas.

| Verificação | Resultado registrado |
| --- | --- |
| `docker compose config --quiet` | PASS |
| `docker compose build` novo | PASS, ambas as imagens |
| `docker compose up --build -d --wait --wait-timeout 180` | PASS, db/backend/frontend saudáveis |
| Volume/rede novos | `aurora-bakery_db_data` e `aurora-bakery_default` |
| Flyway/Hibernate | PASS, V1/V2 aplicadas, schema validado |
| Consulta ao banco | PASS, migrações bem-sucedidas; dois produtos disponíveis e um temporariamente indisponível |
| Readiness com banco | PASS, UP |
| Frontend `/products` | HTTP 200 |
| Proxy Angular `/api/v1/products` | PASS, resposta igual à API com três produtos demo |
| Build produção Angular | PASS, bundle lazy do catálogo |
| Testes Angular | PASS, 4 testes |
| Testes backend | PASS, 9 unidade/API e 6 integração PostgreSQL, sem falhas/skips |
| Logs | Sem erros de startup; restart normal de inicialização PostgreSQL e avisos dev/toolchain |

Não se afirma verificação de renderização completa no navegador, checkout autenticado, pagamento, provisionamento ADMIN ou deploy de produção. Esses fluxos não existem. Catálogo público de leitura não precisa de bootstrap ADMIN. V1 mantém terminologia histórica para integridade da migração.

## Comandos executados na verificação anterior

```sh
docker compose config --quiet
docker compose build
docker compose up --build -d --wait --wait-timeout 180
docker compose ps
docker compose logs --tail=60
docker build --target build -t aurora-bakery-backend-tests ./backend
docker compose run --rm --no-deps frontend npm test
docker compose run --rm --no-deps frontend npm run build
```

Testes backend usaram socket Docker e `TESTCONTAINERS_HOST_OVERRIDE=host.docker.internal`, executando `./mvnw -B -ntp verify -Pintegration` na imagem build-stage com fonte final montada somente para leitura. O README documenta reconstrução da imagem para clones novos. Smoke checks SQL/HTTP usaram `docker compose exec -T db` (psql) e `docker compose exec -T frontend` (Node fetch), conferindo migrações, igualdade API/proxy e readiness.

## Revisão documental de arquitetura — 2026-10-05

Esta revisão separada executou a fonte atual dos testes unidade/API na imagem build-stage Java 25 existente, com mount somente leitura: `docker run --rm -v "$PWD/backend/src:/workspace/src:ro" aurora-bakery-backend-tests ./mvnw -B -ntp verify`. Os 9 testes passaram. A tentativa inicial sem rede falhou porque a distribuição Maven Wrapper não estava disponível na imagem; a repetição com downloads habilitados passou. Nesta revisão não foram executados perfil de integração, suíte frontend, browser ou stack Compose. Container descartável removido; banco/volume da aplicação e ambiente real não foram montados. Os resultados completos anteriores acima são históricos.

## Validação documental — 2026-10-06

Não havia containers em execução antes deste projeto. `docker compose -f docker-compose.yml -f compose.development.yaml config --quiet` passou. Os mesmos arquivos com `up -d` iniciaram db/backend/frontend, com Flyway e seed desabilitados e Hibernate em validate. Readiness, API direta de produtos, frontend `/products` e API pelo proxy retornaram HTTP 200 após prontidão (uma consulta antecipada falhou durante a inicialização do backend). `exec -T frontend npm test` passou 4 testes. Backend `exec -T backend sh ./mvnw -B -ntp test` falhou inicialmente em 1 de 9 por herdar `APP_ENV=dev`; `exec -T -e APP_ENV=default backend sh ./mvnw -B -ntp test` passou todos os 9. Nenhum código da aplicação foi alterado. Integração e build de produção não foram reexecutados. Nenhuma verificação escreveu no banco. `stop frontend backend db` parou todos os serviços iniciados aqui, preservando containers e volumes. Pares de idiomas e links/âncoras Markdown locais foram conferidos.


## Transição de identidade da infraestrutura — 2026-10-09

Retidos: toolchains, serviços/rede, portas/origens/UIDs, migrações aplicadas e healthcheck herdado do Dockerfile. Catálogo somente leitura permanece temporariamente. Adaptados: identidade Compose, imagens/labels/cache Maven, nome Spring, projeto/pacote/título Angular, `.env` real e exemplo, documentação bilíngue e override de volume externo. Removidos: política de compra, role sem uso, bindings/validação/testes de desconto, runner e SQL de seed de catálogo. Fixtures de reconciliação e Stripe adiados; STRIPE_SECRET_KEY vazio é reserva sem efeito atual. Namespace Java/group Maven continuam `com.aurorabakery`; migrações e relatórios históricos preservam referências anteriores. Não há CI workflow versionado, Makefile ou exemplos adicionais de ambiente; hooks de modernização não sobrepõem Compose.

Aprovados: resolução silenciosa de Compose base e overrides; defaults de instalação nova consistentes; `.env` ignorado/não versionado; ausência de variável/binding de desconto; `git diff --check`; builds das duas imagens. Backend: 7 testes unidade/API com Java 25, fonte em cópia temporária. Angular: 4 testes e build de produção na imagem final. Maven offline falhou por cache incompleto; repetição online passou. Build inicial interrompido após go-offline e concluído na repetição usando cache.

Runtime: frontend/backend antigos parados antes do backup lógico protegido em `/tmp/payment-reconciliation-lab-backups/before-transition.dump`; listagem do arquivo verificada; banco antigo parado antes de iniciar novo. `up --wait` confirmou os três serviços saudáveis. Mount usa `aurora-bakery_db_data`; fingerprints ordenados de todas as linhas de produtos e histórico Flyway coincidem antes/depois, preservando três produtos e duas migrações. Readiness, HTTP/título Angular e proxy API responderam 200. Containers antigos parados, novos em execução; nenhum volume excluído/prune executado. Backup em `/tmp` é temporário; copie privadamente para armazenamento durável se necessário.

Pendente: suíte Testcontainers não executada. Revisão automática rejeitou montagem do socket Docker por conceder controle amplo do daemon; unidade executada sem socket. Após aprovação explícita, executar comando de integração em [testing](strategy.md), sempre com bancos descartáveis, nunca banco da aplicação. Override de desenvolvimento apenas resolvido; rollback e restore documentados, sem execução. Stripe/reconciliação não validados. npm reportou 5 vulnerabilidades (3 high, 2 critical); versões não alteradas nesta transição.

## Auditoria documental estática — 2026-10-09

Arquitetura, decisões, roadmap e setup alinhados ao catálogo de leitura, remoção de pricing/vocabulário de identidade e rejeição da flag de seed. Inventário: 7 métodos unitários/API, 5 PostgreSQL opt-in e 4 Angular; não é novo resultado aprovado. Reconciliação/Stripe planejados, chave reservada sem binding/passagem Compose. Não foram executados Docker, builds, testes, inspeção de banco/volume, migração ou transição/backup. Estado de serviços anterior descreve aquela transição, não estado Docker atual.

Checagens estáticas de links/âncoras, fences, pares de idioma e SHA-256 para alterações somente documentais estão na revisão de entrevista (relatório compartilhado anterior não incluído no catálogo atual). Arquivos reais de ambiente e backups sensíveis não foram lidos/alterados.
