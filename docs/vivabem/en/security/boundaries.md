# Access boundaries and partial-commit security behavior

[Contents](../index.md) | [Português brasileiro](../../pt-br/security/boundaries.md)

Reviewed 2026-11-10 at `d412cc7`. Audience: maintainers and security reviewers. A: source inspection, not penetration testing or certification. This chapter distinguishes product authorization, technical sessions and service callbacks without changing any mechanism.

<!-- reading-section: product -->
## Product identity and profile updates

`config/auth.php` selects the web guard with driver redis-session and user provider `Usuario`. `GuardaSessaoRedis` resolves the authorization credential through `SessaoAutenticacaoRedis`, checks consistency against the session's user identity and accepts cookie fallback only for persistent credentials. Passive probes do not qualify for activity renewal. Login rotates current context and revokes prior FCM association; logout revokes that context. This is not proof of all-device logout or Android device attestation.

`Controller::captureProfileAuthorization` requires matching profile OID, professional/patient role and resolved authorization before profile update. `preserveProfileAuthorization` is called after the profile transaction commits: it reloads the user, compares password fingerprints and attempts to preserve authorization after password change. A post-commit Redis failure may yield HTTP 503 explicitly stating that profile data was saved but authentication could not be confirmed. Otherwise invalid authorization redirects to login. Do not instruct users to assume rollback and blindly resubmit a committed profile update.

Read form endpoints, registration and profile-update actions do not share every ownership check; a route-level auth flag is not a complete audit of every read. `Usuario` hides password/remember_token/chave_pix from serialization, but raw DB access, exports and unreviewed payloads remain sensitive. Photo conversion and file cleanup are separate from SQL rollback.

<!-- reading-section: recipient -->
## Hub recipient probe

`SessaoHubControlador` supports configured database/file/redis/memcached session drivers, requires a 40-character alphanumeric session ID, clones the existing session driver and reads it without saving. It resolves the credential already stored in the session, then requires session guard user ID to equal the resolved user. It does not resurrect persistent cookie login when that session is missing.

Response contains purpose hub-recipient-session, project vivabem, userId and psychologist flag, with no-store/private and Vary Cookie. `routes/web.php` excludes normal session startup/save, CSRF and presence-renewal middleware from this probe while retaining cookie decryption. The endpoint authenticates the inspected current context, not arbitrary browser-supplied userId. Hub delivery/revalidation is a separate repository contract and was not executed here.

<!-- reading-section: operator -->
## Technical operator authorization

`AutenticarSaude` requires configured operator identity, matching credential fingerprint and a valid `SessaoPainelTecnico`. Invalid state clears technical authorization and returns JSON 401 or redirects to dedicated login. The technical Redis record has a 90-second TTL. Only an already-authorized heartbeat extends an existing key; a missing key is never recreated, and Redis failure returns false. Separate operator and product sessions therefore do not mean the current Cockpit is independent of Redis availability.

`AcessoPainel` and `config/panel_access.php` govern separate confirmation challenges, whose configured source TTL is 600 seconds. Challenge, technical session, product authorization, cookie and professional presence are different records and durations. Exact login/confirmation delivery and deployment access remain unverified; documentation does not bypass them.

Cockpit access can permit database editing, CSV exports and broker mutations according to actual action checks and effective account grants. It must remain private. Read-only Docker collection and environment-audit Docker execution are different capabilities; do not infer a globally read-only Portal infrastructure boundary. See [Cockpit](../operations/technical-cockpit.md).

<!-- reading-section: service -->
## Service claims, encryption and sensitive output

Financial callbacks validate their own HS256 issuer/audience/scope/time/subject and encrypted-body/path binding; the generic `JwtMiddleware` has a weaker missing-claim branch and is not their full contract. Encryption/integrity, authenticated service identity and business authorization are separate responsibilities. Approved credentials do not authorize an unrelated owner's appointment. [HTTP contracts](../api/index.md) specify actual fields/errors.

Do not log raw encrypted financial bodies, JWTs, signing keys, patient records or CSV contents as troubleshooting examples. Encrypted data can still be sensitive. The inspected callback diagnostics log stage/class/status; this does not establish a corpus-wide audit of every logging statement. No provenance snapshots or real environment values were added.

`DetectorRequisicaoAplicativoOficial` recognizes configured query/header/user-agent markers and a session flag; these are application context hints, not device attestation or independent identity. `ExecutorAuditoria::request` is operational even for list, which may create an absent proposal. Submission invokes global `--apply-audit`, then refreshes the selected project; selected-project UI does not prove selected-directory-only application. Never invoke list/submit as a documentation probe. These preserved boundaries were rechecked in source, without reading actual environment files.

<!-- reading-section: validation -->
## Evidence, gaps and maintenance

Sources: `config/auth.php`, `config/panel_access.php`, `app/Auth/GuardaSessaoRedis.php`, `app/Http/Controllers/{Controller,SessaoHubControlador,ResultadoCompraSaldoControlador,OperacaoFinanceiraInternaControlador}.php`, `app/Http/Middleware/{AutenticarSaude,JwtMiddleware}.php`, `app/Services/{AcessoPainel,SessaoPainelTecnico}.php`, `routes/web.php`, `bootstrap/app.php`.

The existing [suite](../operations/backend-testing.md) verifies selected login, registration, participation, notification and push rules with doubles/SQLite. It does not test the complete Redis guard, technical challenge, deployment permissions, all read authorization, collector or browser. Recheck both languages/collection after authentication, scopes, profile transaction handling, session lifetime or operator capabilities change. No security fix or new test was performed by this documentation task.
