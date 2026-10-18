# ENV — payment-reconciliation-lab

[Project index](../index.md)

Verified on 2026-10-18 from safe local source files. Actual `.env` values were not used in this reference. Secret examples use `<secret>`. Never publish passwords, tokens or credential-bearing URLs; preserve existing cluster credentials. Shell variables can override the Compose environment file.

## Docker Compose inputs

Each row describes behavior **at Compose interpolation**, before the application. `:-` uses the default for both missing and empty values; `:?` rejects both. An empty default is intentionally permitted at this layer. Final consumer behavior is described below.

[Source configuration](../../../../../../../payment-reconciliation-lab/docker-compose.yml)

| Variable | Responsibility / consumer | Required | Missing | Empty | Safe example / default | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `POSTGRES_DB` | PostgreSQL connection and initialization / database and backend | no | default | default | `payment_reconciliation_lab` | L6 |
| `POSTGRES_USER` | PostgreSQL connection and initialization / database and backend | no | default | default | `payment_reconciliation_lab` | L7 |
| `POSTGRES_PASSWORD` | PostgreSQL connection and initialization / database and backend | yes | Compose error | Compose error | `<secret>` | L8 |
| `POSTGRES_HOST_PORT` | Network port / Compose and corresponding service | no | default | default | `5432` | L10 |
| `APP_UID` | File ownership / build or container user | no | default | default | `10001` | L24 |
| `APP_GID` | File ownership / build or container user | no | default | default | `10001` | L25 |
| `APP_ENV` | app env | no | default | default | `dev` | L27 |
| `ALLOWED_ORIGINS` | allowed origins | no | default | default | `http://localhost:4200` | L31 |
| `DEV_SEED_ENABLED` | dev seed enabled | no | default | default | `false` | L32 |
| `BACKEND_HOST_PORT` | Network port / Compose and corresponding service | no | default | default | `8080` | L34 |
| `FRONTEND_HOST_PORT` | Network port / Compose and corresponding service | no | default | default | `4200` | L46 |
| `POSTGRES_VOLUME_NAME` | PostgreSQL connection and initialization / database and backend | no | default | default | `payment-reconciliation-lab_db_data` | L61 |

## Spring outside Compose

Missing `APP_ENV` uses `default`; Compose uses `dev`. Empty survives Spring placeholder resolution (exact profile activation unverified). Optional `DB_URL` defaults when absent to `jdbc:postgresql://localhost:5432/${POSTGRES_DB:payment_reconciliation_lab}`; empty reaches the datasource and is not a valid JDBC URL. Missing `POSTGRES_USER` and `POSTGRES_DB` default to `payment_reconciliation_lab`; empty does not use those Spring defaults. `POSTGRES_PASSWORD` is required by Compose; directly, missing has no default and empty may fail authentication. Empty `ALLOWED_ORIGINS` removes usable entries; absent directly defaults to `http://localhost:4200`. Keep explicit origins aligned with the frontend port. Missing `DEV_SEED_ENABLED` uses false; true deliberately fails because reconciliation fixtures do not exist. Spring empty-to-boolean conversion was not verified. `STRIPE_SECRET_KEY` appears in the template but has no implemented consumer: missing, empty or set does not enable Stripe. Keep it private. `POSTGRES_VOLUME_NAME` selects persistent storage; changing it does not migrate data.

[Spring configuration](../../../../../../../payment-reconciliation-lab/backend/src/main/resources/application.yml) · [Seed guard](../../../../../../../payment-reconciliation-lab/backend/src/main/java/com/aurorabakery/configuration/DevelopmentSeedConfiguration.java)
