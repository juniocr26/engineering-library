# Read API security and future payment boundaries

[English](read-api-boundaries.md) | [Português brasileiro](../../pt-BR/security/read-api-boundaries.md)

Static source review: 2026-10-10. Implemented facts, general theory and hypothetical changes are distinguished below. Runtime commands were not executed.

Spring Security permits specific product/health GETs and dev-profile OpenAPI, then denies all other routes. There is no persisted login, role model or authenticated administrator. CORS only allows configured origins, GET, Accept/Content-Type and no credentials; non-browser clients do not enforce CORS. Stateless sessions and disabled CSRF match the current read-only surface but do not establish a safe future cookie-authenticated write design. Blocked routes produce generic 403 Problem Details.

The base config hides messages/stack traces/binding errors from server responses. `ApiExceptionHandler` logs unexpected exceptions while returning generic 500. Detailed logs require restricted access/redaction: client sanitization does not sanitize server diagnostics. Environment-based database credentials are configuration, not embedded public documentation; this review did not read real environment files. Local database ports are loopback-bound; that is development isolation, not an audited production perimeter.

Stripe is not implemented: no SDK consumer, binding, webhook verification, provider call or injected Compose Stripe key exists. A reserved template entry does not change that. Future reconciliation would need authorized review operations, provider-event authentication, duplicate/replay policy and audit records. Signed provider payloads, TLS, application identity and idempotency protect different boundaries; none may be claimed from the existing CORS/catalog policy. These are hypothetical requirements, not delivered security controls.
