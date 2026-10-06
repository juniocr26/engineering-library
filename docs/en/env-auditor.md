# ENV Auditor technical interview study guide

[English](env-auditor.md) | [Português brasileiro](../pt-BR/env-auditor.md)

Use this guide to understand and explain the problem, execution flow, decisions, alternatives, guarantees, risks and limitations. Suggested answers are study material, not a script to memorize or evidence of professional experience. Repeated explanations in the original study notes are consolidated here; literal examples are retained in the appendix. Source paths refer to the `env-auditor` repository.

Code review corrections: configuration loads before discovery; possible-secret checks precede synchronization. Blocking synchronization does not stop later unused-key cleanup. Strict mode sets the final exit code after processing and does not prohibit writes. Each file is read once per project scan, but nested project scans can overlap. `ignore_projects` is not complete isolation from a parent's usage scan. File symlinks can reach outside the workspace. Reports omit assignment values, but paths, keys and configuration diagnostics are not a general redaction guarantee. No automated regression suite is checked in; proposed tests below are not claimed results.

## 1 Overview

ENV Auditor is a Python CLI for auditing, synchronizing and cleaning `.env`, `.env.*` and `.env.example`. Each directory is an independent environment set. The example is a shared key contract; real values remain separate. After synchronization, the tool classifies runtime references as strong, weak or absent. Default execution removes keys without evidence. Review controls include dry-run, audit-only, backups, possible-secret checks, preservation of weak evidence and explicit external-variable exclusions.

## 2 The problem

Environment files drift: a production-only key may be absent from the example, a removed feature leaves obsolete configuration, or a real credential appears in a public example. The workflow makes discovery, comparison, synchronization, usage review, cleanup and final parity observable. It maintains local file contracts; it does not replace a secret manager or configuration platform.

## 3 The central contract

`.env.example` represents expected keys. Synchronization is asymmetric: real `KEY=real-value` contributes only `KEY=` to the example. An example assignment block may supply a safe default to a real environment missing that key. Real environment values are never copied between environments or back into the example.

## 4 Execution flow

Load optional configuration → discover projects/environments/example → check possible secrets before synchronization → synchronize key structure → build known keys → discover runtime/configuration candidates → classify strong/weak/no evidence → preserve referenced/excluded keys → remove keys without evidence → reload → validate final parity. Structural consistency and usage analysis are related responsibilities. A secret finding blocks synchronization, not every later mutation.

## 5 Why Python

Filesystem traversal, text parsing, regex, JSON, arguments and backups are available in Python 3.10+ standard library. No web framework, database or external package setup is needed. Go, Rust or Node.js could implement the same idea; the choice fits a local automation problem and is not a claim of unique superiority.

## 6 Why no dotenv dependency

`python3 scripts/audit-envs.py` needs no package installation. The cost is ownership of parsing and edge cases. A specialized library or formal input specification becomes reasonable if full dotenv compatibility is required.

## 7 Project discovery

`os.walk` recursively finds directories with `.env`, `.env.*` or `.env.example`. An `api/` directory and a `worker/` directory with separate environment files become independent sets. Discovery relies on location, not a framework manifest.

## 8 Real environment files

`is_env_runtime_file` accepts `.env` and custom `.env.*` names, excluding `.env.example` and backup names such as `.env*.bak.*`. Old backups must not become active environments in subsequent synchronization.

## 9 Why parity

The intended contract is `keys(.env.example) = keys(.env) = keys(.env.prod) = keys(.env.test)`. This answers which settings the system may need; equal keys do not mean equal or semantically valid values.

## 10 Production-specific variables

A key found only in `.env.prod` enters the directory's shared contract as an empty example assignment and can propagate to other environments. Uniform keys reduce drift but sacrifice flexibility for deliberately different environment schemas. Separate schemas or key groups would be a new design.

## 11 Why values remain separate

Copying complete production files could leak credentials or incorrect settings. A production `DATABASE_PASSWORD` absent from the example contributes only an empty assignment. It is not copied to local/test environments.

## 12 Why example blocks may propagate

Examples are expected to hold versionable defaults such as `APP_ENV=local`, `CACHE_DRIVER=file` and `PORT=8080`. Copying a missing assignment preserves that default. This depends on a safe example and differs from handling potentially sensitive real values.

## 13 No example file

When real environments exist without an example, the union of their keys creates `.env.example`. Real `A=1`, `B=2`, `A=10`, `C=30` produce empty A/B/C assignments, not those values.

## 14 Example-only projects

