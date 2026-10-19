# Engineering Library

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
