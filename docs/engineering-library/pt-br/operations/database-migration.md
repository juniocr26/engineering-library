# Migração segura do banco

Em 2026-10-18, com aprovação explícita do proprietário, os bancos `engineering_library_development` e `engineering_library_development_test` foram renomeados para `engineering_library` e `engineering_library_test`. A inspeção anterior encontrou somente tabelas internas Rails: desenvolvimento com uma linha de metadados; teste com estatísticas de uma migração e duas linhas de metadados. Nenhuma tabela de domínio, slot de replicação ou transação preparada foi encontrada. Foram inspecionadas conexões e ACLs; não havia sessões de aplicação conectadas no instante da consulta.

Os arquivos físicos em `.dockerized-postgres/18/docker` foram preservados. Nenhum cluster foi reinicializado e nenhum banco foi excluído. Backups privados em `.local-backups/2026-10-18-database-rename/` contêm os dois dumps custom e `roles.sql` (pode conter hashes de senha). Diretório 0700, arquivos 0600, ignorados no Git. Os dois arquivos passaram por `pg_restore --list`; isso verifica o catálogo do arquivo, mas não substitui um teste de restauração.

## Procedimento para outro cluster existente

Execute a partir da raiz do repositório, antes de mudar o nome efetivo. Não execute a renomeação abaixo novamente neste ambiente já migrado. Primeiro consulte os bancos, tabelas, conexões, slots, transações preparadas e ACLs. Verifique também assinaturas de replicação e integrações externas, se existentes. Se houver dados ou interrupção de serviço, obtenha aprovação explícita antes da renomeação. `POSTGRES_DB` não renomeia bancos existentes.

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

## Recuperação

Se apenas uma renomeação tiver concluído, mantenha os aplicativos parados e confirme os dois nomes reais antes de continuar ou reverter. Para reverter sem descartar dados, pare os escritores, verifique ausência de conexões e renomeie cada banco de volta usando `ALTER DATABASE ... RENAME TO ...`; restaure somente `POSTGRES_DB` na configuração e recrie os aplicativos. Os nomes de destino precisam estar livres. Não encerre sessões desconhecidas automaticamente.

Para testar recuperação lógica, crie um banco isolado com `createdb`, restaure com `pg_restore --exit-on-error --no-owner -d <isolated_database>` e compare esquema e contagens. Não restaure sobre o banco ativo. Papéis podem ser recriados a partir de `roles.sql` somente após revisão, em um cluster isolado; esse arquivo contém dados sensíveis. Faça backup também após novas gravações antes de qualquer reversão. Não use limpeza de volumes nem altere arquivos PostgreSQL diretamente.

DBeaver: driver PostgreSQL, host `localhost`, porta `5499`, banco `engineering_library`, usuário preservado do ambiente local, senha consultada privadamente. SSL local não está configurado. A conectividade pelo cliente DBeaver precisa ser verificada manualmente.
