# Ambiente Docker de desenvolvimento

[English](../../en/docker/runtime.md) | [Português](runtime.md)

## Identidade e configuração

Projeto Compose: `payment-reconciliation-lab`; serviços `db`, `backend`, `frontend` preservados, com nomes de containers gerados. Imagens e labels atualizados; cache Maven `payment-reconciliation-lab-maven`. Backend executa como `app`, com UID/GID configuráveis. Hostnames internos continuam `db:5432` e `http://backend:8080`. Healthcheck de readiness herdado do Dockerfile inclui o banco; frontend aguarda backend saudável. Override de desenvolvimento desabilita esse healthcheck, usa `service_started` e desabilita Flyway.

Novas instalações usam `POSTGRES_DB=payment_reconciliation_lab` e `POSTGRES_USER=payment_reconciliation_lab`. `POSTGRES_PASSWORD` continua obrigatório. `POSTGRES_VOLUME_NAME` padrão: `payment-reconciliation-lab_db_data`. Portas, origens, perfil e UID/GID foram preservados no `.env` local, que permanece ignorado pelo Git. Política de descontos, bindings, validação e testes removidos. Seed de catálogo e SQL de bootstrap removidos; `DEV_SEED_ENABLED=false`, e true impede startup até existirem fixtures de reconciliação. Registros antigos não são removidos.

Stripe ainda não tem SDK ou bindings. `STRIPE_SECRET_KEY` vazio é apenas reserva local, sem efeito atual; nomes definitivos e validação dependem da implementação futura. Nunca copie chaves reais para exemplos ou Angular, imprima ambiente resolvido ou versione `.env`.

## Transição preservando dados

Inspeção de 2026-10-09 confirmou projeto `aurora-bakery`, containers `aurora-bakery-{db,backend,frontend}-1`, volume real `aurora-bakery_db_data` em `/var/lib/postgresql/data`, banco/role `aurora_bakery`, três produtos e duas migrações aplicadas. `.dockerized-postgres` não é o mount ativo e permanece intocado.

O `.env` local reutiliza esse volume e mantém banco, usuário e senha existentes. Variáveis de inicialização não renomeiam bancos ou roles já criados. Use `compose.existing-db.yaml` para exigir volume externo existente em vez de criar um vazio. Não monte o mesmo volume em dois bancos em execução. Pare todos os serviços antigos antes de iniciar os novos nas mesmas portas. Não exclua volumes nem execute prune ou shutdown com remoção de volumes.

`COMPOSE_PROJECT_NAME` não estava no `.env` ou shell inspecionados. Flags `-p` só aparecem no procedimento para parar explicitamente o projeto antigo. Variáveis exportadas e flags podem sobrepor `name`; `COMPOSE_FILE` também altera arquivos carregados. Confira seu shell/automação. A troca de projeto não renomeia containers antigos automaticamente.

Siga os [comandos completos de inspeção, backup, transição, verificação e rollback](../../en/docker/runtime.md), partindo da raiz deste repositório. Antes da troca: valide com `config --quiet`, construa imagens, pare frontend/backend antigos, faça backup lógico com `pg_dump`, depois pare o banco antigo. Inicie com `docker compose -f docker-compose.yml -f compose.existing-db.yaml up -d --wait --wait-timeout 180`. Compare mount, registros e histórico Flyway; teste readiness e `/api/v1/products` pelo frontend. Para rollback, pare primeiro os três serviços novos e só então reinicie containers antigos, aguardando saúde de cada dependência.

Instalações novas seguem [setup](../guides/setup.md), sem override externo. Dependências: [guia de desenvolvimento](development.md). Evidência atual: [verificação](../testing/verification.md); resultados anteriores são históricos.