The tool can create `.env` from an example after checking sensitive-looking names and placeholders. A suspected real secret blocks creation. It does not invent `.env.prod`, `.env.test` or other environments that do not already exist.

## 15 Parsing assignments

The parser recognizes assignments and optional `export` with identifiers matching `[A-Za-z_][A-Za-z0-9_]*`. It records the key, extracted value and original assignment block. Keeping `EnvEntry.block` matters when copying defaults; parsing is more than a naive split of every line.

## 16 Multiline values

Quoted multiline assignments continue until quote closure, accounting for simple escapes. Removal follows the whole assignment block, avoiding orphaned fragments. An unterminated quote may absorb following lines, so malformed input remains a risk.

## 17 Parser limits

This is a supported subset, not universal dotenv syntax or evaluation. The tool does not execute shell or resolve interpolation. Malformed/non-assignment lines are not comprehensively validated. A specialized parser or explicit format specification would be needed for broader semantics.

## 18 Duplicate detection

The parser keeps all key occurrences and uses `Counter` to report frequencies above one. Repeated `PORT` assignments can be interpreted differently by consumers, so duplicates are meaningful findings.

## 19 Why both list and dictionary

A dictionary hides duplicate occurrences and retains the last recognized block. The occurrence list detects duplication; the dictionary supports lookup. Detection does not automatically repair duplicates or establish the application's effective value.

## 20 Possible-secret detection

The example heuristic checks sensitive terms including SECRET, PASSWORD, PASS, TOKEN, PRIVATE, CREDENTIAL, CLIENT_SECRET, APP_KEY and API_KEY, then checks known safe placeholders. Accepted forms include change/changeme, placeholder, example, dummy, fake, your_..., xxx, angle-bracket placeholders, null, booleans, 0/1 and `base64:`. It is a narrow guard, not a complete secret scanner.

## 21 No secrecy guarantee

An innocuous variable name can conceal a credential; a safe default under a sensitive name can be flagged. This additional guard does not replace dedicated scanning or security review.

## 22 `public_non_secret_keys`

An explicit allowlist such as `PUBLIC_CLIENT_KEY` bypasses the heuristic for intentionally public settings. It reduces particular false positives without disabling checks for every key.

## 23 Usage classification

The scanner searches runtime/configuration files using known keys. Strong means a recognized access pattern; weak means an exact relevant token without a recognized accessor; absent means no evidence found. Strong and weak preserve the key.

## 24 Strong examples

Supported forms include PHP/Laravel `env('DB_HOST')`, shell/Compose `${DB_HOST}` and `$DB_HOST`, Node `process.env.DB_HOST` and `process.env["DB_HOST"]`, Vite `import.meta.env.VITE_API_URL`, Python `os.getenv("DB_HOST")` and `os.environ["DB_HOST"]`, and Java/Kotlin `System.getenv("DB_HOST")`. Custom getEnv-style helpers are also recognized. See the literal appendix and subject project's guide for the complete helper list.

## 25 Regex versus AST

Language-specific ASTs can improve precision but require parsers and maintenance across PHP, JS, Python, Java, shell and configuration formats. Regex keeps explicit patterns simple and extensible; weak evidence conservatively covers unrecognized access. Neither layer proves semantic use.

## 26 Weak evidence

Standalone uppercase tokens are intersected with known keys. `SOME_FEATURE_FLAG` in an unfamiliar structure is retained because there is evidence but insufficient certainty to delete it.

## 27 Why retain uncertainty

Keeping a stale setting is often less damaging than removing a required one. Conservative retention accepts manual review and false positives in exchange for fewer aggressive deletions.

## 28 Potentially unused

No detected reference is not proof of no runtime use. CI/CD, Kubernetes, systemd, Docker Swarm, external scripts, hosting platforms, server configuration, other services or dynamic access may consume the setting outside the scanned tree.

## 29 The main static-analysis failure

A deployment platform may require `SERVICE_PORT` even though no source file contains its name. External knowledge must supplement the scanner.

## 30 `ignore_unused_keys`

An explicit list such as `SERVER_INJECTED_VARIABLE` preserves externally consumed keys despite absent references. This documents knowledge the source scanner cannot discover.

## 31 Declarations are not consumption

`.env`, `.env.*`, `.env.example` and `.env-audit.json` do not count as runtime evidence. Otherwise each declaration would justify itself and make stale-key detection impossible.

## 32 Why ignore documentation

READMEs can contain old settings, examples and tutorials. Their mentions do not establish runtime consumption and would retain obsolete configuration indefinitely.

