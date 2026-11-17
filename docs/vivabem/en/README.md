# VivaBem

Documentation continuation, 2026-11-10: [current architecture](architecture/overview.md), [Cockpit](operations/technical-cockpit.md) and [executed tests](operations/backend-testing.md). Legacy modernization remains partial.


[English](README.md) | [Português brasileiro](../pt-br/README.md)

Laravel 12/PHP Portal with Blade/Alpine/Tailwind/Vite for patient and psychologist accounts, appointments, participation and notifications. MySQL holds Portal state; Redis supports authentication/transient state, Hub carries notices, Wallet owns purchases/balances and Cofre stores selected encrypted references. Current purchase and result-application paths exist in source; psychologist payouts remain unavailable.

Private installation. Current source, executed isolated checks, historical evidence and planned work are distinguished. No production/provider acceptance is claimed.

- [Catalog / Catálogo](index.md)
- [Architecture / Arquitetura](architecture/overview.md)
- [Contracts / Contratos](architecture/contracts.md)
- [FAQ](faq/index.md)
- [Historical source review / Revisão histórica](operations/source-review.md)
- [Bio](bio.md)
