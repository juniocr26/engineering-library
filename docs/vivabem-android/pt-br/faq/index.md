# FAQ técnica — VivaBem Android

[English](../../en/faq/index.md) | [Português brasileiro](index.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `07c3fa6cfcb8cd19cc6d271922684b304778ccd5`.

<!-- reading-section: q001 -->

## Q001 — DAL autentica o usuário?

Não. Verifica a relação pacote/certificado com a origem web. Autenticação e autorização Portal continuam decidindo acesso do usuário; permissão de notificação/entrega FCM são capacidades separadas.

<!-- reading-section: q002 -->

## Q002 — Pode regenerar chave para reparar assinatura debug?

Isso altera identidade e pode romper associação da origem e compatibilidade com o app instalado. Gradle exige deliberadamente identidade debug fixa existente; recupere material original autorizado e confira a associação, sem substituição silenciosa.

<!-- reading-section: q003 -->

## Q003 — Quais afirmações permanecem sem validação?

Verificação do certificado instalado, resposta DAL real, ciclo de aparelho/navegador, push negado/obsoleto, release assinado e publicação Play continuam sem validação. Associação token/autorização e filtragem completa por sessão exigem investigação adicional.

[Evidence and limits / Evidências e limites](../operations/source-review.md)

[Failure scenarios / Cenários de falha](failure-scenarios.md)
