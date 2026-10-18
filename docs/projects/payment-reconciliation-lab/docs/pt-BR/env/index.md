# ENV — payment-reconciliation-lab

[Project index](../index.md)

Referência verificada em 2026-10-18 a partir dos arquivos locais seguros. Valores reais de `.env` não foram usados nesta referência. Exemplos com segredos usam `<secret>`. Não publique senhas, tokens ou URLs com credenciais; preserve credenciais do cluster existente. Variáveis do shell podem sobrepor o arquivo de ambiente do Compose.

## Entradas do Docker Compose

Cada linha descreve o comportamento **na interpolação Compose**, antes da aplicação. `:-` aplica o padrão tanto na ausência como no vazio; `:?` rejeita ambos. Um padrão vazio é intencionalmente permitido nessa camada. A aceitação final pelo consumidor é detalhada abaixo.

[Configuração fonte](../../../../../../../payment-reconciliation-lab/docker-compose.yml)

| Variável | Responsabilidade / consumidor | Obrigatória | Ausente | Vazia | Exemplo seguro / padrão | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| `POSTGRES_DB` | Conexão e inicialização PostgreSQL / banco e backend | não | padrão | padrão | `payment_reconciliation_lab` | L6 |
| `POSTGRES_USER` | Conexão e inicialização PostgreSQL / banco e backend | não | padrão | padrão | `payment_reconciliation_lab` | L7 |
| `POSTGRES_PASSWORD` | Conexão e inicialização PostgreSQL / banco e backend | sim | erro Compose | erro Compose | `<secret>` | L8 |
| `POSTGRES_HOST_PORT` | Porta de rede / Compose e serviço correspondente | não | padrão | padrão | `5432` | L10 |
| `APP_UID` | Permissões de arquivos / build ou usuário do container | não | padrão | padrão | `10001` | L24 |
| `APP_GID` | Permissões de arquivos / build ou usuário do container | não | padrão | padrão | `10001` | L25 |
| `APP_ENV` | app env | não | padrão | padrão | `dev` | L27 |
| `ALLOWED_ORIGINS` | allowed origins | não | padrão | padrão | `http://localhost:4200` | L31 |
| `DEV_SEED_ENABLED` | dev seed enabled | não | padrão | padrão | `false` | L32 |
| `BACKEND_HOST_PORT` | Porta de rede / Compose e serviço correspondente | não | padrão | padrão | `8080` | L34 |
| `FRONTEND_HOST_PORT` | Porta de rede / Compose e serviço correspondente | não | padrão | padrão | `4200` | L46 |
| `POSTGRES_VOLUME_NAME` | Conexão e inicialização PostgreSQL / banco e backend | não | padrão | padrão | `payment-reconciliation-lab_db_data` | L61 |

## Spring fora do Compose

`APP_ENV` ausente usa `default`; Compose usa `dev`. Vazio é preservado pelo placeholder Spring (ativação exata de perfil não verificada). `DB_URL` é opcional e, quando ausente, usa `jdbc:postgresql://localhost:5432/${POSTGRES_DB:payment_reconciliation_lab}`; vazio é passado ao datasource e não é um URL JDBC válido. `POSTGRES_USER` e `POSTGRES_DB` ausentes usam `payment_reconciliation_lab`, mas vazios não recebem esses padrões Spring. `POSTGRES_PASSWORD` é obrigatória no Compose; em execução direta ausência não tem padrão e vazio pode falhar na autenticação. `ALLOWED_ORIGINS` vazio remove entradas úteis; fora do Compose ausência usa `http://localhost:4200`. Configure origens explícitas coerentes com a porta frontend. `DEV_SEED_ENABLED` ausente usa false; true falha propositalmente porque fixtures de conciliação não existem. Conversão Spring de vazio para boolean não foi verificada. `STRIPE_SECRET_KEY` aparece no exemplo, mas não tem consumidor implementado: vazio, ausente ou preenchido não habilita Stripe. Mantenha esse segredo privado. `POSTGRES_VOLUME_NAME` seleciona armazenamento persistente: mudar o nome não migra dados.

[Spring configuration](../../../../../../../payment-reconciliation-lab/backend/src/main/resources/application.yml) · [Seed guard](../../../../../../../payment-reconciliation-lab/backend/src/main/java/com/aurorabakery/configuration/DevelopmentSeedConfiguration.java)
