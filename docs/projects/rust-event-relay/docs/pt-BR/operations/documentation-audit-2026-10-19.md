# Auditoria documental — 2026-10-19

[Índice do projeto](../index.md) · [FAQ técnica](../faq/index.md) · [English](../../en/operations/documentation-audit-2026-10-19.md)

**Status: parcial; a auditoria integral do portfólio continua aberta.** Esta etapa coloca respostas completas existentes no índice FAQ, preserva caminhos/âncoras dos roteiros e acrescenta correções fundamentadas no código atual. Nem todas as respostas históricas foram revalidadas linha por linha.

## Recuperação histórica

O commit `5052a8515b30278abea5fb81b37647482c10ba18` existe na Engineering Library. `docs/en/interviews/` e `docs/pt-BR/interviews/` contêm seis guias e fundamentos. Os roteiros atuais já preservam esse material com links realocados/notas de status. Não houve checkout/reset nem restauração da estrutura antiga. Fundamentos foram reescritos seletivamente na FAQ da Library, corrigindo ausência histórica de worker e excluindo referências a produto privado.

## Evidências e correções atuais

Intenções/ações demo, reconciliação de identidade, admissão/timeout HTTP, migration de múltiplas ações e testes selecionados.

HEAD inspecionado (sem garantir árvore limpa): `a1e0fa1513a8cbdf362f06f5cf1bdd906eb2430c`.

Os caminhos abaixo são evidências, sem instrução de execução. Arquivos grandes receberam leitura seletiva; hashes no registro identificam entradas sem afirmar revisão de cada linha.

- `backend/src/application/demo.rs`
- `backend/src/infrastructure/demo_http.rs`
- `backend/src/bin/demo.rs`
- `backend/src/infrastructure/postgres/demo.rs`
- `backend/migrations/20261019000000_multiple_duplicate_actions.up.sql`
- `backend/migrations/20261019000000_multiple_duplicate_actions.down.sql`
- `backend/tests/demo_runs.rs`

## Categorias revisadas nesta etapa

- [architecture/overview.md](../architecture/overview.md)
- [database/migrations.md](../database/migrations.md)

Os dois idiomas receberam respostas atuais e correções por categoria. Texto legado e resultados anteriores permanecem datados. Paridade de caminhos/IDs é estrutural, sem certificação integral de tradução.

## Validação e trabalho pendente

Executado: `python3 -B -m unittest discover -s tools -p 'test_*.py' -v` na Engineering Library: 27 passaram. A verificação final do catálogo passou com 442 arquivos Markdown, 3.540 links locais, zero erros e zero avisos; `git diff --check` passou. São verificações estruturais, sem certificar navegador ou precisão semântica. `node --version` e `npm --version` falharam por comandos ausentes no host. Sem instalação, partida de serviços, suíte dos irmãos, navegador, stage, commit ou push.

Auditar produtor/relay/consumidor/replay/retry/posse completos, broker/SQL, frontend/proxy, supervisor/scripts, topologia/ENV, ADRs/migrations e evidências dos marcos. Inspeção da demo não equivale à auditoria completa de entrega.

[Registro retomável do portfólio](../../../../../validation/documentation-audit-2026-10-19.json) lista hashes, caminhos documentais pendentes e limites. Retome pelas implementações pendentes e compare ambos os idiomas; esta etapa não permite marcar o repositório como integralmente auditado.
