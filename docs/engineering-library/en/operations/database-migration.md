# Safe database migration

On 2026-10-18, with explicit owner approval, `engineering_library_development` and `engineering_library_development_test` were renamed to `engineering_library` and `engineering_library_test`. Preflight found only Rails internal tables: development had one metadata row; test statistics reported one migration and two metadata rows. No domain tables, replication slots or prepared transactions were found. Connections and ACLs were inspected; no application sessions were connected at inspection time.

Physical files under `.dockerized-postgres/18/docker` were preserved. No cluster was reinitialized and no database was dropped. Private backups under `.local-backups/2026-10-18-database-rename/` include both custom dumps and `roles.sql` (may contain password hashes). Directory mode 0700, files 0600, ignored by Git. Both archives passed `pg_restore --list`; that verifies archive catalogs, not a restore drill.

## Procedure for another existing cluster

Run from the repository root before switching the effective name. Do not rerun the rename below in this already migrated environment. Inspect databases, tables, connections, slots, prepared transactions and ACLs first. Also inspect subscriptions and external integrations where applicable. Obtain explicit approval before renaming populated databases or interrupting services. `POSTGRES_DB` does not rename existing databases.

```sh
# Use the actual existing role; credentials stay inside the container.
docker compose exec -T postgres sh -c 'psql -U "$POSTGRES_USER" -d postgres -c "SELECT datname, datacl FROM pg_database;" -c "SELECT datname, usename, state FROM pg_stat_activity;" -c "SELECT slot_name, database FROM pg_replication_slots;" -c "SELECT gid, database FROM pg_prepared_xacts;"'
docker compose exec -T postgres sh -c 'psql -U "$POSTGRES_USER" -d engineering_library_development -c "SELECT schemaname, relname, n_live_tup FROM pg_stat_user_tables;" -c "SELECT subname FROM pg_subscription;"'
umask 077
mkdir -p .local-backups/pre-rename
docker compose exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" -Fc engineering_library_development' > .local-backups/pre-rename/development.dump
docker compose exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" -Fc engineering_library_development_test' > .local-backups/pre-rename/test.dump
docker compose exec -T postgres sh -c 'pg_dumpall -U "$POSTGRES_USER" --roles-only' > .local-backups/pre-rename/roles.sql
docker compose exec -T postgres pg_restore --list < .local-backups/pre-rename/development.dump
docker compose exec -T postgres pg_restore --list < .local-backups/pre-rename/test.dump
# After approval, stop writers; ALTER refuses remaining active connections.
docker compose stop frontend backend
docker compose exec -T postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d postgres -c "ALTER DATABASE engineering_library_development RENAME TO engineering_library;"'
docker compose exec -T postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d postgres -c "ALTER DATABASE engineering_library_development_test RENAME TO engineering_library_test;"'
# Set only POSTGRES_DB and the three host ports in local .env; preserve secrets.
docker compose config --quiet
docker compose up -d
docker compose exec -T postgres sh -c 'psql -U "$POSTGRES_USER" -d engineering_library -c "SELECT current_database();"'
curl --fail http://localhost:3098/up
curl --fail http://localhost:3099
```

## Recovery

If only one rename completes, keep applications stopped and inspect both actual names before continuing or rolling back. To roll back without discarding data, stop writers, verify no connections, rename each database back with `ALTER DATABASE ... RENAME TO ...`, restore only `POSTGRES_DB` in configuration and recreate applications. Destination names must be free. Do not terminate unknown sessions automatically.

For a logical recovery drill, create an isolated database with `createdb`, restore using `pg_restore --exit-on-error --no-owner -d <isolated_database>` and compare schemas and counts. Never restore over the live database. Recreate roles from `roles.sql` only after review in an isolated cluster; that file is sensitive. Back up new writes before any rollback. Never clean volumes or edit PostgreSQL files directly.

DBeaver: PostgreSQL driver, host `localhost`, port `5499`, database `engineering_library`, preserved local username, password inspected privately. Local SSL is not configured. Connectivity from the DBeaver client requires manual verification.
