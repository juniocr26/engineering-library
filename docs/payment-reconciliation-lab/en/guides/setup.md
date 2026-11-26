# Setup and execution

## Development with Docker

Install Docker with Compose v2. From a fresh clone:

```sh
if [ ! -e .env ]; then cp .env.example .env; fi
# Edit .env: use a local development password.
docker compose config --quiet
docker compose up --build -d --wait --wait-timeout 180
```

For an existing checkout, update `.env` from the documented variables rather than overwriting it. Application: http://localhost:4200/products. API: http://localhost:8080/api/v1/products. Local Swagger: http://localhost:8080/swagger-ui/index.html. Readiness: http://localhost:8080/actuator/health/readiness.

Flyway migrations are unchanged; Hibernate validates the schema. The catalog seed and purchase policy are retired. Keep `DEV_SEED_ENABLED=false`; reconciliation fixtures and Stripe are not implemented. Before starting an existing checkout, follow [the data-preserving identity transition](../docker/runtime.md).

```sh
docker compose ps
docker compose logs --tail=100
docker compose stop
```



[Testing](../testing/strategy.md).


[Host-persisted development dependencies and recovery](../docker/development.md). Base startup runs migrations; the retired seed flag must remain false. Use the existing development override to disable Flyway when preserving an initialized database. Never run database-writing tests against application data.
