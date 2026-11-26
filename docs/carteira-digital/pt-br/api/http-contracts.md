# HTTP

Revisão atual: 04/11/2026. O guia mantido na origem define rotas ativas, contratos criptografados vinculados ao titular, resultados e recuperação. Estruturas antigas `/api/compra` e webhook somente de validação não descrevem a implementação atual. Executores de pagamento/estorno externo continuam indisponíveis.

- [HTTP](../../../../../carteira-digital/docs/pt-br/api/http-contracts.md)
- [Reconciliation / Reconciliação](../../../../../carteira-digital/docs/pt-br/operations/reconciliation.md)

## Callback neutro de operação e pagamento interno — revisão de 2026-11-10

O produtor atual é `AdaptadorOperacaoFinanceiraPortal`, usando `/api/internal/financial-operations/{authorize,results}` com `wallet:operations:{authorize,results}`. O Portal mantém rotas financial-refunds de compatibilidade, mas elas não são o destino atual do produtor. Requisições vinculam corpo criptografado, POST/caminho e titular em JWT HS256 de 60 segundos; respostas devem ser strings JSON criptografadas com sucesso HTTP. A entrega do resultado também exige `persisted=true` descriptografado.

`operation=payment` usa `wallet:cards:payment`, exige UUID de atendimento e permite UUIDs opcionais de transação/tentativa e destino. Campos descriptografados desconhecidos, incluindo valores de pagamento fornecidos pelo chamador, são rejeitados. `destination=saldo` despacha `CasoDeUsoPagarPsicologoSaldo`; o Portal fornece autorização e composição coerente de bruto/taxa/líquido. Pagamento/estorno bancário rejeita `bank_transfer_unavailable`; suporte a callback não estabelece executor de repasse externo. A validação de compra exige separadamente centavos inteiros positivos, tentativa, finalidade, identidade do cliente e campos específicos do método; Pix proíbe dados de cartão. O código de erro HTTP pode ser o genérico `purchase_unconfirmed` mesmo para outras operações; somente o ramo de saldo insuficiente confirmado usa `insufficient_balance`.

Fontes: `routes/api.php`, `app/Http/Controllers/OperacaoFinanceiraControlador.php`, `app/UseCases/CasoDeUsoOperarOperacaoFinanceira.php`, `app/Adapters/AdaptadorOperacaoFinanceiraPortal.php`. Nenhuma aceitação real de endpoint/provedor foi executada. Revisar os contratos nos dois idiomas e o consumidor do Portal quando mudarem escopos, despacho ou confirmação.
