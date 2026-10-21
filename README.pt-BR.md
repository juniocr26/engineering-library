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

Docker usa somente `docker/Dockerfile`, com os targets `backend-dependencies`, `backend-development`, `frontend-dependencies` e `frontend-development`. O Compose constrói os runtimes independentemente; dependências ficam nas imagens e caches de desenvolvimento em tmpfs. Rails executa `db:prepare catalog:sync` antes do servidor. Após alterar dependências e seus lockfiles, execute `docker compose up -d --build`. Não é necessário reiniciar manualmente o frontend.

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
