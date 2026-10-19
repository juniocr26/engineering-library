# Auditoria documental — 2026-10-19

[Índice do projeto](../index.md) · [FAQ técnica](../faq/index.md) · [English](../../en/operations/documentation-audit-2026-10-19.md)

**Status: parcial; a auditoria integral do portfólio continua aberta.** Esta etapa coloca respostas completas existentes no índice FAQ, preserva caminhos/âncoras dos roteiros e acrescenta correções fundamentadas no código atual. Nem todas as respostas históricas foram revalidadas linha por linha.

## Recuperação histórica

O commit `5052a8515b30278abea5fb81b37647482c10ba18` existe na Engineering Library. `docs/en/interviews/` e `docs/pt-BR/interviews/` contêm seis guias e fundamentos. Os roteiros atuais já preservam esse material com links realocados/notas de status. Não houve checkout/reset nem restauração da estrutura antiga. Fundamentos foram reescritos seletivamente na FAQ da Library, corrigindo ausência histórica de worker e excluindo referências a produto privado.

## Evidências e correções atuais

API atual, sync de metadados, schema PostgreSQL, isolamento de favoritos, leitores de arquivos e arquitetura atual/futura.

HEAD inspecionado (sem garantir árvore limpa): `7b96b3545d5f257611257d23846606cbdefc0442`.

Os caminhos abaixo são evidências, sem instrução de execução. Arquivos grandes receberam leitura seletiva; hashes no registro identificam entradas sem afirmar revisão de cada linha.

- `compose.yaml`
- `backend/config/routes.rb`
- `backend/config/database.yml`
- `backend/config/initializers/cors.rb`
- `backend/db/schema.rb`
- `backend/app/services/catalog/files.rb`
- `backend/app/services/catalog/sync.rb`
- `backend/app/services/catalog/page.rb`
- `backend/app/services/catalog/presenter.rb`
- `backend/app/controllers/api/projects_controller.rb`
- `backend/app/controllers/api/bookmarks_controller.rb`
- `backend/app/models/catalog_project.rb`
- `backend/app/models/bookmark.rb`
- `backend/test/models/catalog_test.rb`
- `backend/test/integration/catalog_api_test.rb`
- `backend/test/integration/bookmarks_api_test.rb`
- `frontend/lib/catalog.ts`
- `frontend/lib/documentation.ts`
- `frontend/lib/document-links.ts`
- `frontend/lib/reading-order.ts`
- `frontend/lib/source-links.ts`
- `frontend/lib/source-snapshot.ts`
- `frontend/lib/source-search.ts`
- `frontend/tests/reading-order.test.ts`
- `frontend/package.json`
- `docs/validation/check_catalog.py`
- `tools/check_docs.py`
- `tools/test_catalog.py`

## Categorias revisadas nesta etapa

- [architecture/current-state.md](../architecture/current-state.md)
- [architecture/future-direction.md](../architecture/future-direction.md)
- [architecture/source-references.md](../architecture/source-references.md)
- [guides/book-frontend.md](../guides/book-frontend.md)
- [guides/documentation-validator.md](../guides/documentation-validator.md)
- [guides/application-development.md](../guides/application-development.md)
- [env/index.md](../env/index.md)
- [testing/documentation.md](../testing/documentation.md)
- [operations/source-review.md](../operations/source-review.md)

Os dois idiomas receberam respostas atuais e correções por categoria. Texto legado e resultados anteriores permanecem datados. Paridade de caminhos/IDs é estrutural, sem certificação integral de tradução.

## Validação e trabalho pendente

Executado: `python3 -B -m unittest discover -s tools -p 'test_*.py' -v` na Engineering Library: 27 passaram. A verificação final do catálogo passou com 442 arquivos Markdown, 3.540 links locais, zero erros e zero avisos; `git diff --check` passou. São verificações estruturais, sem certificar navegador ou precisão semântica. `node --version` e `npm --version` falharam por comandos ausentes no host. Sem instalação, partida de serviços, suíte dos irmãos, navegador, stage, commit ou push.

Revisar componentes completos do leitor, paginação/mídia/Mermaid, gerador/loader de fontes, demais guias operacionais/setup e migrations/tasks. Conciliar narrativas antigas pelas datas; verificar navegador em runtime apropriado.

[Registro retomável do portfólio](../../../../../validation/documentation-audit-2026-10-19.json) lista hashes, caminhos documentais pendentes e limites. Retome pelas implementações pendentes e compare ambos os idiomas; esta etapa não permite marcar o repositório como integralmente auditado.