## 33 Why ignore binaries and assets

Images, fonts, archives, executables and local database files add I/O, noise and meaningless token matches. Filtering them avoids interpreting arbitrary bytes as relevant text.

## 34 Avoiding repeated reads per key

Instead of looping over every key and rereading every file, each project scan reads a candidate once, runs extractors, collects tokens and intersects with known keys. Nested project scans can still overlap.

## 35 Complexity

Work depends on total text bytes, applicable regex passes and filesystem traversal, not just file count. A 1 KB file and a 100 MB file have different costs. Do not claim constant memory or a universal `O(files)` performance result.

## 36 Automatic removal

Normal mode removes a key if it has no strong evidence, weak evidence or explicit exclusion. Removal applies wherever it occurs in the example and real environments. Reporting names/files does not require exposing assignment values.

## 37 Risk of default writes

Automation corrects drift but acts on incomplete evidence. Weak retention, external exclusions, backups, dry-run, audit-only and usage evidence reduce risk without eliminating it. Review unfamiliar projects with `--dry-run --show-usage` first.

## 38 Dry-run

`--dry-run` simulates synchronization, new-file creation and cleanup without writing. Virtual key sets represent the projected state rather than only existing physical files.

## 39 Why virtual state

If a real environment exists without an example, dry-run plans example creation while leaving the file absent. Subsequent parity checks use `SyncAction` updates to virtual key sets so they reflect that intended state. This is not a full transactional content plan; per-file removal reports can omit keys that would first be created.

## 40 Audit-only

`--audit-only` reports the current state without synchronization or removal; dry-run previews future normal behavior. One observes the present, the other simulates a change.

## 41 Mutually exclusive review modes

`--audit-only --dry-run` is rejected to avoid ambiguous CLI intent, rather than because combining the underlying mechanisms is technically impossible.

## 42 Backups

Before modifying an existing file, the default workflow creates a timestamped copy under `.env-audit-backups/`. It attempts 0700 directory and 0600 file permissions where supported. Newly created files have no earlier version to copy.

## 43 Sensitive backup contents

A backup contains real environment values. It is not sanitization, encryption or secret management. Production use would require deliberate retention, location, access permissions, encryption where appropriate, cleanup policies and exclusion from version control.

## 44 Disabling backups

`--no-backup` may suit externally managed snapshots or regenerable files, but removes a recovery layer and should be a deliberate choice.

## 45 Non-transactional writes

Files are changed individually with direct writes, not a global transaction or automatic coordinated rollback. Failure can leave partial synchronization. Stronger guarantees could stage all outputs, validate them, use temporary files/atomic renames, journal changes and coordinate rollback.

## 46 Concurrent invocations

There is no explicit global locking. Two runs can read different states and overwrite the same files. Run maintenance sequentially; process/filesystem locking would be a future requirement.

## 47 Strict mode

`--strict` returns exit 1 for remaining structural findings such as missing example/environment, divergence, duplicates or possible secrets. It evaluates after processing and is not a preflight write gate. A pipeline can use the exit code, but read-only CI should select audit-only too.

## 48 Strict unused

`--strict-unused` requires `--strict` and adds no-evidence keys to failure criteria. Normal cleanup may remove those findings first; audit-only is useful when CI should detect them without modifying files.

## 49 Findings and severity

Weak evidence represents uncertainty and does not trigger automatic removal or strict failure by itself. Structural divergence, duplicates and possible secrets are different findings. Not every warning should have identical consequences.

## 50 Usage evidence output

`--show-usage` names files such as `config/database.php` and `docker-compose.yml` supporting a `DB_HOST` finding. It makes decisions reviewable rather than merely asserting usage.

## 51 Optional JSON configuration

`.env-audit.json` supplies `public_non_secret_keys`, `ignore_unused_keys`, `ignore_projects` and `ignore_files`. Declarative workspace exceptions keep the general mechanism separate from local policy.

## 52 The scanner's configuration is not evidence

Putting a key in an ignore rule must not manufacture a weak reference. `.env-audit.json` configures the auditor, not the application consuming the key.

## 53 File and project exclusions

`ignore_projects` prunes project discovery; `ignore_files` filters usage candidates and matching directories. Generated files, legacy content and snapshots may need exclusions, but incorrect exclusions conceal real consumption. These lexical rules are not a filesystem sandbox or complete isolation of nested projects.

## 54 Default ignored directories

`.git`, node_modules, vendor, `__pycache__`, `public/build`, `bootstrap/cache`, IDE directories and backup storage are skipped to avoid dependency/generated noise and unnecessary text volume. A dependency's token is not necessarily the audited application's configuration.

