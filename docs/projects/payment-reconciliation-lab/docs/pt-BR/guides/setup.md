# Instalação e execução

## Desenvolvimento com Docker

Instale Docker com Compose v2. Em um clone novo:

```sh
if [ ! -e .env ]; then cp .env.example .env; fi
# Edite .env: use uma senha local de desenvolvimento.
docker compose config --quiet
docker compose up --build -d --wait --wait-timeout 180
```

Em um checkout existente, atualize `.env` conforme as variáveis documentadas, sem sobrescrevê-lo. Aplicação: http://localhost:4200/products. API: http://localhost:8080/api/v1/products. Swagger local: http://localhost:8080/swagger-ui/index.html. Readiness: http://localhost:8080/actuator/health/readiness.

Migrações Flyway preservadas; Hibernate valida o schema. Seed de catálogo e política de compra removidos. Mantenha `DEV_SEED_ENABLED=false`; fixtures de reconciliação e Stripe ainda não foram implementados. Antes de iniciar um checkout existente, siga [a transição preservando dados](../docker/runtime.md).

```sh
docker compose ps
docker compose logs --tail=100
docker compose stop
```



[Testes](../testing/strategy.md).


[Dependências persistidas no host e recuperação](../docker/development.md). A inicialização base executa migrações; a flag do seed removido deve permanecer false. Use o override existente para desabilitar Flyway ao preservar um banco inicializado. Nunca execute testes de escrita contra dados da aplicação.
