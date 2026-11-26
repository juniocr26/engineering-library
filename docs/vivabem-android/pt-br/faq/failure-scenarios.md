# Raciocínio sobre falhas — VivaBem Android

[English](../../en/faq/failure-scenarios.md) | [Português brasileiro](failure-scenarios.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `07c3fa6cfcb8cd19cc6d271922684b304778ccd5`.

<!-- reading-section: q004 -->

## Q004 — Onde termina a consistência?

Preferências nativas mantêm estado local de notificação/token; bancos do Portal continuam como autoridade de consultas e identidade. Gradle valida o keystore debug fixo existente apenas na assinatura debug, sem fallback gerado. Assinatura release exige keystore de upload existente e senhas de ambiente. Certificados de upload, debug e distribuição Play são identidades diferentes; build local não comprova certificado instalado pela Play.

<!-- reading-section: q005 -->

## Q005 — Como conduzir a investigação?

Revise LauncherActivity, serviço de mensagens e app/build.gradle antes de alterar build. Em verificação futura autorizada em aparelho, teste deep link hostil, permissão ausente, logout/revogação do contexto atual, push atrasado e certificado incompatível. Preserve a identidade fixa de assinatura; não regenere chaves para passar o build. Build, assinatura, upload Play e release são procedimentos separados, não executados aqui.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