## 55 Usage scope

Each scan starts at its detected project directory instead of scanning unrelated siblings. A common key name in another project should not justify this project's key. Recursive parent scans can still include nested project content; the implementation does not provide strict subtree ownership.

## 56 Encoding errors

Reads use ignore or replacement handling in relevant places to keep imperfect UTF-8 from stopping every scan. This operational robustness can discard evidence, change bytes during rewriting or miss references; it is not strict parsing.

## 57 Terminal output

Reports are designed to show key names, not assignment values, reducing accidental terminal, CI-log, screenshot and observability exposure. Paths/key names and malformed-configuration diagnostics can still contain sensitive text. Do not present this as comprehensive arbitrary-input redaction.

## 58 Why inspect examples rather than real secrets

Real environments commonly require credentials. The specific guard prevents unsafe values propagating from a versionable example. Whether real environments are committed or exposed is a broader secret-management policy.

## 59 Suspect examples

Synchronization and example-based creation are blocked if the trusted source looks unsafe. Default unused cleanup can still run on other keys. To investigate without writes, use audit-only; a possible-secret finding is not a global mutation prohibition.

## 60 `SyncAction`

An action records `target`, `kind` and `keys`, including CREATE_EXAMPLE_FROM_ENVS, ADD_KEYS_TO_EXAMPLE, CREATE_ENV_FROM_EXAMPLE and ADD_KEYS_TO_ENV. Dry-run applies them to projected key sets, partially separating planning from physical execution.

## 61 Is it Command Pattern

There is a conceptual resemblance, but `SyncAction` does not encapsulate complete execution/undo behavior. Describe the concrete planned synchronization model before assigning a formal pattern name.

## 62 Is it Clean Architecture

The script separates configuration, traversal, parsing, discovery, evidence, secrets, reporting, backup/write, synchronization, audit and CLI functions. It does not implement formal domain/use-case/adapter layers. Additional layers need a concrete maintenance benefit.

## 63 SOLID

Parsing, discovery, evidence, synchronization and backup have understandable responsibilities; `AuditConfig` carries policy. This is pragmatic separation, not a formal demonstration of every SOLID principle or a requirement for a class/interface per function.

## 64 Functions and dataclasses

`parse_env`, `is_ignored`, `analyze_usage` and `suspicious_example_keys` are naturally bounded operations. `EnvEntry`, `EnvFile`, `AuditConfig`, `UsageEvidence` and `SyncAction` model useful state without unnecessary object lifecycles.

## 65 Global configuration

Static sets and regex are global policy data; per-run configuration is passed through `AuditConfig`. The sets are treated as static, not enforced immutable by Python. Plugins, multiple policies or better test isolation could justify injected rule objects.

## 66 Adding a language

Start from real environment-access syntax, such as C# accessors. Add a reliable extractor to `STRONG_USAGE_EXTRACTORS` if sufficient; introduce specialized scanners only when maintenance or accuracy warrants them.

## 67 Regex false positives

A comment/string containing `process.env.OLD_VARIABLE` may count as strong evidence because parsing is not AST-aware. The consequence is conservative retention; richer parsers could reduce stale-key false positives.

## 68 False negatives

Dynamic `name = build_variable_name(); os.environ[name]`, ignored/unreadable files and external configuration can conceal use. Weak evidence and exclusions acknowledge uncertainty rather than proving completeness.

## 69 Uppercase weak tokens

Names such as DATABASE_URL, REDIS_HOST and FEATURE_FLAG_X are conventional, and intersecting tokens with known keys narrows candidates. Parsed keys can be lowercase; uppercase-only weak evidence is a heuristic, not a universal environment-variable definition.

## 70 Main trade-off

Automation improves maintenance while certainty remains incomplete. Strong, weak and explicitly ignored keys are preserved; zero evidence is a cleanup candidate. Review modes and backups mitigate the remaining risk.

## 71 Uniform contracts versus flexibility

Shared keys improve consistency and predictability. Deliberately environment-specific contracts lose flexibility; parity is this tool's model, not a universal rule of configuration management.

## 72 Zero dependencies versus parser responsibility

Simple execution, distribution and fewer transitive dependencies mean the project owns parsing, compatibility, heuristics and edge cases. Greater format complexity can change that trade-off.

## 73 Idempotence

A stable set of synchronized keys with unused settings removed should converge so a second run makes no changes. This is an intended property, not a formal guarantee across all inputs without specific regression tests.

