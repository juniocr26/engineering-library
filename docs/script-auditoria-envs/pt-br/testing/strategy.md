# Testes e aceitação — script-auditoria-envs

[English](../../en/testing/strategy.md) | [Português brasileiro](strategy.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `2e5d5de71d1323b4e588e04f06784324802ae0d3`.

<!-- reading-section: assertions -->

## Asserções inspecionadas

`tests/test_selected_directory.py`: Fixtures sintéticas verificam preservação de modo/proprietário, arquivos alheios, falha de probe e exigência de destino existente.

<!-- reading-section: proposed -->

## Verificação proposta

Para exercício isolado futuro, crie diretório descartável com `.env` e `.env.example` sintéticos contendo SHARED, ONLY_TARGET e ONLY_EXAMPLE. No repositório fonte, execute `python3 audit-envs.py /absolute/synthetic-root --dry-run` para inspecionar ações sobre nomes. Autorize modo de escrita separadamente após revisar o escopo. Escrita bem-sucedida não atualiza caches Laravel, imagens ou workers; ativação é procedimento separado da aplicação.

<!-- reading-section: not-run -->

## Limite de execução

Testes das aplicações não foram executados. Nenhuma contagem histórica é apresentada como atual. Checks documentais ficam registrados separadamente na revisão da biblioteca.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
