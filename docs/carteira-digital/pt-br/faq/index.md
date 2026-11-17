# FAQ técnica — carteira-digital

2026-11-04. Revisão estática dos contratos atuais; sem chamada ao provedor.

[Index / Índice](../index.md)

<!-- reading-section: q001 -->

## Q001 — A verificação da assinatura credita saldo?

A assinatura autentica a entrada. CasoDeUsoProcessarNotificacaoCompra consulta Orders autenticado e valida correlação antes dos efeitos financeiros. Notificação suportada pode retornar accepted=true/processed=true, enquanto falhas de processamento ainda podem retornar 503. Assinatura ou aceite isolados não comprovam pagamento aprovado nem crédito persistido.

<!-- reading-section: q002 -->

## Q002 — Por que saldo ausente difere de indisponível?

Saldo ausente do proprietário é leitura explícita zero/exists=false sem inserção. Duplicidade, delegação inválida, falha criptográfica ou falha de banco não podem virar zero. A migration de unicidade recusa duplicados em vez de somar saldos; aplicação no ambiente não foi conferida.

<!-- reading-section: q003 -->

## Q003 — Quais afirmações permanecem sem verificação?

Aprovação real do provedor, homologação de débito, concorrência SQL real, recuperação completa do broker e aceite em produção não foram verificados nesta tarefa. Compras externas e reconciliação possuem implementação; esse fato não permite inventar uma inbox durável separada de webhooks.

## Cartão salvo ou webhook assinado comprova pagamento concluído?

Não. Tokenização, associação do cliente, armazenamento cifrado, aprovação do provedor, efeito financeiro SQL e entrega ao Portal são resultados distintos. A simulação local Pix também é distinta da confirmação do provedor.

[Integration / Integração](../integrations/mercado-pago.md) · [Failure scenarios / Cenários de falha](failure-scenarios.md) · [Source / Origem](../../../../../carteira-digital/docs/pt-br/architecture/current-implementation.md).