## 74 Write failure

Filesystem exceptions may stop execution after earlier files changed. Recovery relies on backups/manual restoration; coordinated plan/commit/rollback is a possible improvement.

## 75 Large files

Usage scans read whole files into memory for regex. Very large text files increase memory and latency. Size limits, streaming, parallelism, hash caches or changed-file scans should follow measurements.

## 76 Sequential processing

No current parallel scan. Sequential work simplifies output and exceptions. Threads/processes could help measured bottlenecks but add coordination, resources and result ordering.

## 77 Progress feedback

Progress every 250 files keeps a large scan from appearing stuck without printing one line per candidate.

## 78 No environments

A workspace without `.env`, `.env.*` or `.env.example` reports nothing to audit and is not inherently a structural failure.

## 79 Exit codes

Human output and automation serve different needs. Strict findings return 1; handled configuration errors can return 2, while argparse also handles invalid options. Non-strict runs can return 0 with findings. Not every filesystem exception follows the handled configuration-error path.

## 80 CI integration

Start read-only, for example `python3 scripts/audit-envs.py --audit-only --strict --show-usage`. A pipeline may report/fail, a developer reviews dry-run locally, and changes enter through a PR. Automatic CI fixes need separate operational policy; no CI workflow is delivered here.

## 81 Larger-team distribution

Consider behavior tests, CLI versioning, packaging, configuration schema, structured logs/JSON, configurable policy, locking, atomic writes, rollback, symlink boundaries, file classification, language scanners, performance metrics, CI, specialized scanning and backup retention. Each addition needs a real requirement.

## 82 Production readiness

The tool is functional with explicit safety mechanisms, but static uncertainty, regex errors, partial writes, absent locks, sensitive backups and parser/secret heuristics remain. Avoid a context-free production-ready claim.

## 83 Greatest limitation

A source tree is not a complete runtime view. No reference is not proof a variable is unnecessary, especially when default mode removes keys automatically.

## 84 Most interesting decision

Combining synchronization with conservative evidence creates an intermediate state between confident recognized access and no evidence. This makes precision versus false-removal risk an engineering discussion rather than a regex checklist.

## 85 Lessons

Declaration differs from use; no evidence differs from proof; backup differs from transaction and secret protection; regex differs from semantic understanding; placeholders differ from complete scanning; dry-run differs from audit-only; equal keys differ from equal values; examples are not credential storage; weak evidence differs from strong evidence.

## 86 Why not a text diff

A two-file diff treats order, comments and values as differences. This tool handles multiple environments, key union, creation, safe defaults, duplicates, secrets, evidence, cleanup, backups, simulations and exceptions with a key-based contract.

## 87 Why Git is insufficient recovery

Real secrets should often be untracked, so Git cannot restore their immediate pre-change contents. Timestamped backups address that gap; Git remains another layer for tracked files.

## 88 Secret managers

Vault or infrastructure secret services manage storage, access, distribution and rotation. ENV Auditor maintains existing file contracts and can coexist with externally supplied secrets; it does not replace those services.

## 89 Why no value types

Current validation concerns key existence and references. Integer, boolean, enum, URL, required/default and environment-specific constraints would introduce a new semantic schema responsibility.

## 90 A possible typed schema

An explicit schema could declare PORT as required integer and APP_ENV as an enum of local/test/production. Separate key parity from semantic value validity instead of inferring everything from examples. This is a proposed design, not current configuration support.

## 91 Improving secret detection

Known token patterns, entropy, optional dedicated scanners, allowlists and severity could supplement the simple heuristic. Do not invent cryptography or promise total accuracy.

## 92 Improving usage detection

Specialized Python/JavaScript/Php/Shell scanners with a GenericTokenScanner fallback could reduce observed errors. AST investment should target languages where accuracy gains justify complexity.

## 93 Proposed behavior tests

Prioritize assignment/export, quoted multiline/escapes, duplicates/comments/empty files; real-only/example-only/multiple-environment synchronization, production-only keys/defaults and no real-value propagation; strong access per language, weak/absent evidence, ignored files/docs and external exclusions; secret placeholders/allowlists and output; pre-change backups, non-mutating dry-run/audit-only, whole multiline removal and idempotence; invalid flag combinations and strict exits.

## 94 Safety-critical test properties

Real values never enter examples; review modes preserve bytes; weak/excluded keys survive; possible secrets block propagation; backups precede mutation; multiline cleanup leaves no fragments; exclusions do not fabricate evidence. Test that synchronization blocking does not silently imply all writes are blocked.

