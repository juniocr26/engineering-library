# Portal HTTP contracts and financial callback boundaries

[Contents](../index.md) | [Português brasileiro](../../pt-br/api/index.md)

Reviewed 2026-11-10 at `d412cc7`. Audience: integration and backend maintainers. A: inspected routes/controllers, not executed HTTP/provider acceptance. Prefix `/api` is registered by `AppServiceProvider`; product web/auth routes use web middleware. The generic JWT middleware is not the financial callback's complete security contract.

<!-- reading-section: routes -->
## Route families and authorization

| Boundary | Routes / owner | Access and side effects |
| --- | --- | --- |
| Login/activation/reset | `routes/auth.php`, `ControladorAutenticacao` | Product session lifecycle; activation/reset credentials are sensitive |
| Patient/professional profiles | `routes/web.php`, profile controllers/FormRequests | Public registration and authenticated edit routes; auth alone does not establish ownership of every read |
| Appointments | `/atendimento/*`, `/psicologos/agendamento/*` | Product auth, participant/state checks in operation; scheduling, cancellation, rescheduling and conference actions |
| Purchases/cards | `/transacoes/*`, `ControladorTransacao` | Authenticated coordination with Wallet/Cofre; token/card reference is not approval |
| Push web | `PUT/DELETE /notificacoes/push/inscricao` | Product auth and web CSRF |
| Push API | `PUT/DELETE /api/fcm/registrations` | `auth:sanctum`; registration/removal |
| Purchase results | `POST /api/internal/balance-purchases/results` | Controller-validated service JWT plus encrypted body and mandatory effects |
| Financial operations | `POST /api/internal/financial-operations/{acao}` | Controller-validated service capability; authorize/results only |
| Refund compatibility | `POST /api/internal/financial-refunds/{acao}` | Refund-only compatibility and separate scope prefix |
| Hub recipient probe | `GET /hub/recipient-session` | Existing authorization, read-only session probe; excludes normal session-save/presence middleware |
| Technical operators | `/health/*`, `/audit/*` | Dedicated technical sessions and CSRF, independent of product login |

This is a boundary map, not a claim that every route uses an identical status/body. Browser form handlers may redirect, JSON controllers validate fields, and domain methods can reject ownership/state. The [Cockpit reference](../operations/technical-cockpit.md) documents operator endpoints separately. `/api/compra` and `psychologists/payments/webhook-results` are not current entries in inspected `routes/api.php`.

<!-- reading-section: callback-auth -->
## Financial callback authentication

`ResultadoCompraSaldoControlador` and `OperacaoFinanceiraInternaControlador` require outer `body` as a string, decode a Bearer HS256 token, require configured nonempty service user/password matching claims, issuer `carteira-digital`, audience `vivabem`, expected scope, integer iat/exp valid at receipt and lifetime at most 60 seconds. Request binding uses SHA-256 of `POST`, newline, actual slash-prefixed request path, newline and the encrypted body. Sub must equal decrypted oid_usuario and environment must equal configured Mercado Pago environment.

This prevents treating a valid signature alone as authority to mutate arbitrary owners/paths/bodies. It does not document secret values or prescribe creating keys. The controllers decrypt JSON at bounded depth before field validation. Do not send synthetic callback requests to a live installation as a test: accepted callbacks can create durable business effects.

<!-- reading-section: purchase -->
## Purchase result input and outcome

Purchase-result scope is `wallet:purchases:complete`. Decrypted contract:

| Field | Validation / meaning |
| --- | --- |
| `oid_usuario` | Required string, max 36; matching subject and existing user |
| `transaction_id`, `attempt_id` | Required UUIDs |
| `purchase_status` | Required approved/refused/pending |
| `environment` | Required teste/producao, matching configuration |
| `event_id` | Required string max 100, exactly balance-purchase: plus transaction_id |
| `amount_cents` | Optional integer 1–9999999999; mandatory for conversion branch |
| `payment_method` | Optional pix marker |
| `purpose` | Optional compra_saldo/atendimento_emergencial/atendimento_agendado/atendimento_imediato |
| `appointment_id`, `duration_minutes` | Nullable UUID / integer 1–1440 |
| `outcome_unconfirmed` | Optional boolean; must be true for pending |
| `convertida_em_saldo`, `data_compra_original` | Conversion requires approved appointment-purpose result, amount and original date |
| `pix_simulado` | Optional boolean; true requires configured teste and coherent local/testing application environment |

