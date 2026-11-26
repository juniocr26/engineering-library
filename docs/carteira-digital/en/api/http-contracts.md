# HTTP

Current source review: 2026-11-04. The maintained source guide defines the active routes, owner-bound encrypted contracts, provider outcomes and recovery. Earlier `/api/compra` shells and validation-only webhook descriptions no longer describe this implementation. External payout/provider-refund executors remain unavailable.

- [HTTP](../../../../../carteira-digital/docs/en/api/http-contracts.md)
- [Reconciliation / Reconciliação](../../../../../carteira-digital/docs/en/operations/reconciliation.md)

## Neutral operation callback and internal payment — reviewed 2026-11-10

The current producer is `AdaptadorOperacaoFinanceiraPortal`, using `/api/internal/financial-operations/{authorize,results}` with `wallet:operations:{authorize,results}`. Portal retains financial-refunds compatibility routes, but they are not the producer's current destination. Requests bind encrypted body, POST/path and owner in a 60-second HS256 JWT; responses must be successful encrypted JSON strings. Result delivery additionally requires decrypted `persisted=true`.

`operation=payment` uses `wallet:cards:payment`, requires appointment UUID and permits optional transaction/attempt UUID and destination. Unknown decrypted fields, including caller-provided payment amounts, are rejected. `destination=saldo` dispatches `CasoDeUsoPagarPsicologoSaldo`; the Portal supplies authorization and a coherent gross/fee/net breakdown. Bank payment/refund dispatch rejects `bank_transfer_unavailable`; callback support does not establish an external payout executor. Purchase validation separately requires positive integer cents, attempt, purpose, customer identity and method-specific fields; Pix forbids card input. The HTTP error code may be generic `purchase_unconfirmed` even for other operation kinds; only the confirmed insufficient-balance branch uses `insufficient_balance`.

Sources: `routes/api.php`, `app/Http/Controllers/OperacaoFinanceiraControlador.php`, `app/UseCases/CasoDeUsoOperarOperacaoFinanceira.php`, `app/Adapters/AdaptadorOperacaoFinanceiraPortal.php`. No endpoint/provider acceptance was executed. Recheck both language contracts and the Portal consumer when scopes, dispatch or acknowledgement change.