## 95 Property-based tests

Generate broader file combinations to test no real-value propagation, equal key sets after successful synchronization and stable second runs. These would strengthen guarantees but are proposed, not checked-in results.

## 96 Performance evidence

Measure file count, text bytes, key count, discovery/analysis time and peak memory. Reading once per project scan is an architectural optimization, not a measured throughput claim.

## 97 Incremental cache

A future `path + hash/mtime → references` cache could skip unchanged files, at the cost of invalidation and stored state. Add it only after proving full scans are a bottleneck.

## 98 Large monorepos

Project filters, incremental execution, caches, parallelism, subtree policy, file-size limits, JSON and changed-project selection are possible improvements. Recursive discovery does not establish benchmarked performance at giant-repository scale.

## 99 Symlink policy

Define whether to follow links, avoid loops, permit targets outside the root and back up linked files. Current default traversal does not follow directory symlinks, but file links can be read/written and resolved root does not enforce containment.

## 100 One more week

Prioritize filesystem behavior, idempotence, write-failure tests, temporary-file/rename writes, locking, JSON reports and realistic performance measurements before plugins or parallelism.

## 101 Infrastructure to avoid without a need

Docker, databases, Redis and distributed services do not currently solve the local filesystem responsibility. A small, self-contained CLI is proportional to this problem.

## 102 Why not a microservice

A remote API adds identity, uploads/workspace access, filesystem authorization, isolation, concurrency, storage, secret security and deployment. Central repository auditing would be another product with different requirements.

## 103 Evaluating architecture

Assess clarity of the problem/responsibilities, safe value handling, reviewable mutations, acknowledged uncertainty/limits, convergence, testability, defensible mechanisms and evolvability. Technology count is not quality.

## 104 About sixty seconds

ENV Auditor is a Python CLI keeping environment-file keys consistent. Each directory is an environment set and the example is its contract. Real files contribute empty keys; safe example defaults can fill missing real assignments. It scans consumers for strong, weak or absent evidence, retaining uncertainty and explicit external keys while default mode cleans up no-evidence settings. Dry-run, audit-only, backups, duplicate/secret checks and strict exits support review and automation. Its central trade-off is automating configuration with incomplete runtime knowledge.

## 105 About thirty seconds

It audits and synchronizes `.env` keys without transferring real values between environments. Strong and weak evidence distinguish recognized use from uncertainty; external exclusions protect invisible consumers. Review modes, backups and example heuristics reduce the risks of automatic cleanup.

## 106 Decision matrix

| Decision | Benefit | Cost or limitation |
| --- | --- | --- |
| Python standard library | Simple distribution/setup | Own parser maintenance |
| Example contract and key union | Reduced drift/full key inventory | Environment-exclusive keys propagate |
| Empty real-to-example assignments | Values remain isolated | Asymmetric logic |
| Full example blocks | Preserve safe defaults | Depends on example safety |
| Regex and weak evidence | Multiple languages/conservative retention | No semantic certainty; stale keys can survive |
| Automatic cleanup/exclusions | Maintenance with external knowledge | Incomplete runtime view/manual policy |
| Secret heuristic | Common mistake detection | Not complete scanning |
| Backups/direct writes | Recovery/simple implementation | Sensitive copies/no global transaction |
| Virtual dry-run/audit-only | Preview/current-state inspection | Projection logic/no automatic correction in audit-only |
| Strict exits | Automation signal | Policy criteria and post-processing evaluation |
| Sequential whole-file scans | Simple behavior | Large-file memory/large-workspace latency |
| Local CLI/no distributed services | Natural filesystem access | No central service or multi-machine coordination |

## 107 Claims to avoid

Prefer “no detected evidence” to “definitely unused”; “possible-secret heuristic” to “no secrets”; “explicit patterns with conservative fallback” to “all languages understood”; “external exclusions” to “absent from code means removable”; “sensitive recovery copies” to “backups make everything safe”; “individual writes” to “atomic changes”; “supported dotenv subset” to “universal parser”; “known limits” to “production-ready”; “bytes and extractors per scan” to unqualified `O(files)`; and “functional responsibility separation” to formal Clean Architecture.

## 108 Hard follow-up questions

Automatic cleanup is risky: explain weak/external retention, backups and review modes, and recommend dry-run with evidence first. Confirmation prompts could suit interactive use but complicate CI; no current interactive approval mechanism exists. Real-to-example safety comes from explicitly generating `KEY=` and merits regression/property tests. Production-only external consumption needs `ignore_unused_keys`. Automatic analysis and automatic production configuration mutation are different policies; critical autofix requires permissions, atomicity, rollback, locks, auditability, backups, review and deployment ownership.

