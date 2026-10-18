# Testing


No host Java or Node is required for the Docker workflow:

```sh
docker build --target build -t payment-reconciliation-lab-backend-tests ./backend
docker run --rm payment-reconciliation-lab-backend-tests ./mvnw -B -ntp verify
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -e TESTCONTAINERS_HOST_OVERRIDE=host.docker.internal payment-reconciliation-lab-backend-tests ./mvnw -B -ntp verify -Pintegration
docker compose run --rm --no-deps frontend npm run build
docker compose run --rm --no-deps frontend npm test
```

The integration runner needs access to a local Docker daemon and uses a separate disposable PostgreSQL container; it does not modify the application database. With JDK 25 and Node 22.23.3 on the host, use `./mvnw verify -Pintegration` in `backend` and `npm ci && npm run build && npm test` in `frontend`.


When running unit tests in the development backend, use `docker compose -f docker-compose.yml -f compose.development.yaml exec -T -e APP_ENV=default backend sh ./mvnw -B -ntp test`. Otherwise inherited `APP_ENV=dev` changes the OpenAPI security assertion. The integration suite owns a new Testcontainers PostgreSQL instance, but its `@BeforeEach` deletes test rows; never point it at an existing database. Integration tests were not rerun in this documentation pass.

## Current source inventory — 2026-10-09

Source inspection finds 7 backend unit/API test methods (5 ProductApiTest, 2 DevelopmentSeedConfigurationTest), 5 opt-in ProductPostgresIT methods and 4 Angular cases. This is an inventory, not a passing result. HTTP fakes exercise DTOs, empty/error responses, blocked routes and CORS; seed tests assert default disablement and explicit rejection of the retired flag. PostgreSQL cases exercise both migrations, constraints, visibility/order, preserved hidden rows and health/dev docs. No purchase-policy, repeatable-seed or reconciliation/Stripe test remains. Historical counts in verification/refactor reports describe the earlier checkout. No tests, builds, dependency installation or services were run during this audit.
