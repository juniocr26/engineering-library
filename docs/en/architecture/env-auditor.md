# env-auditor: implementation dossier

[English](env-auditor.md) | [Português brasileiro](../../pt-BR/architecture/env-auditor.md)

Static review: 2026-10-10. This independent portfolio project has no verified runtime calls to another portfolio repository. Evidence links support the complete explanations below.

## Execution, representation and decisions

The implemented product is a local, standard-library Python CLI that aligns literal environment-file key membership with authoritative examples. It is neither a service nor a source-code usage analyzer. `main` parses arguments, `resolve_root` fixes scope, `discover` groups files by directory, `parse` builds a `Document`, `plan` computes bytes, and `run` presents or writes each pair. The default root is two parents above the resolved script; explicit relative roots use the caller's directory. No cross-project API is involved: scanning sibling directories is a filesystem capability, not an application integration.

`Document.raw` retains original bytes and `blocks` is an ordered list of `(key or None, literal text)`. A block can span quoted lines; comments have no key. Sets support membership comparison and `Counter` rejects duplicate example keys. Existing duplicate target keys survive if allowed. Planning preserves allowed blocks, collects removed blocks and appends missing reference assignments. A new target copies the whole validated reference, including comments. An empty reference removes all assignments from an existing target while leaving comments. This is deliberate structural behavior, not proof the application can run afterward.

Discovery uses sorted `os.scandir` recursion and exact exclusions, independent of Git. Specific variant examples win over same-directory base examples. Unreferenced targets are skipped, and base examples do not invent arbitrary variants. Filesystem discovery finds ignored configuration but can traverse unexcluded storage; scanning and sorting cost grows with entries, while parsing and planning grow with input bytes and blocks. `key in added` currently uses a list, so many missing keys can make appending comparisons quadratic. This is a static complexity observation, not a measured bottleneck. A set alongside the ordered list is a possible optimization.

Planning separately from mutation makes preview faithful to the transformation and keeps it testable. A formatting-aware dotenv library could broaden grammar; typed schemas could validate values; explicit include roots could limit traversal. These are hypothetical alternatives. None would justify silently sourcing arbitrary input. The current parser does not execute or interpolate values, but accepts only its documented literal grammar.

## Filesystem safety and plaintext recovery

Inputs must be regular files; discovery skips symlinks and processing checks file status again. Parsing rejects invalid UTF-8, NUL bytes, malformed assignments and unterminated quotations. These checks reduce accidental traversal and malformed transformations; there is no file locking or race-free descriptor-based traversal. A path can change between checking and using it. Do not describe this as an adversarial filesystem sandbox.

Values are omitted from terminal output, but paths and key names remain visible. Reference values are trusted literals: the program does not detect secrets. Backups contain exact original bytes and removed blocks in plaintext. Session directories use 0700, files use 0600, and the backup-root ignore file contains `*`. This reduces ordinary access and accidental Git inclusion, but does not encrypt backups, protect against the same user or define retention. Existing target permission bits are preserved; ownership, ACLs and extended attributes are not.

A changed existing target is backed up before replacement. The same-directory temporary file is flushed and fsynced, chmodded and replaced using `os.replace`. This gives individual-file replacement, not a multi-file transaction. The directory is not fsynced, and concurrent writers can be overwritten. Stronger durability would require a directory-sync design; writer coordination would require locking and change detection. Both are hypothetical changes. No real environment or backup was inspected during this documentation review.

## Operation, failures and evidence limits

Use the CLI contract in the README before applying synchronization. `--dry-run` and `--audit-only` are mutually exclusive aliases for the same read-only plan. They do not create targets or backups. A proposed difference alone exits 0; handled discovery/pair errors yield 1, invalid root/CLI input yields 2. Skipped links or missing references alone are not errors. Preview cannot establish future permission or backup success.

The write path is opt-in by invoking the normal command, not a background daemon. Errors are handled per pair, allowing other pairs to proceed; successful earlier writes are not rolled back. If a backup fails, replacement does not begin. If replacement fails, backups or partial temporary artifacts may remain. An operator should inspect the identifier-only report, locate the exact backup session and deliberately restore the intended original after checking concurrent edits. Automatic bulk rollback, retention and crash recovery are absent. Output failures and pathological recursion can escape the usual error mapping.

The existing `unittest` suite uses isolated temporary fixtures for parsing, variants, preview, backups, replacement failures, permissions and idempotence. Existing verification records are historical evidence, not executions in this review. No runtime or application tests were run here. Installation consists of distributing the script with Python 3.10+; relocating it changes its default root. There is no service deployment, database, Docker topology, payment flow or network API to document. A library comparison may discuss these concerns conceptually without implying that the other portfolio applications call the CLI.

Remaining evidence gaps: crash/power-loss durability, concurrent writers and filesystem races, ACL/ownership portability, very deep trees, backup retention and scale measurements. Resolve these with separately authorized implementation and isolated experiments; no throughput or complete shell-parser compatibility is claimed.

## Supporting evidence

- [architecture/implementation-review](../../../../env-auditor/docs/en/architecture/implementation-review.md)
- [security/filesystem-boundaries](../../../../env-auditor/docs/en/security/filesystem-boundaries.md)
- [operations/recovery-and-evidence](../../../../env-auditor/docs/en/operations/recovery-and-evidence.md)
- [Interview / Entrevista](../interviews/env-auditor.md)
