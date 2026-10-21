# Desenvolvimento da aplicação

## Execução em Docker

Execute os comandos de shell na raiz deste repositório. Node.js, npm, Ruby, Bundler, Rails e clientes PostgreSQL executam dentro dos containers; o host precisa de Docker com Compose. Não é necessário instalar esses runtimes no host. `exec` exige o serviço ativo e usa `/app/frontend` ou `/app/backend`; A verificação de build copia fontes para um diretório temporário dentro do frontend existente, preservando o cache do servidor ativo.

Para o bootstrap, copie `.env.example` para `.env` e preencha credenciais privadas, ou use o gerador Python opcional abaixo; o gerador preserva `.env` existente. Python 3.10+ no host é uma exceção opcional: `python3 tools/init_dev_env.py` gera credenciais; os validadores documentais usam apenas a biblioteca padrão; `tools/check_docker_startup.py` coordena o Docker e verifica portas do host. Instale Python apenas se escolher essas ferramentas no host. Não se presume sua presença.

Playwright 1.58.2, Chromium e dependências de sistema estão na imagem `frontend-development`, fora do target de dependências da aplicação. Reconstrua com `docker compose up -d --build --wait --wait-timeout 300`. O navegador executado no frontend acessa `http://localhost:3000`, a porta interna do mesmo container; no host, use `http://localhost:3099`. Outros containers usam `http://frontend:3000`. Os scripts de demos continuam restritos a loopback.

Os documentos dos demais projetos são referências dos repositórios de origem, não comandos operacionais desta instalação; esta política não afirma suporte Docker adicional nesses projetos. Resultados antigos de validação são históricos.


Revisão atual: 2026-10-19. Rails serve catálogo PostgreSQL e anotações compartilhadas; Next renderiza o livro bilíngue interno. O setup abaixo mantém escopo de desenvolvimento; consulte [arquitetura atual](../architecture/current-state.md) e [guia do leitor](book-frontend.md) para responsabilidades presentes.

## Versões e arquitetura

Ruby 3.4.11, Rails 8.1.4, PostgreSQL 18 (`18-bookworm`, com versão principal fixada), Node 24.22.0, Next.js 16.4.2, React 19.3.1, TypeScript 5.9.3 e ESLint 9.39.5. Gemfile.lock e package-lock.json fixam as dependências. Atualizações menores da imagem PostgreSQL são intencionais. As imagens são voltadas ao desenvolvimento.

Navegador :3099 → Next.js :3000 → Rails :3000 no Compose → PostgreSQL :5432. Rails também é exposto em loopback :3098. Consultas Next ao catálogo usam `BACKEND_URL` no servidor, `cache: no-store` e timeout de cinco segundos. `/up` Rails continua como liveness de boot, sem consultar catálogo/banco. Serviços/models atuais implementam sync, paginação e anotações compartilhadas; o leitor implementa transições de páginas. Não há autenticação de contas, inferência IA ou geração automática de documentação. Acesso do navegador à API usa rotas Next de mesma origem; o initializer CORS Rails revisado está inativo.

```text
docker/
  Dockerfile              backend-dependencies, backend-development,
                          frontend-dependencies, frontend-development
  backend-entrypoint.sh   db:prepare catalog:sync; exec Rails
  frontend-entrypoint.sh  lockfile consistency; exec Next.js
backend/                  Rails, Gemfile.lock
frontend/                 Next.js, package-lock.json
docs/                     Markdown
.dockerized-postgres/     PostgreSQL 18: 18/docker
.env                      local credentials (ignored)
compose.yaml              PostgreSQL + independent Rails and Next.js services
```

## Preparação e execução

