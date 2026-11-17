# Raciocínio sobre falhas — script-auditoria-envs

[English](../../en/faq/failure-scenarios.md) | [Português brasileiro](failure-scenarios.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `2e5d5de71d1323b4e588e04f06784324802ae0d3`.

<!-- reading-section: q004 -->

## Q004 — Onde termina a consistência?

O modelo é de blocos ordenados, conjuntos de nomes e snapshots de arquivos, sem banco. `atomic_write` aplica fsync ao temporário e substitui um caminho. `env_apply.apply_directory` bloqueia o diretório, verifica snapshots e preservação de proprietário/ACL, escreve `.env` e depois `.env.example`, verifica e limpa propostas. Falha entre substituições deixa progresso parcial; o par e o workspace não formam uma transação.

<!-- reading-section: q005 -->

## Q005 — Como conduzir a investigação?

Para exercício isolado futuro, crie diretório descartável com `.env` e `.env.example` sintéticos contendo SHARED, ONLY_TARGET e ONLY_EXAMPLE. No repositório fonte, execute `python3 audit-envs.py /absolute/synthetic-root --dry-run` para inspecionar ações sobre nomes. Autorize modo de escrita separadamente após revisar o escopo. Escrita bem-sucedida não atualiza caches Laravel, imagens ou workers; ativação é procedimento separado da aplicação.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
