# Engineering Library API

Private Viva Bem component for authorized internal use. / Componente privado da Viva Bem para uso interno autorizado.

## English

Rails provides paginated catalog metadata, shared PostgreSQL notes/highlights/bookmarks and guarded development-only catalog/MakeDocs operations. Markdown remains the chapter-body source. `GET /up` checks Rails response and required host filesystem adapter readiness; it does not certify database integrity, approved-model availability or generation quality.

Use the repository-root managed launcher: `python3 -B tools/init_dev_env.py up -d --build --wait --wait-timeout 600`. Application Ruby/Bundler/Rails stay inside Docker; the supervisor/adapter requires POSIX host Python. Startup runs `db:prepare catalog:sync`. The default CLI and frontend reuse `Documentation::Command`, with recoverable delivery to the library and original project docs. Accepted outputs remain drafts; no completed neural fine-tuning is claimed.

See [architecture](../docs/engineering-library/en/architecture/current-implementation.md), [development](../docs/engineering-library/en/guides/application-development.md), [MakeDocs](../docs/engineering-library/en/training/local-documentation-command.md) and [recovery](../docs/engineering-library/en/operations/runtime-and-recovery.md).

## Português brasileiro

Rails fornece metadados paginados do catálogo, notas/destaques/marcadores PostgreSQL compartilhados e operações protegidas de catálogo/MakeDocs em desenvolvimento. Markdown continua fonte dos capítulos. `GET /up` verifica Rails e adapter obrigatório; não certifica integridade do banco, modelo aprovado ou qualidade da geração.

Use o launcher na raiz: `python3 -B tools/init_dev_env.py up -d --build --wait --wait-timeout 600`. Ruby/Bundler/Rails executam no Docker; supervisor/adapter exigem Python POSIX no host. O startup executa `db:prepare catalog:sync`. CLI padrão e frontend reutilizam `Documentation::Command`, com entrega recuperável na biblioteca e docs originais. Saídas aceitas continuam rascunhos; não se afirma fine-tuning neural concluído.

Consulte [arquitetura](../docs/engineering-library/pt-br/architecture/current-implementation.md), [desenvolvimento](../docs/engineering-library/pt-br/guides/application-development.md), [MakeDocs](../docs/engineering-library/pt-br/training/local-documentation-command.md) e [recuperação](../docs/engineering-library/pt-br/operations/runtime-and-recovery.md).