Approved appointment Pix that is not converted to balance delegates to `CasoDeUsoAplicarCompraAtendimentoPix`; other results delegate to `CasoDeUsoAplicarResultadoCompraSaldo`. Ordinary successful application responds `persisted=true`; the Pix branch returns its use-case result. This acknowledges application effects, not a new payment-provider execution.

Failure responds `persisted=false, code=purchase_effects_unconfirmed`. HTTP exceptions retain status; signature/UnexpectedValueException handling maps to 401; otherwise fallback is 503. Validation and mandatory-effect failures are logged by stage with exception class/status, without logging the financial body. A failed response does not justify repeating the original payment operation.

<!-- reading-section: operations -->
## Refund/payment authorization and results

Neutral scopes are `wallet:operations:authorize` / `wallet:operations:results`; compatibility uses `wallet:refunds:authorize` / `wallet:refunds:results`. Accepted actions are authorize/results. Compatibility rejects payment operations. Required decrypted fields include oid_usuario, environment and appointment_id UUID; operation defaults to refund or accepts payment. original_transaction_id is required unless payment.

For results, refund uses refund_transaction_id, refunded and refund_status; payment uses transaction_id, completed and operation_status. IDs/attempt_id are UUIDs, status approved/refused, completion flag boolean, amount integer 1–9999999999 and optional balance_after_cents 0–9999999999. Payment requires purpose pagamento_saldo and breakdown with positive gross/net cents, nonnegative fee cents and percentage 0–100. Refund purpose, when present, is estorno_saldo/estorno_pix; retryable is optional boolean.

Dispatch selects `CasoDeUsoEstornoAtendimento` or `CasoDeUsoPagamentoPsicologo` and calls autorizar/concluir. Successful result is encrypted JSON returned as a JSON string; it is not the purchase callback's persisted object. Failure is `persisted=false, code=financial_operation_unconfirmed`, with HTTP exception status or 503. Controller acceptance of a payment-shaped payload is not proof that all psychologist payout flows work; [architecture](../architecture/overview.md) documents partial financial functionality.

<!-- reading-section: push-balance -->
## Push registration and balance reads

`RegistroFcmControlador::store` accepts registration_id (aliases fid/token), target_type fid/token, optional platform web/android/ios, device_id max 255 and context_proof exactly 64 lowercase hexadecimal characters. Registration string max is 512. It delegates ownership/context rules to `CasoDeUsoRegistroPush` and returns ok/enabled on success; removal accepts the same registration aliases and returns ok. A stored registration is not confirmed delivery or professional availability. Existing tests verify ownership and prevention of Android-to-web downgrade.

`LeitorSaldo::read` derives owner from Auth rather than caller input. It encrypts the owner, signs scope `wallet:balance:read` with request binding for `POST /api/get_saldo`, disables redirects and uses configured timeout (default 10, minimum 1 second). It requires HTTP 201, an encrypted JSON string, status sucesso and decimal string content.saldo matching up to eight integer digits and two decimals, optionally negative. Failures become service-unavailable, never fabricated zero balance.

<!-- reading-section: evidence -->
## Evidence and maintenance

Sources: `routes/{api,web,auth,health}.php`, `app/Providers/AppServiceProvider.php`, `app/Http/Controllers/{ResultadoCompraSaldoControlador,OperacaoFinanceiraInternaControlador,RegistroFcmControlador}.php`, `app/Services/LeitorSaldo.php`, `bootstrap/app.php`. Current tests and gaps are documented in [testing](../operations/backend-testing.md). Recheck producer/consumer contracts, both languages and collection after routes, claims, field requirements, encryption, states or error mappings change. Provider homologation, replay behavior of every downstream use case and complete HTTP integration remain unverified here.
