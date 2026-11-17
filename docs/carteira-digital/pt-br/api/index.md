# Operações financeiras, cartões e entrada do provedor

2026-11-04. O endpoint financeiro cifrado delegado distingue finalidades de compra, estorno e pagamento. Consultas de saldo/histórico, preparação/associação/exclusão de cartões e recuperação de status têm contratos separados. Autenticação da assinatura Orders difere do JWT interno. Resultado desconhecido do provedor deve preservar transação e correlação originais, sem implicar recusa ou autorizar nova cobrança.

O repositório de origem mantém detalhes e evidências de código; a revisão foi estática, sem acesso a banco ou provedor.

- [HTTP](../../../../../carteira-digital/docs/pt-br/api/http-contracts.md)
- [Orders](../../../../../carteira-digital/docs/pt-br/integrations/mercado-pago.md)
- [Recovery / Recuperação](../../../../../carteira-digital/docs/pt-br/operations/reconciliation.md)

[Index / Índice](../index.md)

[Catalog HTTP / HTTP do catálogo](http-contracts.md)
