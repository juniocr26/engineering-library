# VivaBem documentation review — 2026-10-26

[English](vivabem-documentation-review.md) | [Português brasileiro](../../pt-br/operations/vivabem-documentation-review.md)

## Initial mapping

All source trees and the historical library were initially clean. The destination was clean at `d641b17e5285407c2f717d3bb5555993d56bcbd2`. No authorized collection existed. New stable IDs use the exact source slugs; display names follow recorded project headings where available.

| Source | Old-library material | Destination / new ID | Planned work | Gaps |
| --- | --- | --- | --- | --- |
| `acesso-servidor/` | `docs/<lang>/architecture/acesso-servidor.md`; `docs/<lang>/interviews/acesso-servidor-interview.md` | `docs/acesso-servidor/`; `acesso-servidor` | Bilingual current-state synthesis, contracts, configuration, security, guides, FAQ and provenance | Runtime acceptance; see project review |
| `carteira-digital/` | `docs/<lang>/architecture/carteira-digital.md`; `docs/<lang>/interviews/carteira-digital-interview.md` | `docs/carteira-digital/`; `carteira-digital` | Bilingual current-state synthesis, contracts, configuration, security, guides, FAQ and provenance | Runtime acceptance; see project review |
| `cofre-paciente/` | `docs/<lang>/architecture/cofre-paciente.md`; `docs/<lang>/interviews/cofre-paciente-interview.md` | `docs/cofre-paciente/`; `cofre-paciente` | Bilingual current-state synthesis, contracts, configuration, security, guides, FAQ and provenance | Runtime acceptance; see project review |
| `criptografia-lib/` | `docs/<lang>/architecture/criptografia-lib.md`; `docs/<lang>/interviews/criptografia-lib-interview.md` | `docs/criptografia-lib/`; `criptografia-lib` | Bilingual current-state synthesis, contracts, configuration, security, guides, FAQ and provenance | Runtime acceptance; see project review |
| `hub-vivabem/` | `docs/<lang>/architecture/hub-vivabem.md`; `docs/<lang>/interviews/hub-vivabem-interview.md` | `docs/hub-vivabem/`; `hub-vivabem` | Bilingual current-state synthesis, contracts, configuration, security, guides, FAQ and provenance | Runtime acceptance; see project review |
| `script-auditoria-envs/` | `docs/<lang>/architecture/script-auditoria-envs.md`; `docs/<lang>/interviews/script-auditoria-envs-interview.md` | `docs/script-auditoria-envs/`; `script-auditoria-envs` | Bilingual current-state synthesis, contracts, configuration, security, guides, FAQ and provenance | Runtime acceptance; see project review |
| `vivabem/` | `docs/<lang>/architecture/vivabem.md`; `docs/<lang>/interviews/vivabem-interview.md` | `docs/vivabem/`; `vivabem` | Bilingual current-state synthesis, contracts, configuration, security, guides, FAQ and provenance | Runtime acceptance; see project review |
| `vivabem-android/` | `docs/<lang>/architecture/vivabem-android.md`; `docs/<lang>/interviews/vivabem-android-interview.md` | `docs/vivabem-android/`; `vivabem-android` | Bilingual current-state synthesis, contracts, configuration, security, guides, FAQ and provenance | Runtime acceptance; see project review |

## Source revisions

| Repository | HEAD |
| --- | --- |
| `engineering-library_old` | `dfb5b7a5b8a9159af65a991872c34e78d8fd6fd0` |
| `acesso-servidor` | `ba70952fd63992c85aa153f141a39fadf33360a0` |
| `carteira-digital` | `9a6b795b6ebc16f0390e0fbdbf711f257e42fa2a` |
| `cofre-paciente` | `85edbcb16fd029235dc74eba12c7b14b164d3d62` |
| `criptografia-lib` | `c95a12038760a663f69bb576f7c172e8b021bece` |
| `hub-vivabem` | `e0ab75952946bc3f764dcb4144e404097277933f` |
| `script-auditoria-envs` | `2e5d5de71d1323b4e588e04f06784324802ae0d3` |
| `vivabem` | `f0b884ca536a26996d40bf4187981d8c7506d0d7` |
| `vivabem-android` | `07c3fa6cfcb8cd19cc6d271922684b304778ccd5` |

## Delivery and actual investigation

Eight new collections contain 310 Markdown files: 38 per project plus six focused bilingual additions including README/bio pairs and navigation. The substantive pages cover purpose/architecture/data, implemented interfaces, inspected configuration, integration boundaries, security, safe investigation, five FAQ answers, inspected test assertions and historical reconciliation. Category indexes are navigation only. The existing six collections were preserved. No empty category, source snapshot or PDF was created.

Current source inspection was selective, concentrated on financial retirement/balance reading, the Cofre request policy and partial reads, authenticated envelope construction, Hub publication/subscriptions, Portal dashboard/authentication/audit, updater cleanup/Compose selection and Android launch/signing. This is not a full application or security audit. Per-project `operations/source-review.md` and catalog metadata identify paths/revisions and actual coverage. The historical architecture maps and selected interview explanations were synthesized, not blindly restored; full original records remain intact in the read-only old library. The manifest records their hashes. Historical execution counts were not reused as current results.

