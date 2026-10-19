# Auditoria documental — 2026-10-19

[Índice do projeto](../index.md) · [FAQ técnica](../faq/index.md) · [English](../../en/operations/documentation-audit-2026-10-19.md)

**Status: parcial; a auditoria integral do portfólio continua aberta.** Esta etapa coloca respostas completas existentes no índice FAQ, preserva caminhos/âncoras dos roteiros e acrescenta correções fundamentadas no código atual. Nem todas as respostas históricas foram revalidadas linha por linha.

## Recuperação histórica

O commit `5052a8515b30278abea5fb81b37647482c10ba18` existe na Engineering Library. `docs/en/interviews/` e `docs/pt-BR/interviews/` contêm seis guias e fundamentos. Os roteiros atuais já preservam esse material com links realocados/notas de status. Não houve checkout/reset nem restauração da estrutura antiga. Fundamentos foram reescritos seletivamente na FAQ da Library, corrigindo ausência histórica de worker e excluindo referências a produto privado.

## Evidências e correções atuais

Contratos multipart, padrões, buffers do proxy, limites codificados/pixels e definições HTTP selecionadas.

HEAD inspecionado (sem garantir árvore limpa): `cdb188c6a08f08482060a43d3d505fd494a1189e`.

Os caminhos abaixo são evidências, sem instrução de execução. Arquivos grandes receberam leitura seletiva; hashes no registro identificam entradas sem afirmar revisão de cada linha.

- `backend/internal/infrastructure/http/handler/compress_image/handler.go`
- `backend/internal/infrastructure/http/handler/resize_image/handler.go`
- `backend/internal/infrastructure/http/handler/convert_image/handler.go`
- `backend/internal/infrastructure/http/router.go`
- `backend/internal/infrastructure/http/server.go`
- `backend/internal/infrastructure/imaging/limits.go`
- `backend/internal/infrastructure/http/resize_test.go`
- `frontend/app/api/images/forward-image-request.ts`
- `frontend/app/api/images/compress/route.ts`

## Categorias revisadas nesta etapa

- [api/contracts.md](../api/contracts.md)
- [security/resource-boundaries.md](../security/resource-boundaries.md)

Os dois idiomas receberam respostas atuais e correções por categoria. Texto legado e resultados anteriores permanecem datados. Paridade de caminhos/IDs é estrutural, sem certificação integral de tradução.

## Validação e trabalho pendente

Executado: `python3 -B -m unittest discover -s tools -p 'test_*.py' -v` na Engineering Library: 27 passaram. A verificação final do catálogo passou com 442 arquivos Markdown, 3.540 links locais, zero erros e zero avisos; `git diff --check` passou. São verificações estruturais, sem certificar navegador ou precisão semântica. `node --version` e `npm --version` falharam por comandos ausentes no host. Sem instalação, partida de serviços, suíte dos irmãos, navegador, stage, commit ou push.

Inspecionar todos os casos de uso e codecs/fixtures, controles/download do frontend, Docker/CGO, consumidores ENV, ADR e testes restantes; revalidar todas as respostas legadas.

[Registro retomável do portfólio](../../../../../validation/documentation-audit-2026-10-19.json) lista hashes, caminhos documentais pendentes e limites. Retome pelas implementações pendentes e compare ambos os idiomas; esta etapa não permite marcar o repositório como integralmente auditado.
