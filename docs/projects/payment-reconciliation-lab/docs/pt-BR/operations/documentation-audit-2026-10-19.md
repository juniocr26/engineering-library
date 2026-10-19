# Auditoria documental — 2026-10-19

[Índice do projeto](../index.md) · [FAQ técnica](../faq/index.md) · [English](../../en/operations/documentation-audit-2026-10-19.md)

**Status: parcial; a auditoria integral do portfólio continua aberta.** Esta etapa coloca respostas completas existentes no índice FAQ, preserva caminhos/âncoras dos roteiros e acrescenta correções fundamentadas no código atual. Nem todas as respostas históricas foram revalidadas linha por linha.

## Recuperação histórica

O commit `5052a8515b30278abea5fb81b37647482c10ba18` existe na Engineering Library. `docs/en/interviews/` e `docs/pt-BR/interviews/` contêm seis guias e fundamentos. Os roteiros atuais já preservam esse material com links realocados/notas de status. Não houve checkout/reset nem restauração da estrutura antiga. Fundamentos foram reescritos seletivamente na FAQ da Library, corrigindo ausência histórica de worker e excluindo referências a produto privado.

## Evidências e correções atuais

DTOs somente leitura, visibilidade, preservação do schema legado, restrições SQL, allowlist, falha de seed e fronteiras dos testes.

HEAD inspecionado (sem garantir árvore limpa): `c27a55959101e6c29d0fb201c6d6b0d322fd40d1`.

Os caminhos abaixo são evidências, sem instrução de execução. Arquivos grandes receberam leitura seletiva; hashes no registro identificam entradas sem afirmar revisão de cada linha.

- `backend/src/main/java/com/aurorabakery/catalog/application/CatalogService.java`
- `backend/src/main/java/com/aurorabakery/catalog/api/ProductController.java`
- `backend/src/main/java/com/aurorabakery/catalog/infrastructure/ProductRepository.java`
- `backend/src/main/java/com/aurorabakery/catalog/domain/Product.java`
- `backend/src/main/java/com/aurorabakery/configuration/SecurityConfiguration.java`
- `backend/src/main/java/com/aurorabakery/configuration/ApiExceptionHandler.java`
- `backend/src/main/java/com/aurorabakery/configuration/DevelopmentSeedConfiguration.java`
- `backend/src/main/resources/application.yml`
- `backend/src/main/resources/application-dev.yml`
- `backend/src/main/resources/db/migration/V1__create_stores.sql`
- `backend/src/main/resources/db/migration/V2__single_bakery_catalog.sql`
- `backend/src/test/java/com/aurorabakery/catalog/ProductApiTest.java`
- `backend/src/test/java/com/aurorabakery/catalog/ProductPostgresIT.java`

## Categorias revisadas nesta etapa

- [database/catalog-and-transition.md](../database/catalog-and-transition.md)
- [security/read-api-boundaries.md](../security/read-api-boundaries.md)

Os dois idiomas receberam respostas atuais e correções por categoria. Texto legado e resultados anteriores permanecem datados. Paridade de caminhos/IDs é estrutural, sem certificação integral de tradução.

## Validação e trabalho pendente

Executado: `python3 -B -m unittest discover -s tools -p 'test_*.py' -v` na Engineering Library: 27 passaram. A verificação final do catálogo passou com 442 arquivos Markdown, 3.540 links locais, zero erros e zero avisos; `git diff --check` passou. São verificações estruturais, sem certificar navegador ou precisão semântica. `node --version` e `npm --version` falharam por comandos ausentes no host. Sem instalação, partida de serviços, suíte dos irmãos, navegador, stage, commit ou push.

Inspecionar fluxos Angular, build/Compose/volume existente, demais DTOs/testes de seed, ENV e guias ADR/operação; revalidar todas as respostas legadas.

[Registro retomável do portfólio](../../../../../validation/documentation-audit-2026-10-19.json) lista hashes, caminhos documentais pendentes e limites. Retome pelas implementações pendentes e compare ambos os idiomas; esta etapa não permite marcar o repositório como integralmente auditado.
