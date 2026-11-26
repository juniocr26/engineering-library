# Declared data structures and verification limits

2026-11-04. Current source inventory without a database connection. Migrations describe intended structure, not the installed schema. No migration, query, cleanup or schema change was executed.

## Current models

| Model | Declared connection / mapping |
| --- | --- |
| `app/Models/Atendimento.php` | table=atendimentos |
| `app/Models/Paciente.php` | table=pacientes |
| `app/Models/Psicologo.php` | table=psicologos |
| `app/Models/RegistroFcm.php` | table=registros_fcm |
| `app/Models/SolicitacaoExclusaoConta.php` | table=solicitacoes_exclusao_conta |
| `app/Models/TempoAtendimento.php` | table=tempo_atendimentos |
| `app/Models/Usuario.php` | table=usuarios |

## Present migrations

| File | Tables in create/table |
| --- | --- |
| `database/migrations/0001_01_01_000000_create_usuario_table.php` | `usuarios` |
| `database/migrations/0001_01_01_000001_create_cache_table.php` | `cache` |
| `database/migrations/0001_01_01_000002_create_jobs_table.php` | `jobs` |
| `database/migrations/0001_01_01_000010_create_password_reset_tokens_table.php` | `password_reset_tokens` |
| `database/migrations/0001_01_01_000011_create_sessions_table.php` | `sessions` |
| `database/migrations/0001_01_01_000012_create_cache_locks_table.php` | `cache_locks` |
| `database/migrations/0001_01_01_000013_create_job_batches_table.php` | `job_batches` |
| `database/migrations/0001_01_01_000014_create_failed_jobs_table.php` | `failed_jobs` |
| `database/migrations/2025_10_03_063440_create_personal_access_tokens_table.php` | `personal_access_tokens` |
| `database/migrations/2025_10_03_215955_psicologos.php` | `psicologos` |
| `database/migrations/2025_10_05_154602_pacientes.php` | `pacientes` |
| `database/migrations/2026_05_19_000000_create_atendimentos.php` | `atendimentos` |
| `database/migrations/2026_05_19_000001_create_tempo_atendimentos_table.php` | `tempo_atendimentos` |
| `database/migrations/2026_07_22_000003_create_solicitacoes_exclusao_conta_table.php` | `solicitacoes_exclusao_conta` |
| `database/migrations/2026_07_22_000004_criar_registros_fcm.php` | `registros_fcm` |

[Implementation / Implementação](../architecture/overview.md). Historical results remain in dated operations reports; textual references to removed columns are not evidence of current use.

<!-- reading-section: current-storage -->
## Current appointment storage contract — 2026-11-10

Audience: backend and database maintainers. A: source inspection of `Atendimento`, `Usuario`, `TempoAtendimento` and their appointment/participation create migrations at `d412cc7`; this is not a query against a running database. The inventory above is retained, while the following explains the checked constraints.

`atendimentos` uses string UUID primary identity and decimal(10,2) amounts. The professional reference is nullable with null-on-delete, the buyer references usuarios with cascade, and an interrupted appointment reference uses null-on-delete. Indexes cover user/status/start, professional/status/start and status/end. These declarations support the read/state model without constituting a measured query improvement. There is no foreign key from the Portal transaction reference to Wallet's database.

`tempo_atendimentos` uses the appointment as primary identity, participant references, unsigned integer participation counters and consultation duration. The appointment and participant foreign keys cascade on deletion. Model casts preserve integers, while appointment values use decimal:2 casts; `Atendimento::toDTO` still converts valor to float. Do not describe uniform fixed-point arithmetic throughout the Portal merely because storage is decimal or one purchase boundary uses cents.

Model update hooks register cache/notification effects and some operations after SQL commit. A successful SQL commit does not guarantee Redis invalidation, Hub delivery, remote link persistence or financial completion. `salvarRecuperacaoFinanceira` distinguishes an internal recovery save when invalidation fails; it is not a cross-service transaction or a public retry command. Usuario hides credentials and Pix key from model serialization, which does not eliminate their storage/access sensitivity.

Create migrations define a fresh schema; their presence does not authorize resetting or replaying them over an existing installation. Preserve SQL, uploaded assets, cryptographic custody and dedicated operator audit/control state according to their separate ownership. Backup/restore and deletion cascades were not exercised. Recheck both languages and the curated collection after schema/model/hook changes. [Current architecture](../architecture/overview.md) and [current tests](../operations/backend-testing.md) delimit implemented behavior and actual verification.

- [Query Plan and safe diagnostics](query-plan.md)
