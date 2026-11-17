# Financial operations, cards and provider ingress

2026-11-04. The delegated encrypted financial endpoint distinguishes purchase, refund and payment purposes. Balance/history reads, card preparation/association/deletion and status recovery have separate contracts. Orders webhook signature authentication differs from internal service JWT. Unknown provider outcome must retain the original transaction and correlation rather than imply rejection or authorize a fresh charge.

The source repository maintains detailed contracts and source evidence; review was static without database or provider access.

- [HTTP](../../../../../carteira-digital/docs/en/api/http-contracts.md)
- [Orders](../../../../../carteira-digital/docs/en/integrations/mercado-pago.md)
- [Recovery / Recuperação](../../../../../carteira-digital/docs/en/operations/reconciliation.md)

[Index / Índice](../index.md)

[Catalog HTTP / HTTP do catálogo](http-contracts.md)
