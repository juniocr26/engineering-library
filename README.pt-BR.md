# Engineering Library

> Este repositório/versão da Engineering Library é privado e preserva documentação das coleções autorizadas de portfólio e Viva Bem privado. Uma versão pública separada está planejada para depois.

## Base documental atual — 04/11/2026

- [Engineering Library: catálogo, leitor e anotações compartilhadas](docs/engineering-library/pt-br/architecture/current-implementation.md)
- Contratos atuais do código prevalecem sobre notas de marcos datados. Testes com mocks não comprovam homologação no provedor.

## Execução em Docker

Execute os comandos de shell na raiz deste repositório. Node.js, npm, Ruby, Bundler, Rails e clientes PostgreSQL executam dentro dos containers; o host precisa de Docker com Compose. Não é necessário instalar esses runtimes no host. `exec` exige o serviço ativo e usa `/app/frontend` ou `/app/backend`; A verificação de build copia fontes para um diretório temporário dentro do frontend existente, preservando o cache do servidor ativo.

No Windows, use Docker Desktop com containers Linux e execute os comandos Compose no PowerShell a partir desta pasta. `.gitattributes` mantém scripts shell e `backend/bin/*` em LF mesmo com `core.autocrlf=true`. O build das imagens também normaliza os entrypoints copiados, permitindo iniciar um checkout existente em CRLF. Em checkouts existentes, salve em LF os scripts montados do host antes de executá-los, incluindo `frontend/tools/build-in-container.sh`. Após atualizar, reconstrua com `docker compose up -d --build --wait --wait-timeout 600`. Os comandos Python opcionais abaixo usam `python3` no macOS/Linux. No Windows, use `python` ou `py -3`.

Para o bootstrap, copie `.env.example` para `.env` e preencha credenciais privadas, ou use o gerador Python opcional abaixo; o gerador preserva `.env` existente. Python 3.10+ no host é uma exceção opcional: `python3 tools/init_dev_env.py` gera credenciais; os validadores documentais usam apenas a biblioteca padrão; `tools/check_docker_startup.py` coordena o Docker e verifica portas do host. Instale Python apenas se escolher essas ferramentas no host. Não se presume sua presença.

Playwright 1.58.2, Chromium e dependências de sistema estão na imagem `frontend-development`, fora do target de dependências da aplicação. Reconstrua com `docker compose up -d --build --wait --wait-timeout 600`. O navegador executado no frontend acessa `http://localhost:3000`, a porta interna do mesmo container; no host, use `http://localhost:3099`. Outros containers usam `http://frontend:3000`. Os scripts de demos continuam restritos a loopback.

Os documentos dos demais projetos são referências dos repositórios de origem, não comandos operacionais desta instalação; esta política não afirma suporte Docker adicional nesses projetos. Resultados antigos de validação são históricos.


## Comando local de documentação

`make docs` roda no backend existente e chama o Ollama Docker para produzir um resultado EN/PT-BR revisável nesta biblioteca e em `docs/` do projeto analisado. Fontes são somente leitura; resumos e blocos de navegação controlados têm recuperação; entradas inalteradas resultam em no-op. A redação exige revisão factual/bilíngue; erros atuais do modelo 3B estão registrados.

```sh
docker compose exec backend sh
# Dentro do backend, após preparar mounts restritos de docs graváveis:
make docs
make docs DOCS_ARGS='--project project-slug'
```

O [guia de execução/recuperação](docs/engineering-library/pt-br/training/local-documentation-command.md) traz preparo dos mounts inteiramente em Docker, coleções explícitas, seleção de fontes, revisão assistida, recuperação e provisionamento separado do modelo. Não exige runtime de linguagem no host. A descoberta padrão visita irmãos diretos e exclui esta biblioteca; a avaliação privada em duas coleções usa configuração explícita.

Pesquisa é offline por padrão. O [Compose SearXNG opcional](compose.research.yaml) fornece busca real sem chave; recuperação de URLs públicas aprovadas e uso local dos trechos citados estão integrados. Restrições upstream e degradação são explícitas. Skills entram como contexto, sem treinamento de pesos; não há fallback cloud, publicação automática ou geração raster.

Plataforma local de documentação de engenharia, com Rails, Next.js e PostgreSQL. Catálogo bilíngue organizado por projeto; a redação local de resumos do código está implementada; agentes autônomos mais amplos permanecem futuros.

[English](README.md) | [Português brasileiro](README.pt-BR.md)

- [Catalog / Catálogo](docs/index.md)
- [Engineering Library](docs/engineering-library/pt-br/index.md)
- [Development / Desenvolvimento](docs/engineering-library/pt-br/guides/application-development.md)
- [FAQ](docs/engineering-library/pt-br/faq/index.md)
- [ENV](docs/engineering-library/pt-br/env/index.md)
- [Database migration / Migração do banco](docs/engineering-library/pt-br/operations/database-migration.md)

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
python3 -B tools/check_catalog.py
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

## Descoberta de projetos e manutenção

`tools/docs_manifest.json` mapeia os 13 repositórios para duas raízes relativas a este repositório, independentemente do diretório do shell: `../` (nove projetos VivaBem) e `../../Portifólio/` (quatro projetos de portfólio; grafia real local diferente de `Portfólio`). `repositories` mantém o inventário estável. `tools/check_docs.py` usa o mapa na validação; `tools/check_catalog.py`, na conferência das fontes importadas. Nenhuma entrada nova é criada no catálogo.

Antes de uma atualização geral, execute `python3 -B tools/check_docs.py --discover-only` nesta raiz (ou invoque o caminho absoluto do script de qualquer diretório). Inspecione mudanças verificadas de código e documentação em **todos os 13** projetos mapeados, incluindo explicitamente `script-auditoria-envs` e a própria Engineering Library. Relate raízes/projetos indisponíveis; nunca deduza exclusão pela localização antiga. Preserve nomes, slugs, mapeamentos de origem, organização bilíngue e estrutura documental específica. Atualize somente documentos justificados por mudanças verificadas; preserve documentação atual. Não regenere o catálogo nem duplique entradas.

O código da aplicação é evidência somente leitura; diretórios docs/ selecionados são graváveis pelo make docs. Descoberta não autoriza publicação: preserve restrições públicas/privadas, inclusive a identificação privada deste checkout. Nunca copie código privado, detalhes proprietários ou documentação confidencial para artefatos públicos. Nunca leia ou ingira `.vivabem-secrets`, `.env*`, credenciais, chaves privadas ou valores de configuração sensíveis. `.github`/`.vscode`, dependências, caches e dados gerados não são projetos documentais. A descoberta verifica apenas repositórios imediatos configurados e existência de metadados Git; não abre conteúdo de origem. A revisão de código deve aplicar essas restrições; o validador lê somente documentação e metadados permitidos.

## Referências de marcos anteriores

> Checkout privado da documentação VivaBem: `parceiro-vivabem/engineering-library`, confirmado pelo proprietário em 2026-10-26. O portfólio público `juniocr26/engineering-library` é outro destino. A documentação de produtos deste checkout deve permanecer privada. Descrições antigas de catálogo público abaixo registram sua origem histórica.
