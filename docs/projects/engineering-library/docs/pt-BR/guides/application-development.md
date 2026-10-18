# Desenvolvimento da aplicação

Este marco acrescenta uma API Rails, uma página Next.js inspirada na leitura de um livro e PostgreSQL. Os guias de engenharia e validadores Python existentes foram mantidos nos locais originais. Os dossiês anteriores retratam o escopo histórico das inspeções; este documento descreve a nova aplicação.

## Versões e arquitetura

Ruby 3.4.11, Rails 8.1.4, PostgreSQL 18 (`18-bookworm`, com versão principal fixada), Node 24.22.0, Next.js 16.4.2, React 19.3.1, TypeScript 5.9.3 e ESLint 9.39.5. Gemfile.lock e package-lock.json fixam as dependências. Atualizações menores da imagem PostgreSQL são intencionais. As imagens são voltadas ao desenvolvimento.

Navegador :3099 → Next.js :3000 → Rails :3000 na rede Compose → postgres :5432. Rails também fica disponível na porta 3098 do computador. O servidor Next consulta `/up`, com limite de três segundos e indicação de indisponibilidade em caso de falha. Esse endpoint verifica a inicialização do Rails; a conexão SQL é testada separadamente. Como o navegador não consulta outra origem, não é necessário middleware CORS. Mantemos as convenções Rails e adicionaremos serviços e domínio quando houver casos de uso reais. Autenticação, IA, análise de repositórios, geração de documentos e animações ainda não existem.

```text
backend/                  API Rails, config, db, test, Dockerfile, Gemfile.lock
  vendor/bundle/          gems Linux no host, ignoradas pelo Git
frontend/                 App Router, components, public, Dockerfile, package-lock.json
  node_modules/           pacotes Linux no host, ignorados pelo Git
docs/projects/engineering-library/docs/en/guides/      documentação da aplicação em inglês
docs/projects/engineering-library/docs/pt-BR/guides/   documentação da aplicação em português
tools/                    validadores existentes
.dockerized-postgres/     dados ignorados pelo Git, cluster em 18/docker
.env                      credenciais locais, ignoradas pelo Git
.env.example              modelo de configuração
compose.yaml              três serviços, sem volumes nomeados para dados/dependências
```

## Preparação e execução