## 109 Reasoning checklist

Problem → information available/unavailable → decision → guarantee/non-guarantee → false positives/negatives → mitigation → remaining limit → stronger requirements. Ask whether values can leak, required configuration can be removed, a write can be recovered, and a heuristic is being mistaken for certainty.

## 110 Interview principle

Demonstrate understanding rather than perfection: explain keys versus values, the example contract, incomplete evidence, conservative retention, non-transactional sensitive backups, parser/regex/secret limits and requirements-driven alternatives. Adapt first-person answers to what you actually understand and can demonstrate. A defensible small design is more useful than invented guarantees or complexity for appearance.

## Literal examples from the study notes

The following literal snippets retain commands, configuration, identifiers, pseudocode and placeholder values. Labels/comments inside snippets remain as originally written; explanation is in the English topics above.

```text
.env
.env.local
.env.test
.env.prod
.env.example
```

```text
descobrir
→ comparar
→ sincronizar
→ analisar uso
→ preservar o que pode estar em uso
→ remover configuração sem evidência
→ validar o estado final
```

```text
.env.example
```

```text
.env
.env.local
.env.prod
.env.test
.env.staging
...
```

```text
KEY=valor-real
```

```text
KEY=
```

```text
Descobrir projetos
        ↓
Descobrir .env / .env.*
        ↓
Localizar .env.example
        ↓
Carregar configuração opcional
        ↓
Sincronizar estrutura dos arquivos
        ↓
Detectar possíveis secrets no .env.example
        ↓
Construir conjunto conhecido de variáveis
        ↓
Descobrir arquivos de runtime/configuração
        ↓
Analisar referências
        ↓
Classificar strong / weak / unused
        ↓
Preservar strong
        ↓
Preservar weak
        ↓
Preservar ignore_unused_keys
        ↓
Remover variáveis sem evidência
        ↓
Recarregar arquivos alterados
        ↓
Validar paridade final
```

```text
python3 scripts/audit-envs.py
```

```text
.env
.env.*
```

```text
.env.example
```

```text
workspace/
├── api/
│   ├── .env
│   └── .env.example
└── worker/
    ├── .env.prod
    └── .env.example
```

```text
.env
.env.qualquer-coisa
```

```text
.env.example
.env*.bak.*
```

```text
keys(.env.example)
=
keys(.env)
=
keys(.env.prod)
=
keys(.env.test)
...
```

```text
PROD_ONLY=
```

```text
.env.prod
DATABASE_PASSWORD=senha-real
```

```text
DATABASE_PASSWORD=
```

```text
DATABASE_PASSWORD=senha-real
```

```text
APP_ENV=local
CACHE_DRIVER=file
PORT=8080
```

```text
.env
A=1
B=2

.env.prod
A=10
C=30
```

```text
A=
B=
C=
```

```text
KEY=value
export KEY=value
```

```text
[A-Za-z_][A-Za-z0-9_]*
```

```text
PRIVATE_KEY="linha 1
linha 2
linha 3"
```

```text
PORT=8000
DATABASE_URL=...
PORT=9000
```

```text
SECRET
PASSWORD
PASS
TOKEN
PRIVATE
CREDENTIAL
CLIENT_SECRET
APP_KEY
API_KEY
```

```text
change
changeme
placeholder
example
dummy
fake
your_...
xxx
<value>
null
true
false
0
1
```

```text
{
  "public_non_secret_keys": [
    "PUBLIC_CLIENT_KEY"
  ]
}
```

```text
strong
weak
unused
```

```text
env('DB_HOST')
```

```text
${DB_HOST}
$DB_HOST
```

```text
process.env.DB_HOST
process.env["DB_HOST"]
```

```text
import.meta.env.VITE_API_URL
```

```text
os.getenv("DB_HOST")
os.environ["DB_HOST"]
```

```text
System.getenv("DB_HOST")
```

```text
SOME_FEATURE_FLAG
```

```text
"talvez esteja morta, então apagar"
```

```text
"existe algum sinal de uso, então preservar"
```

```text
SERVICE_PORT
```

```text
{
  "ignore_unused_keys": [
    "SERVER_INJECTED_VARIABLE"
  ]
}
```

```text
.env
.env.*
.env.example
.env-audit.json
```

```text
para cada variável:
    para cada arquivo:
        ler arquivo
        procurar variável
```

