# Context validation, diagnostics and privacy boundaries

[Contents](../index.md) | [Português brasileiro](../../pt-br/security/context-and-diagnostics.md)

Reviewed 2026-11-10. Audience: catalog authors, integrators and security reviewers. A: current implementation inspection. Scope: minimization before writer dispatch; no regulatory certification, encryption guarantee or production access audit is implied.

<!-- reading-section: context -->
## Approved scalar context

`Dominio\CampoContexto` defines `nome`, `tipo='string'`, `anulavel=false`, `minimo=null`, `valoresPermitidos=[]`. Names match `[a-z][a-z0-9_]{0,63}`. Supported types are `string`, `integer`, finite `number` and `boolean`. Strict checks reject numeric strings, booleans masquerading as numbers, arrays, objects and nonnullable null. Missing approved fields are optional and omitted; allowed null, zero, false and empty string remain distinct.

`CampoContexto::normalizar` permits at most 32 unique fields. String shorthand maps `attempt/retry_delay_ms` to nonnegative integer, `duration_ms` to nonnegative number, `retry_scheduled/success` to boolean, ordinary names to string. `dependency/operation` require an explicit `CampoContexto` with a nonempty allowed-value list. Reserved conventional fields cannot be redefined with conflicting types. Lists accept at most 100 correctly typed values, compared strictly; approved strings must be valid UTF-8 and at most 1024 bytes. Numeric minima must be finite and numeric; conventional nonnegative fields cannot set a negative minimum.

`Aplicacao\SanitizadorContexto::sanitizar` iterates approved definitions, not the incoming object graph. Unknown fields are dropped without serialization. Even approved names matching its sensitive-name pattern are dropped before validation: password/senha, token, authorization, cookie, secret/private, patient/paciente, medical/medic, financial/finance, payment/pagamento, payload/body/corpo, binding/sql, request/response, prontuario/cartao/credential. This is a name filter, not semantic detection of sensitive values under innocuous field names.

Approved values are validated; strings are truncated to 1024 bytes, invalid UTF-8 is substituted and the final byte boundary is repaired to valid UTF-8. Keys are sorted. Lists are checked before truncation. Review field meaning before approval: allowing `text` does not make arbitrary clinical text safe. Caller-provided identity labels, correlation/request IDs, static definition message/impact, tag taxonomy and approved diagnostic messages also need privacy review; syntactic validators do not redact their contents.

<!-- reading-section: diagnostics -->
## Exception diagnostics

`Aplicacao\DiagnosticoExcecao` never copies Throwable messages directly or includes trace arguments. It emits `type`, a fixed approved `message` or `[REDACTED]`, `message_redacted`, `source`, bounded `frames`, bounded `previous`, and `truncation` (`frames_omitted`, `cause_chain_truncated`, `source_omitted`). Anonymous Throwable types become `anonymous_throwable`.

With no configured root, source locations are omitted. With a root, it must resolve to an existing directory other than `/`; `localizacao` includes only canonical files within it, with relative path at most 256 bytes using letters/digits/underscore/dot/slash/hyphen, plus line. Trace frames keep only permitted file/line and class/function/type strings up to 160 bytes matching the implementation's symbol pattern. Default limits are 12 frames and 3 total causes, configurable to 0–16 and 1–4. Truncation is explicit, not evidence that no deeper cause exists.

`mensagensAprovadas` maps exact exception class names to static nonempty UTF-8 strings up to 256 bytes. It substitutes approved text rather than approving runtime message contents, and does not automatically match parent classes. Class names and permitted symbol names can still reveal implementation structure; the corpus and output storage remain private. Configure only an approved application root and reviewed static messages.

<!-- reading-section: trust -->
## Trust and storage responsibilities

The registrar is the privacy boundary. Constructing `Dominio\Evento` and passing it directly to a writer bypasses that boundary; `Evento::paraArray` does not revalidate content. A custom `Gravador` can also retain data differently. Review custom adapters and the destination before adopting them. The library does not implement caller authentication, authorization, log encryption, credential custody or retention deletion.

The file writer creates new directories with requested `0700` and initializes marker/new empty daily-file permissions with `0600`. Existing directories are canonicalized but not chmod-hardened; existing nonempty daily files are not automatically permission-repaired. Operators must verify ownership, mounts and existing access. Symlink checks, single-link regular-file checks and inode/device identity checks reduce destination substitution hazards, but are not a general guarantee against privileged host attackers or every filesystem race. Directory input is resolved by `realpath`; do not claim that every symlink in the supplied directory path is forbidden.

Use dedicated private storage. No actual dotenv contents, credentials, patient records, payment payloads, source snapshots or real exception messages belong in examples. Writer failure causes may themselves contain sensitive external messages: do not blindly render chained exceptions to public output or recursively send them through the failing logger.

<!-- reading-section: evidence -->
## Verification and maintenance

Evidence: `src/Dominio/CampoContexto.php::{validar,normalizar}`, `src/Aplicacao/SanitizadorContexto.php::{sanitizar,excecao}`, `src/Aplicacao/DiagnosticoExcecao.php::{causa,localizacao}`, `src/Infraestrutura/GravadorArquivoDiario.php`. Existing assertions: `tests/Aplicacao/{ContextoTest,DiagnosticoTest}.php`, `tests/Dominio/CampoContextoTest.php`, `tests/Infraestrutura/{PsrTest,ArquivoDiarioTest}.php`. See [executed verification](../testing/verification.md).

Maintainers must recheck both languages after field approval, sensitive-name pattern, diagnostic class/root, serialization, permission or adapter changes. Tests with synthetic sentinel strings support stated cases; they do not prove every sensitive value is detected. Actual deployment permissions, collectors, private registry controls and consumer input policies remain outside this verification.
