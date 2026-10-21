# Engineering Library

## Execução em Docker

Execute os comandos de shell na raiz deste repositório. Node.js, npm, Ruby, Bundler, Rails e clientes PostgreSQL executam dentro dos containers; o host precisa de Docker com Compose. Não é necessário instalar esses runtimes no host. `exec` exige o serviço ativo e usa `/app/frontend` ou `/app/backend`; A verificação de build copia fontes para um diretório temporário dentro do frontend existente, preservando o cache do servidor ativo.

Para o bootstrap, copie `.env.example` para `.env` e preencha credenciais privadas, ou use o gerador Python opcional abaixo; o gerador preserva `.env` existente. Python 3.10+ no host é uma exceção opcional: `python3 tools/init_dev_env.py` gera credenciais; os validadores documentais usam apenas a biblioteca padrão; `tools/check_docker_startup.py` coordena o Docker e verifica portas do host. Instale Python apenas se escolher essas ferramentas no host. Não se presume sua presença.

Playwright 1.58.2, Chromium e dependências de sistema estão na imagem `frontend-development`, fora do target de dependências da aplicação. Reconstrua com `docker compose up -d --build --wait --wait-timeout 300`. O navegador executado no frontend acessa `http://localhost:3000`, a porta interna do mesmo container; no host, use `http://localhost:3099`. Outros containers usam `http://frontend:3000`. Os scripts de demos continuam restritos a loopback.

Os documentos dos demais projetos são referências dos repositórios de origem, não comandos operacionais desta instalação; esta política não afirma suporte Docker adicional nesses projetos. Resultados antigos de validação são históricos.


Plataforma local de documentação de engenharia, com Rails, Next.js e PostgreSQL. Catálogo bilíngue organizado por projeto; agentes de IA permanecem futuros.

[English](README.md) | [Português brasileiro](README.pt-BR.md)

- [Catalog / Catálogo](docs/index.md)
- [Engineering Library](docs/projects/engineering-library/docs/pt-BR/index.md)
- [Development / Desenvolvimento](docs/projects/engineering-library/docs/pt-BR/guides/application-development.md)
- [FAQ](docs/projects/engineering-library/docs/pt-BR/faq/index.md)
- [ENV](docs/projects/engineering-library/docs/pt-BR/env/index.md)
- [Database migration / Migração do banco](docs/projects/engineering-library/docs/pt-BR/operations/database-migration.md)

```sh
python3 tools/init_dev_env.py
docker compose config --quiet
docker compose up --build
# Preserve data / preservar dados
docker compose down
```


Frontend: http://localhost:3099 · Rails: http://localhost:3098/up · PostgreSQL/DBeaver: `localhost:5499`, database `engineering_library`. Rails → `postgres:5432`.

Clusters existentes exigem backup e migração explícita; mudar POSTGRES_DB não renomeia bancos. Consulte o procedimento antes de reiniciar um ambiente antigo.

```sh
python3 -B docs/validation/check_catalog.py
python3 -B -m unittest discover -s tools -p 'test_*.py' -v
```

Licença MIT para o software e documentação pública própria. Conteúdo de terceiros mantém suas licenças. Documentação privada deve ficar em repositórios separados com controle de acesso; a licença não substitui gestão de segredos. Nunca publique credenciais ou arquivos .env reais. [LICENSE](LICENSE).

Demos opcionais, com os serviços ativos (shell na raiz):

```sh
docker compose exec -T frontend npm run notes:demos
docker compose exec -T frontend npm run notes:demos:cleanup
```

## Fontes locais das dependências (desenvolvimento Docker)

Os serviços existentes `frontend` e `backend` instalam dependências pelos entrypoints na inicialização. `npm ci --include=dev` preenche fisicamente `frontend/node_modules` (container `/app/frontend/node_modules`); `bundle install` com lockfile congelado preenche `backend/vendor/bundle/ruby/3.4.0/` (ABI Ruby atual) (container `/app/backend/vendor/bundle`). Esses caminhos pertencem aos bind mounts de código existentes, sem volume ou tmpfs aninhado de dependências. Pacotes nas camadas das imagens permanecem separados; a instalação de desenvolvimento não depende de arquivos ocultos pelos mounts. O startup precisa de acesso aos registries quando faltam pacotes locais; npm substitui sua árvore a cada inicialização e Bundler reaproveita gems instaladas conforme o lockfile. O cache npm fica em `/tmp` no container; recriações geralmente exigem acesso ao registry.

Na raiz do repositório, após preparar `.env`:

```sh
docker compose config --quiet
docker compose up -d --build --wait --wait-timeout 600
# Atualizar após alterar lockfiles, sem concorrer com processos ativos:
docker compose stop frontend backend
docker compose up -d --wait --wait-timeout 600 backend frontend
# Recriar somente containers de aplicação; preservar PostgreSQL e seus dados:
docker compose up -d --force-recreate --no-deps --wait --wait-timeout 600 backend frontend
# Inspecionar resolução nos serviços existentes ativos:
docker compose exec -T frontend node -p 'require.resolve("next/package.json")'
docker compose exec -T backend bundle check
docker compose exec -T backend bundle show rails
```

Não é necessário Node.js, npm, Ruby ou Bundler no host. Mantenha as pastas graváveis pelo `LOCAL_UID`/`LOCAL_GID` configurado (padrão 1000:1000 no Docker Desktop); a instalação usa esse usuário, sem alterações recursivas de permissões. O conteúdo gerado já é ignorado pelo Git e pelos contextos Docker; preserve `backend/vendor/.keep` versionado. `.next`, logs e temporários Rails continuam efêmeros. Nunca exclua dados do banco nem use `docker compose down -v` para atualizar dependências. Targets de dependências e seus caminhos de instalação nas imagens permanecem inalterados; esses entrypoints e mounts do Compose são de desenvolvimento.

VS Code pode ler fontes dos pacotes, declarações TypeScript e fontes das gems locais. O `frontend/tsconfig.json` inspecionado usa resolução bundler, plugin Next e alias `@/*`; não é necessário adicionar alias para caminhos do container. Os diretórios de tipos gerados em `.next` continuam em tmpfs apenas no container, indisponíveis localmente. O `.vscode/settings.json` ignorado inspecionado contém somente cores. A instalação local do VS Code tem suporte TypeScript integrado; nenhuma extensão Ruby foi encontrada em seu diretório local de extensões. Isso não é uma verificação de diagnósticos ao vivo. Gems físicas não fornecem IntelliSense Ruby sozinhas: Ruby LSP exige extensão, Ruby compatível e processo de language server ([documentação Ruby do VS Code](https://code.visualstudio.com/docs/languages/ruby)). Nenhum runtime, extensão ou arquitetura remota de editor foi instalado; solicite aprovação antes de introduzir essa abordagem. A execução da extensão ESLint também não foi validada. Módulos e gems nativos Linux executam nos containers, não no macOS. Comandos e verificações da aplicação continuam em Docker.
