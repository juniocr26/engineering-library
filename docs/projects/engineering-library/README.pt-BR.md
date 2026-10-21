# Engineering Library

## Execução em Docker

Execute os comandos de shell na raiz deste repositório. Node.js, npm, Ruby, Bundler, Rails e clientes PostgreSQL executam dentro dos containers; o host precisa de Docker com Compose. Não é necessário instalar esses runtimes no host. `exec` exige o serviço ativo e usa `/app/frontend` ou `/app/backend`; A verificação de build copia fontes para um diretório temporário dentro do frontend existente, preservando o cache do servidor ativo.

Para o bootstrap, copie `.env.example` para `.env` e preencha credenciais privadas, ou use o gerador Python opcional abaixo; o gerador preserva `.env` existente. Python 3.10+ no host é uma exceção opcional: `python3 tools/init_dev_env.py` gera credenciais; os validadores documentais usam apenas a biblioteca padrão; `tools/check_docker_startup.py` coordena o Docker e verifica portas do host. Instale Python apenas se escolher essas ferramentas no host. Não se presume sua presença.

Playwright 1.58.2, Chromium e dependências de sistema estão na imagem `frontend-development`, fora do target de dependências da aplicação. Reconstrua com `docker compose up -d --build --wait --wait-timeout 300`. O navegador executado no frontend acessa `http://localhost:3000`, a porta interna do mesmo container; no host, use `http://localhost:3099`. Outros containers usam `http://frontend:3000`. Os scripts de demos continuam restritos a loopback.

Os documentos dos demais projetos são referências dos repositórios de origem, não comandos operacionais desta instalação; esta política não afirma suporte Docker adicional nesses projetos. Resultados antigos de validação são históricos.


<!-- collection entry -->
## Coleção Engineering Library

[Biblioteca](../../index.md) | [English](docs/en/index.md) | [Português brasileiro](docs/pt-BR/index.md) | [Entrevista](docs/pt-BR/faq/index.md) | [Proveniência](docs/pt-BR/operations/source-review.md)

Biblioteca bilíngue de engenharia e entrevistas com scaffold Rails/Next.js/PostgreSQL. Inclui frontend bilíngue em formato de livro e API de catálogo com PostgreSQL; o leitor Markdown interno oferece paginação medida, busca, capítulos e marcações compartilhadas no PostgreSQL.

[Bio do projeto](bio/pt-BR.md)

## Fontes locais das dependências

O desenvolvimento Docker instala fontes físicas em `frontend/node_modules` e `backend/vendor/bundle`, pelos serviços e lockfiles existentes. Consulte [instalação, atualização e limitações do VS Code](docs/pt-BR/guides/application-development.md#fontes-locais-das-dependências-desenvolvimento-docker). A execução permanece no Docker.