## Reconciled differences

- Wallet financial execution/Stripe/Connect/outbox narratives are retired. The dedicated balance read and generic unavailable adapter are distinct; supported signed Mercado Pago webhooks still return 503 without durable acceptance.
- Cofre has nine operation/body-bound POST routes; historical bank routes are absent. Exact replay remains possible. Unreadable stored cards remain explicit partial results.
- Current crypto authenticates header, IV and ciphertext; the old unmarked format is rejected. Exact PEM bytes remain part of derivation compatibility.
- Hub publication and recipient authorization are separate. Liveness/readiness and AMQP/domain success are different observations; POST /events is not supported.
- Updater validation flags delete dependencies/audit proposals and are not safe read-only checks. Current Compose selection replaces generated-overlay descriptions.
- CLI selected-directory support does not imply Portal use: the inspected AuditExecutor invokes global --apply-audit and can create a proposal even on list. No code was changed to resolve that difference.
- Android TWA session, DAL, notification permission and push delivery are distinct. Current Portal policy has rolling 60-day inactivity; passive heartbeat is not qualifying use.

## Destination contracts and discrepancies

The actual catalog reads project-local bilingual trees and matching bio IDs/names. Category discovery and frontend canonical ordering were inspected in Catalog::Files/Sync and documentation.ts. Relative collection links are used. Source file references remain code spans for an authorized checkout only: no source expansion in the reader is claimed. Optional icons use the existing reader fallback; none was required for metadata compatibility.

The inherited central index described a public catalog and provenance retains historical public-portfolio origins. The user identifies this checkout as the private destination; its observed origin is the organization repository, not the personal portfolio remote recorded historically. A remote URL and MIT license do not prove remote visibility. The central index now explicitly separates private ecosystem material. No visibility/remotes were changed, no remote service was queried and nothing was published. Existing historical portfolio provenance was retained rather than rewritten as private-source evidence.

The unbounded check_catalog.py requires all sibling repositories to equal its manifest and hashes their imports. That behavior exceeds this task's scope and was not run or changed. New manifest entries describe authored syntheses with empty imports and separately recorded historical sources. No database synchronization/ingestion ran; live catalog activation is unverified.

## Verification and failures

`python3 -B -m unittest discover -s tools -p 'test_*.py' -v`: 27 tests passed. These are existing documentation-tool fixture tests, not application tests. Host Python was used as the established standard-library validator exception; no runtime was installed.

The first bounded validation mistakenly treated the language index file as a category directory and reported 32 false category findings. Category traversal was corrected to inspect directories only and checked again; this was an ad hoc checker issue, not a documentation defect. The first collection-generation attempt also stopped before writing a collection because its parent directory had not been created; generation was corrected. Neither failure changed source repositories.

Docker inspection initially lacked socket permission; the approved read-only query then succeeded and found no running services. No containers/services were started. Therefore no browser/renderer or Rails/Node execution is claimed. The supplied manual's recorded tests/PDF work remain historical and were not imported as current execution.

Final bounded structural/link/parity/secret-pattern results and the changed-file inventory are recorded in [the validation artifact](validation/vivabem-documentation-2026-10-26.json). Git whitespace and final scope/status checks are recorded there. Pattern scans do not certify absence of all sensitive content. English and Portuguese were authored as paired technical syntheses with matching canonical section/question IDs; this is not independent translation certification.

## Remaining evidence and work

Every project retains explicit runtime/restore/production gaps in its review. Configuration references cover inspected consumers, not every framework and deployment input. Portal appointment/conference state machines, complete ratings lifecycle, queue handoff/recovery, full configuration inventory and detailed operational runbook reconciliation need deeper source review before this can be described as exhaustive documentation of the ecosystem. No missing feature was implemented. This delivery establishes the eight grounded bilingual collections but does not claim that exhaustive coverage is finished.

No effective environment/configuration, application behavior, database/schema, infrastructure, accounts or identities changed. Source repositories and engineering-library_old remained read-only and were checked for a clean final Git state. Existing destination changes were initially absent. Only destination documentation/provenance changed. No staging, commit, amend, rebase, push or publication occurred.

Focused additions cover Cofre confirmation/ACK and rating summary/marker windows, plus Portal appointment retirement and the Jitsi reference behind historical GoogleMeet naming. Source paths were added to project provenance.

Initial literal parity also flagged different-language historical paths; verification was repeated normalizing only the documentary language segment. All 14 current catalog bio IDs are unique. H1 titles put the subject before the em dash so the reader suffix filter retains distinct chapter titles.

## Language-directory portability — 2026-11-04

The Git index of the eight VivaBem source repositories records docs/pt-BR, while enumeration on this macOS filesystem shows docs/pt-br. Existing validators use pt-br; the central collection also uses that form. Existence checks on this volume do not establish resolution on a case-sensitive filesystem. No directory rename, Git-index write or validator change was performed in this documentation review. Tracked normalization and Linux-checkout validation remain pending; preserve slugs and bilingual content when addressing the discrepancy.
