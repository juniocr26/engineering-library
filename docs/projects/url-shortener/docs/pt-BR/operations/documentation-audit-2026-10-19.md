# Auditoria documental — 2026-10-19

[Índice do projeto](../index.md) · [FAQ técnica](../faq/index.md) · [English](../../en/operations/documentation-audit-2026-10-19.md)

**Status: parcial; a auditoria integral do portfólio continua aberta.** Esta etapa coloca respostas completas existentes no índice FAQ, preserva caminhos/âncoras dos roteiros e acrescenta correções fundamentadas no código atual. Nem todas as respostas históricas foram revalidadas linha por linha.

## Recuperação histórica

O commit `5052a8515b30278abea5fb81b37647482c10ba18` existe na Engineering Library. `docs/en/interviews/` e `docs/pt-BR/interviews/` contêm seis guias e fundamentos. Os roteiros atuais já preservam esse material com links realocados/notas de status. Não houve checkout/reset nem restauração da estrutura antiga. Fundamentos foram reescritos seletivamente na FAQ da Library, corrigindo ausência histórica de worker e excluindo referências a produto privado.

## Evidências e correções atuais

Criação/resolução, inicialização Redis, upsert Cassandra, incerteza entre stores, settings globais e testes selecionados com fakes.

HEAD inspecionado (sem garantir árvore limpa): `ed43c65c2893172f94c231ee608ecf2753b8f92f`.

Os caminhos abaixo são evidências, sem instrução de execução. Arquivos grandes receberam leitura seletiva; hashes no registro identificam entradas sem afirmar revisão de cada linha.

- `app/main.py`
- `app/schemas.py`
- `app/api/routes.py`
- `app/core/config.py`
- `app/core/security.py`
- `app/services/url_service.py`
- `app/infrastructure/redis_id_generator.py`
- `app/infrastructure/cassandra_url_store.py`
- `app/helpers/base62.py`
- `app/helpers/obfuscation.py`
- `tests/test_redis_id_generator.py`
- `tests/test_url_service.py`

## Categorias revisadas nesta etapa

- [architecture/overview.md](../architecture/overview.md)
- [database/identity-and-consistency.md](../database/identity-and-consistency.md)

Os dois idiomas receberam respostas atuais e correções por categoria. Texto legado e resultados anteriores permanecem datados. Paridade de caminhos/IDs é estrutural, sem certificação integral de tradução.

## Validação e trabalho pendente

Executado: `python3 -B -m unittest discover -s tools -p 'test_*.py' -v` na Engineering Library: 27 passaram. A verificação final do catálogo passou com 442 arquivos Markdown, 3.540 links locais, zero erros e zero avisos; `git diff --check` passou. São verificações estruturais, sem certificar navegador ou precisão semântica. `node --version` e `npm --version` falharam por comandos ausentes no host. Sem instalação, partida de serviços, suíte dos irmãos, navegador, stage, commit ou push.

Inspecionar controllers/injeção, todos os testes, bootstrap/consistência Cassandra, Compose/AOF, ENV e guias de segurança/operação; revalidar todas as respostas legadas.

[Registro retomável do portfólio](../../../../../validation/documentation-audit-2026-10-19.json) lista hashes, caminhos documentais pendentes e limites. Retome pelas implementações pendentes e compare ambos os idiomas; esta etapa não permite marcar o repositório como integralmente auditado.