Instale Docker Desktop no macOS ou Docker Engine com o plugin Compose no Linux seguindo o [guia oficial](https://docs.docker.com/engine/install/). Inicie o mecanismo Docker, permita o compartilhamento da pasta e confira as portas 3099, 3098 e 5499. Não é necessário instalar Ruby ou Node no computador.

A implementação gerou `.env` local com senha PostgreSQL aleatória de 12 caracteres ASCII alfanuméricos, incluindo maiúsculas, minúsculas e números, além de segredo Rails aleatório. Nenhum segredo entra no Git. Em um clone novo, execute `python3 tools/init_dev_env.py` (Python 3.10+); o script preserva qualquer `.env` existente. Consulte as variáveis em `.env.example`. No Linux, ajuste LOCAL_UID e LOCAL_GID para os valores de `id -u` e `id -g` antes de instalar dependências. O Docker Desktop no macOS aceita os valores padrão 1000. As pastas montadas precisam permitir escrita por esses IDs. Corrija conscientemente arquivos criados com outro usuário; não altere recursivamente os dados PostgreSQL para o usuário da aplicação. A imagem oficial gerencia a propriedade do cluster.

```sh
python3 tools/init_dev_env.py
docker compose config --quiet
docker compose up --build
# Em outro terminal, na preparação inicial e após criar migrações:
docker compose exec backend bin/rails db:prepare
# Acesse http://localhost:3099 e http://localhost:3098/up
# Encerre preservando os dados:
docker compose down
```

O PostgreSQL cria o banco de desenvolvimento ao inicializar um cluster novo. `db:prepare` prepara explicitamente o esquema e migrações; a inicialização dos contêineres não executa migrações. Rails aguarda o PostgreSQL saudável; Next aguarda Rails saudável. O código usa bind mounts e recarga de desenvolvimento. Next usa webpack para observação previsível de arquivos no Docker. Ao iniciar, o frontend executa `npm ci`; o backend confere as gems e instala as ausentes. As dependências das imagens validam o build, mas são ocultadas pelos bind mounts em execução; a inicialização as restaura fisicamente no host.

## Dependências e comandos

```sh
docker compose exec backend bundle install
docker compose exec frontend npm ci
# Recuperação quando o serviço não inicia:
docker compose run --rm --no-deps backend bundle install
docker compose run --rm --no-deps frontend npm ci
# Após alterar package.json, atualize o lockfile e reinicie:
docker compose exec frontend npm install
docker compose restart frontend
docker compose exec backend bin/rails db:migrate
docker compose exec backend bin/rails console
docker compose logs -f backend frontend postgres
```

Gems e pacotes nativos são compilados para Linux e a arquitetura do contêiner; não podem ser reutilizados diretamente pelo macOS ou por outra arquitetura. Execute os comandos dentro dos contêineres e reinstale ao mudar a plataforma. `npm ci` reconstrói node_modules; pare o frontend antes de recuperar dependências em uso. Não execute instalações concorrentes na mesma pasta. Versione os lockfiles, nunca as dependências.

## DBeaver e persistência

Use o driver PostgreSQL, host `localhost` (ou `127.0.0.1`), porta `5499` ou POSTGRES_PORT, banco `engineering_library`, usuário `admin` e a senha consultada privadamente no `.env`. Desative SSL para essa conexão local, que não configura TLS. A porta é publicada somente em 127.0.0.1. Rails usa sempre `postgres:5432`, independentemente da porta publicada.

Se falhar, confira `docker compose ps`, `docker compose logs postgres`, o mecanismo Docker, conflitos de porta e o endereço no DBeaver. Para usar outra porta, altere POSTGRES_PORT e execute `docker compose up -d postgres`. Alterar a senha no `.env` não altera a senha de um cluster existente: as variáveis só inicializam clusters novos. Faça a troca autenticada no psql com `\password admin`, atualize `.env` e recrie o backend. Não apague dados para resolver autenticação.

Os dados permanecem em `.dockerized-postgres/18/docker` após recriar contêineres. Excluir `.dockerized-postgres/` destrói os dados locais. Nunca limpe essa pasta automaticamente nem troque a versão principal sobre um cluster existente. Persistência não substitui backup:

```sh
mkdir -p /tmp/engineering-library-backups
docker compose exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > /tmp/engineering-library-backups/library.dump
# Confira o dump e restaure primeiro em outro banco vazio:
docker compose exec -T postgres sh -c 'createdb -U "$POSTGRES_USER" engineering_library_restore'
docker compose exec -T postgres sh -c 'pg_restore -U "$POSTGRES_USER" -d engineering_library_restore --no-owner --exit-on-error' < /tmp/engineering-library-backups/library.dump
```

Guarde backups fora da pasta de dados e do repositório, proteja o acesso e teste a restauração. Copiar PGDATA com o servidor ativo não garante consistência. Para mudar a versão principal, use dump/restore ou procedimentos oficiais de atualização PostgreSQL.

## Verificação

```sh
docker compose config --quiet
docker compose build
docker compose up -d --wait --wait-timeout 300
docker compose exec backend bin/rails db:prepare
docker compose exec -e RAILS_ENV=test backend bin/rails db:prepare
docker compose exec -e RAILS_ENV=test backend bin/rails test
docker compose exec backend bin/rails zeitwerk:check
docker compose exec frontend npm run lint
docker compose exec frontend npm run typecheck
docker compose exec frontend npm run build
curl --fail http://localhost:3098/up
curl --fail http://localhost:3099
python3 -B -m unittest discover -s tools -p test_check_docs.py -v
```

A suíte Rails cobre saúde HTTP, ausência da senha na resposta e conexão SQL real. Lint, tipos e build são proporcionais à página inicial; não acrescentamos biblioteca de testes de navegador. `/up` verifica vida do processo, não a prontidão de toda a infraestrutura. Próximo marco sugerido: definir uma API de leitura de coleções/capítulos e apresentar a documentação existente, preservando fontes e navegação bilíngue. IA continua no planejamento.

## Limite da auditoria de dependências

Mantivemos ESLint 9.39.5 porque os plugins React incluídos em eslint-config-next não declaram compatibilidade com ESLint 10. O npm marca ESLint 9 como sem suporte. npm audit aponta cinco alertas altos de ferramentas de desenvolvimento na cadeia eslint-config-next → fast-glob → micromatch → braces; braces 3.0.3 ainda é a versão mais recente publicada. Não forçamos overrides incompatíveis nem rebaixamos o framework. Revisar quando os mantenedores publicarem correções compatíveis. A auditoria de runtime é feita separadamente.

## Validação executada — 18/10/2026

Validado em macOS ARM64 com Docker Desktop: Compose válido; imagens das aplicações construídas; três serviços saudáveis; preparação/migração do banco Rails e Zeitwerk aprovados; testes Rails aprovados (2 testes, 4 asserções); lint, TypeScript e build otimizado webpack do Next.js aprovados. As verificações HTTP confirmam `/up`, conteúdo renderizado e conexão da página com a API pelo servidor. A autenticação PostgreSQL pela porta publicada funciona; a identidade do cluster permanece após recriação forçada do contêiner. bundle install e npm ci funcionam com diretórios físicos no host. Foram conferidas a política da senha, permissão 0600 e preservação de `.env` existente. A auditoria npm de runtime retorna zero vulnerabilidades; a auditoria completa aponta os cinco alertas de ferramentas descritos acima.

Os 22 testes Python existentes passam. A varredura documental dos seis repositórios aponta dois erros preexistentes relativos à categoria vazia/desconhecida `rust-event-relay/docs/pt-BR/manual` e 18 avisos de links bloqueados; nenhum erro pertence à Engineering Library. Dos 48 documentos originais, 46 permanecem idênticos e os dois índices receberam apenas um link de navegação ao final. O conteúdo anterior dos READMEs foi preservado com orientações adicionais. Não foram exercitados a interface gráfica do DBeaver, inspeção visual em navegador, execução Linux/x86, reconstrução de gem efetivamente removida nem restauração de backup. A autenticação SQL via TCP verifica o caminho de conexão usado por clientes locais, não a interface do DBeaver.


[ENV](../env/index.md) · [Database migration / Migração do banco](../operations/database-migration.md)
