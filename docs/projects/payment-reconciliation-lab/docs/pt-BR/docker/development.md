# Desenvolvimento Docker e recuperação

Execute os comandos no diretório `payment-reconciliation-lab/` do host. Docker Engine/Desktop e Compose são necessários; a auditoria anterior usou Compose v5.1.4 no macOS. As imagens fixam Node 22.23.3 (npm 10.9.9), Java 25.0.4.1 e PostgreSQL 17.11; o Maven Wrapper instala Maven 3.9.11 e o Angular é 21.2.x. npm e Maven no host não são necessários.

## Serviços e segurança

`db` é PostgreSQL, `backend` usa Spring Boot/JPA/Flyway e `frontend` é Angular com proxy para `backend:8080`. Projeto: `payment-reconciliation-lab`; portas padrão: 5432, 8080 e 4200 em loopback. O backend base executa migrações Flyway; habilitar o seed removido falha o startup. Não o inicie contra dados existentes nesta validação.

O override de desenvolvimento usa um workspace JDK/Maven e fontes Angular montadas do host. Desabilita Flyway e mantém false a flag do seed removido. O frontend aguarda o processo backend, não sua saúde; confira readiness manualmente. O Dockerfile de runtime continua empacotando um JAR com JRE. As imagens de desenvolvimento têm tags próprias.

## Clone novo e instalação de dependências

```sh
if [ ! -e .env ]; then cp .env.example .env; fi
# Configure POSTGRES_PASSWORD e DEV_SEED_ENABLED=false localmente.
mkdir -p backend/.m2
docker compose -f docker-compose.yml -f compose.development.yaml build backend frontend
docker compose -f docker-compose.yml -f compose.development.yaml run --rm --no-deps -T --entrypoint sh frontend -c 'npm ci --no-fund'
docker compose -f docker-compose.yml -f compose.development.yaml run --rm --no-deps -T --entrypoint sh backend -c 'sh ./mvnw -B -ntp compile -DskipTests'
```

Esses containers não publicam portas, não iniciam dependências nem Spring. Compilar não executa testes. `npm ci` usa o lockfile e substitui a instalação; os scripts npm não possuem hook de inicialização da aplicação durante a instalação.

| Componente | Caminho no container | Caminho no host | Montagem / finalidade |
| --- | --- | --- | --- |
| Angular/npm | `/app/node_modules` | `frontend/node_modules` | Bind das fontes; pacotes JS e nativos Linux |
| Maven | `/root/.m2/repository` | `backend/.m2/repository` | Bind; dependências e plugins |
| Maven Wrapper | `/root/.m2/wrapper` | `backend/.m2/wrapper` | Mesmo bind; distribuição Maven |

`/home/node/.npm` é cache descartável de downloads, não a instalação. `backend/target`, `frontend/.angular`, `frontend/dist` e `frontend/out-tsc` são artefatos de build. Maven usa seu repositório nativo, não `vendor`. `.m2/settings.xml` personalizado é configuração e exige backup.

## Inicialização e parada seguras

Instalar dependências não exige containers persistentes. Inspecione serviços e portas sem exibir valores do ambiente:

```sh
docker compose -f docker-compose.yml -f compose.development.yaml config --services
docker ps --format '{{.Names}} {{.Ports}}'
```

Angular pode executar sozinho, mas o proxy API ficará indisponível:

```sh
docker compose -f docker-compose.yml -f compose.development.yaml up -d --no-deps frontend
docker compose -f docker-compose.yml -f compose.development.yaml stop frontend
```

A stack exige schema compatível já inicializado: Flyway desabilitado não inicializa banco novo. Inicialização/migração é operação explícita fora deste guia seguro. Após verificar schema e efeitos da aplicação, execute `docker compose -f docker-compose.yml -f compose.development.yaml up -d`. Pare somente os serviços que iniciou: `docker compose -f docker-compose.yml -f compose.development.yaml stop frontend backend db`. Não remova volumes para recuperar dependências. Veja [a validação atual](../testing/verification.md).

## Dependências excluídas e containers parados

Pare frontend antes de reinstalar node_modules e backend antes de restaurar Maven. Recrie diretórios com `mkdir -p backend/.m2` e repita os comandos de instalação one-off. Eles funcionam mesmo quando containers da aplicação encerram imediatamente. Não é preciso rebuild por exclusão de dependências do host. Se uma montagem aponta para diretório excluído/recriado, use ambos os arquivos Compose com `up -d --no-deps --force-recreate frontend`. Não recrie backend sem verificar segurança do banco. Rebuild é necessário quando Dockerfile/toolchain muda.

