# Raciocínio sobre falhas — acesso-servidor

[English](../../en/faq/failure-scenarios.md) | [Português brasileiro](failure-scenarios.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `ba70952fd63992c85aa153f141a39fadf33360a0`.

<!-- reading-section: q004 -->

## Q004 — Onde termina a consistência?

Identidade original de cifra, identidade de publicação, material SSH de build, dependências, armazenamento e logs privados têm ciclos diferentes. Funções guard rejeitam raízes inseguras/ancestrais simbólicos e colisões de branch antes das mutações. Startup da aplicação pode executar migrations sem --migrate opcional: preservar dados não promete ausência de escritas. Remoção explícita Mongo tem alvo protegido/decisão de terminal próprios; não é reset SQL genérico.

<!-- reading-section: q005 -->

## Q005 — Como conduzir a investigação?

Para investigar, leia main, compose, cleanup_dependencies e deployment_guard.git_state antes de usar flags. Revise branches exatas, estado inicial, configuração existente e evidências de backup/restauração em janela de manutenção autorizada separadamente. Se uma fase falhar, identifique as concluídas e preserve logs/chaves originais; não presuma rollback automático nem repita todo o atualizador cegamente. Esta coleção não fornece comando executável de deploy de produção.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
