# FAQ técnica — acesso-servidor

[English](../../en/faq/index.md) | [Português brasileiro](index.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `ba70952fd63992c85aa153f141a39fadf33360a0`.

<!-- reading-section: q001 -->

## Q001 — --dry-run é verificação documental somente leitura?

Não. Seleciona validação, mas cleanup_dependencies remove diretórios de dependências e propostas audit exatas antes do preflight. Falha posterior não os restaura. Inspecione o código sem executar o atualizador.

<!-- reading-section: q002 -->

## Q002 — Uma falha restaura as quatro aplicações?

Não. O fluxo é sequencial, sem rollback global automático. Registre fases de branch/build/startup concluídas, preserve dados e identidades e planeje recuperação compatível. Probe de readiness bem-sucedido não é procedimento de restauração testado.

<!-- reading-section: q003 -->

## Q003 — Quais afirmações permanecem sem validação?

Deploy em servidor autorizado, ordem completa de startup, restauração de dados originais, compatibilidade entre versões e recuperação de limpeza interrompida não foram executados. Nenhum modo do atualizador, update Git, SSH, reset ou migration foi executado.

[Evidence and limits / Evidências e limites](../operations/source-review.md)

[Failure scenarios / Cenários de falha](failure-scenarios.md)
