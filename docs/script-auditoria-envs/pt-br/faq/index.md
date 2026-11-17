# FAQ técnica — script-auditoria-envs

[English](../../en/faq/index.md) | [Português brasileiro](index.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `2e5d5de71d1323b4e588e04f06784324802ae0d3`.

<!-- reading-section: q001 -->

## Q001 — A chamada padrão é somente leitura?

Não. Ela sincroniza destinos, inclusive removendo nomes após backup. A prévia exige --dry-run ou --audit-only; no estudo, sempre forneça raiz explícita descartável.

<!-- reading-section: q002 -->

## Q002 — Uma proposta aplicada já está ativa?

Não. O resultado comprova apenas trabalho nos arquivos. Configuração em cache e processos duradouros podem manter estado antigo. Confira a ativação do consumidor, sem repetir cegamente a proposta após progresso parcial.

<!-- reading-section: q003 -->

## Q003 — Quais afirmações permanecem sem validação?

Recuperação após crash, corridas com editores não cooperantes, ACLs nomeadas em cada filesystem e ativação completa dos consumidores permanecem sem validação. A CLI não foi executada sobre configuração real.

[Evidence and limits / Evidências e limites](../operations/source-review.md)

[Failure scenarios / Cenários de falha](failure-scenarios.md)