Instale Docker Desktop no macOS ou Docker Engine com o plugin Compose no Linux seguindo o [guia oficial](https://docs.docker.com/engine/install/). Inicie o mecanismo Docker, permita o compartilhamento da pasta e confira as portas 3099, 3098 e 5499. Não é necessário instalar Ruby ou Node no computador.

A implementação gerou `.env` local com senha PostgreSQL aleatória de 12 caracteres ASCII alfanuméricos, incluindo maiúsculas, minúsculas e números, além de segredo Rails aleatório. Nenhum segredo entra no Git. Em um clone novo, use o bootstrap Python opcional abaixo ou prepare `.env` manualmente; o script preserva qualquer `.env` existente. Python 3.10+ no host é alternativa opcional. Consulte as variáveis em `.env.example`. No Linux, ajuste LOCAL_UID e LOCAL_GID para os valores de `id -u` e `id -g` antes de instalar dependências. O Docker Desktop no macOS aceita os valores padrão 1000. As pastas montadas precisam permitir escrita por esses IDs. Corrija conscientemente arquivos criados com outro usuário; não altere recursivamente os dados PostgreSQL para o usuário da aplicação. A imagem oficial gerencia a propriedade do cluster.

```sh
python3 tools/init_dev_env.py
docker compose config --quiet
docker compose up --build
# Acesse http://localhost:3099 e http://localhost:3098/up
# Encerre preservando os dados:
docker compose down
```

O PostgreSQL cria o banco ao inicializar um cluster novo. Rails aguarda PostgreSQL saudável, executa `db:prepare catalog:sync` e inicia o servidor; falhas interrompem o processo. Next aguarda Rails saudável. As migrações futuras devem ser revisadas antes da inicialização. O sync atual atualiza metadados sem excluir registros.

O único Dockerfile usa o contexto raiz e quatro targets: `backend-dependencies`, `backend-development`, `frontend-dependencies` e `frontend-development`. Gems ficam em `/usr/local/bundle`; pacotes Node em `/app/node_modules`, acima do código montado em `/app/frontend`. O mount vazio de `node_modules` mascara pacotes do host. `.next`, logs e temporários Rails usam tmpfs e são descartados ao parar. Dependências são instaladas a partir dos lockfiles durante o build, sem instalação nem acesso ao registry no startup. Os serviços rodam com LOCAL_UID/LOCAL_GID, padrão 1000:1000. São imagens de desenvolvimento.

## Dependências e comandos

```sh
docker compose build backend
docker compose build frontend
# Após atualizar os manifests e lockfiles:
docker compose up -d --build
# Build Next isolado do cache do servidor em desenvolvimento:
docker compose exec -T frontend npm run build:check
docker compose exec backend bin/rails console
docker compose logs -f backend frontend postgres
# Cinco ciclos controlados; preserva dados e deixa o último ciclo ativo:
python3 tools/check_docker_startup.py --cycles 5
```

Atualize os lockfiles com os gerenciadores nos containers existentes; reconstrua a imagem correspondente. Dependências instaladas apenas em um container ativo não são reproduzíveis. Pacotes e gems antigos no host permanecem intactos, mas não são usados. O cache Next em tmpfs acelera o uso durante cada execução, custa memória e recompila após parar o contêiner. Não execute `npm run build` no servidor de desenvolvimento ativo: use o comando isolado acima.

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
docker compose exec backend bin/rails db:prepare catalog:sync
docker compose exec -e RAILS_ENV=test backend bin/rails db:prepare
docker compose exec -e RAILS_ENV=test backend bin/rails test
docker compose exec backend bin/rails zeitwerk:check
docker compose exec frontend npm run lint
docker compose exec frontend npm run typecheck
docker compose exec -T frontend npm run build:check
curl --fail http://localhost:3098/up
curl --fail http://localhost:3099
python3 -B -m unittest discover -s tools -p test_check_docs.py -v
```

A suíte Rails cobre saúde HTTP, ausência da senha na resposta e conexão SQL real. Testes unitários, lint, tipos e build executam em Docker; a imagem de desenvolvimento inclui Playwright e Chromium para as suítes documentadas. `/up` verifica vida do processo, não a prontidão de toda a infraestrutura. Próximo marco sugerido: definir uma API de leitura de coleções/capítulos e apresentar a documentação existente, preservando fontes e navegação bilíngue. IA continua no planejamento.

## Limite da auditoria de dependências

Mantivemos ESLint 9.39.5 porque os plugins React incluídos em eslint-config-next não declaram compatibilidade com ESLint 10. O npm marca ESLint 9 como sem suporte. npm audit aponta cinco alertas altos de ferramentas de desenvolvimento na cadeia eslint-config-next → fast-glob → micromatch → braces; braces 3.0.3 ainda é a versão mais recente publicada. Não forçamos overrides incompatíveis nem rebaixamos o framework. Revisar quando os mantenedores publicarem correções compatíveis. A auditoria de runtime é feita separadamente.

## Validação executada — 18/10/2026

Validado em macOS ARM64 com Docker Desktop: Compose válido; imagens das aplicações construídas; três serviços saudáveis; preparação/migração do banco Rails e Zeitwerk aprovados; testes Rails aprovados (2 testes, 4 asserções); lint, TypeScript e build otimizado webpack do Next.js aprovados. As verificações HTTP confirmam `/up`, conteúdo renderizado e conexão da página com a API pelo servidor. A autenticação PostgreSQL pela porta publicada funciona; a identidade do cluster permanece após recriação forçada do contêiner. bundle install e npm ci funcionam com diretórios físicos no host. Foram conferidas a política da senha, permissão 0600 e preservação de `.env` existente. A auditoria npm de runtime retorna zero vulnerabilidades; a auditoria completa aponta os cinco alertas de ferramentas descritos acima.

Os 22 testes Python existentes passam. A varredura documental dos seis repositórios aponta dois erros preexistentes relativos à categoria vazia/desconhecida `rust-event-relay/docs/pt-BR/manual` e 18 avisos de links bloqueados; nenhum erro pertence à Engineering Library. Dos 48 documentos originais, 46 permanecem idênticos e os dois índices receberam apenas um link de navegação ao final. O conteúdo anterior dos READMEs foi preservado com orientações adicionais. Não foram exercitados a interface gráfica do DBeaver, inspeção visual em navegador, execução Linux/x86, reconstrução de gem efetivamente removida nem restauração de backup. A autenticação SQL via TCP verifica o caminho de conexão usado por clientes locais, não a interface do DBeaver.


[ENV](../env/index.md) · [Database migration / Migração do banco](../operations/database-migration.md)

## Verificação deste ajuste — 2026-10-21

Nos serviços existentes: 100 testes frontend, lint e TypeScript passaram; `build:check` concluiu em diretório temporário no frontend, preservando o cache do servidor. Rails passou 25 testes e 408 asserções no banco `_test`. A regressão de demos passou com banco sintético no PostgreSQL existente, seed idempotente, dois navegadores e limpeza preservando anotações manuais. Os comandos CLI de instalação e limpeza também passaram, preservando duas notas sintéticas em projetos diferentes. O backend foi restaurado ao banco original; hashes e contagens de 60 notas, 60 destaques e 12 marcações ficaram iguais antes/depois. O banco temporário foi removido.

Chromium executou no frontend; manifesto: 132 âncoras válidas, zero inválidas. O smoke de cinco viewports passou após uma tentativa com timeout de navegação. Geração de snapshots passou numa cópia temporária da documentação, sem alterar snapshots publicados. A inspeção de âncoras agora repete uma única leitura interrompida por navegação, sem repetir mutações. A stack QA adicional da tentativa anterior, seu Compose e suas duas imagens foram removidos; restam os três serviços originais.

Python no host: 27 testes passaram; catálogo sem erros, com um aviso de índices IMG idênticos. `npm ci` informou cinco vulnerabilidades altas existentes; não houve correção de dependências nesta tarefa. A suíte de fontes que inicia servidor de fixtures apresentou `width is not defined` na tentativa anterior e permanece fora do fluxo autorizado. Não houve validação Linux/x86 nem deploy de produção.
