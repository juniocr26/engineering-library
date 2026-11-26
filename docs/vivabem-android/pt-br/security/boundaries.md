# Fronteiras de confiança — VivaBem Android

[English](../../en/security/boundaries.md) | [Português brasileiro](boundaries.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `07c3fa6cfcb8cd19cc6d271922684b304778ccd5`.

<!-- reading-section: mechanisms -->

## Mecanismos e limites

Digital Asset Links associa pacote/certificado à origem web; não é login de usuário. URI de abertura segura impede entrada em origem não confiável, sem autorizar ação de domínio. Push recebido pode estar obsoleto: releia estado atual autorizado antes de agir. Permissão de notificação negada não indica logout. Nenhum keystore, certificado, credencial Firebase ou token pessoal foi aberto.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
