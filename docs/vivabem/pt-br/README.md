# VivaBem

Continuação documental, 2026-11-10: [arquitetura atual](architecture/overview.md), [Cockpit](operations/technical-cockpit.md) e [testes executados](operations/backend-testing.md). Modernização do legado ainda parcial.


[English](../en/README.md) | [Português brasileiro](README.md)

Portal Laravel 12/PHP com Blade/Alpine/Tailwind/Vite para contas de pacientes e psicólogos, atendimentos, participação e notificações. MySQL mantém o estado do Portal; Redis suporta autenticação/estado transitório, Hub transporta avisos, Carteira mantém compras/saldos e Cofre referências criptografadas selecionadas. Há fluxos de compra e aplicação de resultados no código; repasses ao psicólogo permanecem indisponíveis.

Instalação privada. Código atual, verificações isoladas executadas, evidência histórica e planejamento são distintos. Não se afirma aceite de produção/provedor.

- [Catalog / Catálogo](index.md)
- [Architecture / Arquitetura](architecture/overview.md)
- [Contracts / Contratos](architecture/contracts.md)
- [FAQ](faq/index.md)
- [Historical source review / Revisão histórica](operations/source-review.md)
- [Bio](bio.md)
