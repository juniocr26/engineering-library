# Testes e aceitação — acesso-servidor

[English](../../en/testing/strategy.md) | [Português brasileiro](strategy.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `ba70952fd63992c85aa153f141a39fadf33360a0`.

<!-- reading-section: assertions -->

## Asserções inspecionadas

`tests/test_operator_workflow.py`: Cria fixtures Git/segredos descartáveis e substitui funções selecionadas; verifica preservação dos bytes e fluxo do operador. Sucesso dessas fixtures não comprovaria deploy. Suíte não executada.

<!-- reading-section: proposed -->

## Verificação proposta

Para investigar, leia main, compose, cleanup_dependencies e deployment_guard.git_state antes de usar flags. Revise branches exatas, estado inicial, configuração existente e evidências de backup/restauração em janela de manutenção autorizada separadamente. Se uma fase falhar, identifique as concluídas e preserve logs/chaves originais; não presuma rollback automático nem repita todo o atualizador cegamente. Esta coleção não fornece comando executável de deploy de produção.

<!-- reading-section: not-run -->

## Limite de execução

Testes das aplicações não foram executados. Nenhuma contagem histórica é apresentada como atual. Checks documentais ficam registrados separadamente na revisão da biblioteca.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
