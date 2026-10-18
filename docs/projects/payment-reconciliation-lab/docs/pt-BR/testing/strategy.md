# Testes


O fluxo Docker não exige Java ou Node no host:

```sh
docker build --target build -t payment-reconciliation-lab-backend-tests ./backend
docker run --rm payment-reconciliation-lab-backend-tests ./mvnw -B -ntp verify
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -e TESTCONTAINERS_HOST_OVERRIDE=host.docker.internal payment-reconciliation-lab-backend-tests ./mvnw -B -ntp verify -Pintegration
docker compose run --rm --no-deps frontend npm run build
docker compose run --rm --no-deps frontend npm test
```

O executor de integração precisa do daemon Docker local e usa um PostgreSQL descartável separado; não altera o banco da aplicação. Com JDK 25 e Node 22.23.3 no host, execute `./mvnw verify -Pintegration` em `backend` e `npm ci && npm run build && npm test` em `frontend`.


Para testes unitários no backend de desenvolvimento, use `docker compose -f docker-compose.yml -f compose.development.yaml exec -T -e APP_ENV=default backend sh ./mvnw -B -ntp test`. `APP_ENV=dev` herdado altera a asserção de segurança OpenAPI. A suíte de integração cria PostgreSQL novo via Testcontainers, mas `@BeforeEach` exclui linhas de teste; nunca a direcione a banco existente. A integração não foi reexecutada nesta revisão documental.

## Inventário atual do código — 2026-10-09

Inspeção encontra 7 métodos unitários/API de backend (5 ProductApiTest, 2 DevelopmentSeedConfigurationTest), 5 métodos opt-in ProductPostgresIT e 4 casos Angular. É inventário, não resultado aprovado. Fakes HTTP cobrem DTOs, vazio/erro, bloqueios e CORS; testes de seed verificam desabilitação padrão e rejeição da flag removida. PostgreSQL cobre duas migrações, constraints, visibilidade/ordem, linhas ocultas preservadas e health/docs dev. Não restam testes de política de compra, seed repetível ou reconciliação/Stripe. Contagens históricas referem-se ao checkout anterior. Nenhum teste, build, instalação ou serviço foi executado nesta auditoria.