```text
files → read once → extract references → intersect known keys
```

```text
volume total de texto analisado
× quantidade de extractors aplicáveis
```

```text
.env
.env.*
.env.example
```

```text
.env existe
.env.example não existe
```

```text
estado físico atual
```

```text
estado projetado após execução
```

```text
audit-only
= observar o presente
```

```text
dry-run
= simular alterações futuras
```

```text
--audit-only --dry-run
```

```text
.env-audit-backups/
```

```text
0700
```

```text
0600
```

```text
backup ≠ sanitização
backup ≠ secret management
backup ≠ encryption
```

```text
--no-backup
```

```text
python3 scripts/audit-envs.py --strict
```

```text
--strict --strict-unused
```

```text
DB_HOST está em uso
```

```text
STRONG_USAGE DB_HOST:
    config/database.php
    docker-compose.yml
```

```text
{
  "public_non_secret_keys": [],
  "ignore_unused_keys": [],
  "ignore_projects": [],
  "ignore_files": []
}
```

```text
.git
node_modules
vendor
__pycache__
public/build
bootstrap/cache
```

```text
errors="ignore"
```

```text
errors="replace"
```

```text
POSSIBLE_SECRET_IN_EXAMPLE:
    - DATABASE_PASSWORD
```

```text
se a fonte considerada segura parece não ser segura,
não propagar automaticamente.
```

```text
target
kind
keys
```

```text
CREATE_EXAMPLE_FROM_ENVS
ADD_KEYS_TO_EXAMPLE
CREATE_ENV_FROM_EXAMPLE
ADD_KEYS_TO_ENV
```

```text
decidir a mudança
```

```text
executar fisicamente a mudança
```

```text
configuração
filesystem
parsing
discovery
usage detection
secrets
output
backup/write
synchronization
audit
CLI
```

```text
parse_env(path)
is_ignored(path)
analyze_usage(keys, files)
suspicious_example_keys(example, config)
```

```text
EnvEntry
EnvFile
AuditConfig
UsageEvidence
SyncAction
```

```text
STRONG_USAGE_EXTRACTORS
```

```text
process.env.OLD_VARIABLE
```

```text
name = build_variable_name()
os.environ[name]
```

```text
DATABASE_URL
REDIS_HOST
FEATURE_FLAG_X
```

```text
strong → preservar
weak   → preservar
explicit ignore → preservar
zero evidence → candidato à remoção
```

```text
mesmas keys em todos os ambientes
```

```text
benefício:
consistência e previsibilidade

custo:
menor flexibilidade para configurações deliberadamente exclusivas
```

```text
Completed with 1 project still requiring review
```

```text
exit code 1
```

```text
python3 scripts/audit-envs.py --audit-only --show-usage
```

```text
nenhuma referência encontrada
```

```text
a variável definitivamente não é necessária
```

```text
strong
weak
no evidence
```

```text
declaração de variável ≠ uso da variável

ausência de referência ≠ prova de não uso

backup ≠ transação

backup ≠ proteção de secret

regex match ≠ compreensão semântica

placeholder detection ≠ secret scanning completo

dry-run ≠ audit-only

mesmas chaves ≠ mesmos valores

.env.example ≠ lugar para credenciais reais

weak evidence ≠ strong evidence
```

```text
{
  "PORT": {
    "type": "integer",
    "required": true
  },
  "APP_ENV": {
    "type": "enum",
    "values": ["local", "test", "production"]
  }
}
```

```text
paridade de keys
```

```text
validade semântica do valor
```

```text
UsageScanner
├── PythonScanner
├── JavaScriptScanner
├── PhpScanner
├── ShellScanner
└── GenericTokenScanner
```

```text
path + hash/mtime
→ referências encontradas
```

```text
python3 scripts/audit-envs.py --dry-run --show-usage
```

```text
KEY=
```

```text
Qual problema estou tentando resolver?
            ↓
Qual informação o script realmente possui?
            ↓
Qual informação ele NÃO possui?
            ↓
Qual decisão foi tomada?
            ↓
Qual garantia essa decisão oferece?
            ↓
Qual garantia ela não oferece?
            ↓
Quais falsos positivos ou negativos podem existir?
            ↓
Como o projeto reduz esse risco?
            ↓
Qual limitação continua existindo?
            ↓
O que eu mudaria se o requisito fosse mais rigoroso?
```

```text
Posso estar expondo algum valor?
Posso remover algo necessário?
Posso alterar um arquivo sem conseguir recuperar?
Estou confundindo heurística com certeza?
```