## Recuperação de configuração

Para `.env` ausente, copie o template somente se o arquivo não existir. Senhas e configurações personalizadas exigem backup ou fonte de segredos; defaults não as recuperam. Restaure individualmente arquivos versionados ausentes com `git restore --source=HEAD -- path/to/missing-file`, após confirmar ausência e preservação de alterações. Isso inclui Dockerfiles, Compose, `backend/.mvn`, wrappers, POM, configuração Angular/TypeScript/proxy, manifests e lockfiles. O wrapper vem do Git, não da instalação de dependências. Não foi identificado diretório de configuração gerado pela aplicação. Maven baixa novamente `.m2/repository` e `.m2/wrapper`; `settings.xml` personalizado exige backup. Dados/configurações PostgreSQL excluídos exigem recuperação de backup, nunca substituição por diretório vazio ou template.

## Solução de problemas

Use sempre os dois arquivos Compose. A configuração base usa dependências nas imagens e backend empacotado. Inspecione mounts com `docker inspect CONTAINER --format '{{json .Mounts}}'`: um volume sobre node_modules ocultaria a instalação do host. No Linux, o usuário `node` precisa escrever no bind; se necessário, use um container one-off com `--user "$(id -u):$(id -g)" -e HOME=/tmp` e confira o proprietário do diretório específico. Maven development usa root; para evitar problemas de propriedade, use UID do host e HOME/user home Maven graváveis. Não use chmod 777 nem mudanças recursivas amplas.

Em conflito de porta, inspecione listeners Docker/host; pare apenas seus serviços ou configure portas livres em `FRONTEND_HOST_PORT`, `BACKEND_HOST_PORT`, `POSTGRES_HOST_PORT`. Atualize allowed origins se alterar frontend. Pacotes nativos instalados nos containers são específicos de Linux/plataforma; execute-os nesses containers, não diretamente no macOS/Windows. Lockfiles e versões permanecem.

## Auditoria anterior de dependências — 2026-10-06

Os pacotes npm antes estavam na imagem e Maven no cache BuildKit. As montagens foram inspecionadas. `npm ci --no-fund` passou (466 pacotes); Angular resolveu `/app/node_modules/@angular/core/fesm2022/core.mjs`, presente em `frontend/node_modules` no host. Outro container resolveu a mesma instalação sem reinstalar. npm informou três vulnerabilidades; não houve upgrades. Maven `compile -DskipTests` passou (12 arquivos Java); outro container compilou offline com `backend/.m2`. JAR PostgreSQL e distribuição Maven físicos foram conferidos. `dependency:go-offline` foi interrompido após travar em dependências transitivas, incluindo HTTP 401 do GitHub Packages. Cobertura offline completa de plugins/testes não foi verificada. Use compile para recuperação normal; outros goals podem precisar de downloads.

Nenhum diretório de dependências existente foi excluído/renomeado. Recuperação Angular com diretório vazio passou usando bind temporário separado em `/app/node_modules`; arquivos físicos conferidos e diretório temporário removido. Recuperação Maven com cache vazio não foi simulada separadamente; o cache novo foi populado. A auditoria anterior não iniciou aplicação/banco, testes, migrações, seeds ou integrações externas.

## Conferência no host e recuperação versionada

```sh
test -f frontend/node_modules/@angular/core/fesm2022/core.mjs
test -f backend/.m2/repository/org/postgresql/postgresql/42.7.12/postgresql-42.7.12.jar
for path in .env.example docker-compose.yml backend/Dockerfile backend/pom.xml backend/mvnw backend/.mvn/wrapper/maven-wrapper.properties frontend/Dockerfile frontend/package.json frontend/package-lock.json frontend/angular.json frontend/proxy.conf.cjs frontend/tsconfig.json frontend/tsconfig.app.json frontend/tsconfig.spec.json; do
  if [ ! -e "$path" ]; then git restore --source=HEAD -- "$path"; fi
done
```

Confira se o override e este guia estão versionados; inclua alterações locais no backup. Maven compile regenera target; Angular build regenera dist/cache com `docker compose -f docker-compose.yml -f compose.development.yaml run --rm --no-deps -T --entrypoint npm frontend run build`. Esse build Angular não foi executado na auditoria anterior. Builds das imagens backend runtime e frontend development passaram com camadas Maven em cache, sem comprovar cobertura offline de todos os goals. Nenhum container de auditoria ou diretório temporário permaneceu.
