# Trust boundaries — Hub VivaBem

[English](boundaries.md) | [Português brasileiro](../../pt-br/security/boundaries.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `e0ab75952946bc3f764dcb4144e404097277933f`.

<!-- reading-section: mechanisms -->

## Mechanisms and limits

Publisher policies control trusted kid/key/issuer/subject/project and channel/event/scope permissions. Tokens use audience hub-publication and a maximum 60-second lifetime; keys come from operator configuration, not token URLs. Recipient identity instead comes from a Portal session probe and same-origin/cookie checks. Publisher credentials do not grant browser receive access. CORS is not authentication; namespace ownership still depends on effective Redis ACL deployment. Allowed event names can remain after financial execution is retired.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
