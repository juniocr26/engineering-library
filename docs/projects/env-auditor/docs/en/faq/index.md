# env-auditor — Technical FAQ

[Project index](../index.md) · [Português brasileiro](../../pt-BR/faq/index.md)

Technical questions, detailed answers and follow-ups are available directly on this page. Historical milestone statements retain their dates; current corrections below take precedence. First-person examples describe portfolio artifacts, not employment experience. The [study guide](study-guide.md) retains its existing URLs and anchors for compatibility.

## Current source review — 2026-10-19

The answers below were checked against selected current source and test definitions. No sibling application tests or services were executed. See the [scope and evidence record](../operations/documentation-audit-2026-10-19.md).

### Q006 — Can a zero-change preview guarantee a no-op when the normal command runs later?

**Answer:** No. Preview and mutation share `plan`, so unchanged inputs produce the same transformation. They are separate scans and reads, with no lock, snapshot or content recheck binding the later write to the earlier preview. A changed example can change the key contract; another writer can alter a target between read and replace. Review scope and reference files again before applying, and compare exact backup originals before manual recovery. A zero exit code in preview means no handled discovery/pair error; it does not mean no proposed differences or valid runtime values. The existing isolated tests compare fixture bytes and directory entries before/after both preview aliases; those assertions concern that invocation, not future executions.


## ENV Auditor technical interview study guide


[English](index.md) | [Português brasileiro](../../pt-BR/faq/index.md)

Study material grounded in the current [CLI contract](../../../README.md), [implementation](../../../../../../../env-auditor/scripts/audit-envs.py) and [tests](../../../../../../../env-auditor/tests/test_audit_envs.py). First-person answers describe the portfolio implementation, not professional experience. Rationale below is architectural interpretation unless separately recorded; alternatives are learning comparisons, not claims of historical evaluation. Static review: 2026-10-09; no auditor commands or tests were executed during this review.

## 1 Overview

**Question: Explain the project.**

**Model answer:** “This is a local Python CLI that synchronizes literal environment assignments against same-directory examples. It recursively discovers files, selects a reference per target, preserves existing values for allowed keys, adds missing reference assignments and removes keys absent from that reference. Existing changed targets receive backups before atomic replacement. Two preview flags calculate the same plan without writes.”

It solves structural drift, not runtime configuration validation. It does not inspect application source, detect secrets, generate examples from runtime files, expand values or prove that a removed key is unused.

**Follow-up:** Can a key used in code still be removed? Yes: membership in the selected example is the only removal criterion. Review the reference contract before synchronization.

## 2 Architecture and execution flow

```text
main → resolve_root → run
  → discover (filesystem groups, errors, skipped links)
  → choose target/reference pairs
  → read_document / parse → plan
  → preview report OR backup → atomic_write
  → outcomes / totals / exit code
```

`Document` retains original bytes and ordered `(key, literal block)` entries. Non-assignment blocks retain blank lines/comments. This allows whole multiline assignments to survive or disappear together. `plan` separates transformation from filesystem mutation, so preview uses the same planned bytes. `run` processes pairs independently and continues after handled errors. It is a small functional CLI, not a framework or service.

**Question: Why standard-library Python?**

**Model answer:** “The implementation uses filesystem, regex, argument parsing and temporary-file APIs without external dependencies. That keeps distribution small, at the cost of maintaining a deliberately limited assignment parser.”

A dotenv library could offer broader syntax, but a value-loading API might discard the formatting needed here. A typed schema could validate values, at the cost of a separate responsibility and migration path. Neither alternative is implemented.

## 3 Scan root and filesystem discovery

**Question: Why derive the default root from the script?**

**Model answer:** “`Path(__file__).resolve().parents[2]` selects the shared portfolio root for the current `env-auditor/scripts/audit-envs.py` layout. The caller can run the script from the portfolio, repository or scripts directory without changing its default scope. An explicit relative root intentionally resolves from the caller's directory.”

The dependency on installation layout is a cost: moving the script changes the default. A required root argument would make scope explicit but lose the workspace convenience. The script does not search ancestor directories for repository markers. Root symlinks are resolved; child symlinks are skipped.

**Question: Why discover through the filesystem instead of Git?**

**Model answer:** “Runtime configuration is commonly ignored by Git. `os.scandir` recursively finds sibling, nested, hidden and ignored files without requiring a repository or querying Git. Exact directory exclusions constrain traversal; this is directory grouping, not repository-boundary discovery.”

The [README](../../../README.md#discovery-and-synchronization) lists all exclusions. Names match `.env` or `.env.*`, excluding names containing `.bak` or ending in `~`. Any discovered symlink is reported/skipped, including non-environment links. `.cargo-cache` and `.dockerized-*` are not in the exclusion set: ignored storage can still be traversed. Git-ignore rules are intentionally irrelevant; add explicit exclusions only in a separate code task if that scan scope is undesirable.

**Follow-up:** Does hidden mean excluded? No. Exclusions are exact names and the two path suffixes `bootstrap/cache` and `public/build`.

## 4 Target/reference matching

**Question: How do variants work?**

**Model answer:** “`.env.prod` prefers `.env.prod.example`; otherwise it uses `.env.example` in the same directory. A reference creates its missing corresponding target. The base reference creates `.env`, but does not invent `.env.test` or other variants. Without a reference, an existing target is reported skipped and left unchanged.”

Every eligible name ending in `.example` is a reference, never a target. A nested suffix such as `.env.odd.example.example` does not generate `.env.odd.example`. There is no cross-directory fallback or key union across environments.

Example: if `.env.example` contains `A=default` and `.env.local` contains `A=` plus `OLD=local`, the local empty A remains and OLD is removed. A specific production example containing only PROD removes A from the production target regardless of source usage.

**Trade-off:** Per-variant examples express distinct contracts but can drift independently. A single base example reduces reference maintenance but forces its key set on every variant without a specific example.

## 5 Literal preservation and deletion

**Question: What does synchronization guarantee?**

**Model answer:** “After successful synchronization, target key membership matches its selected validated example. Existing allowed assignment blocks remain literal, including empty values, duplicates and multiline text. Missing keys copy reference blocks. This does not make values equal or valid for the application.”

The result retains target comments/blank lines even when associated assignments disappear. Removed assignment blocks are backed up separately. New targets copy the entire validated example, including comments. Existing targets receive only missing assignment blocks, not all reference comments. Duplicate reference keys are rejected; retained duplicates in targets are preserved rather than normalized. An empty valid reference removes every active assignment from an existing target while retaining comments.

Parsing rejects invalid UTF-8, NULs, malformed assignments, unterminated quoted values and unexpected text after a closing quote. It accepts optional `export`, identifier keys and quoted multiline literals. It never sources, evaluates, interpolates or expands values. It is not a complete shell grammar, dotenv compatibility guarantee, secret detector or type checker.

**Follow-up:** Can a reference accidentally propagate a credential? Yes. References are authoritative literal data; no secret heuristic is present. Output omits values, but that does not make reference contents safe.

## 6 Preview and exit contract

**Question: How do dry-run and audit-only differ?**

**Model answer:** “They are aliases for the same no-write plan, mutually exclusive on the CLI. Both read and validate current inputs and report proposed creations, updates and removals. Neither creates targets, backup directories or other files through the auditor.”

A preview does not verify future write permissions or successful backup/replace operations. A proposed change alone is success: exit 0. Discovery or handled pair errors yield 1; invalid root and CLI arguments yield 2. Missing references and skipped links alone do not cause failure. Reports show the absolute root, paths, pairs, key names/counts, outcomes and totals. Paths and key names remain visible; this is not general diagnostic redaction.

Complete output now contains one Unicode bordered table per validated pair: `Variável | Situação | Ação prevista`. It shows all initial keys, sorted example-only, target-only, then shared, alphabetically inside each category. Target/reference paths identify pairs; project summaries group nested directories by the first relative path component (root pairs use `.`). Discovery itself still groups by directory.

The final summary omits shared keys and retains initial differences. Preview actions say `Proposta:`; successful writes say `Concluída:`. Failed pairs distinguish `Falhou:` from known actions marked `Não aplicada:`. Projects without findings print `Nenhuma pendência de sincronização.` Missing targets (even with empty examples), missing references and processing/discovery errors remain visible. `added`/`removed`/`shared` include successfully planned comparisons even if writing fails; `actual_created`/`actual_updated` count successful writes only. No-backup synchronization and low-use/no-reference source classifications remain unsupported. Example absence does not prove non-use. See [synthetic terminal examples](../operations/terminal-report.md).

Retired flags `--strict`, `--strict-unused`, `--show-usage`, `--no-backup` are rejected. `.env-audit.json` is ignored with a notice. Old study notes describing usage classification, secret heuristics, key union, strict policy and real-to-example propagation are superseded by this guide.

## 7 Backups, permissions and atomic replacement

**Question: What happens before a write?**

**Model answer:** “A changed existing target first gets an exact `.original` and a `.removed` file in a uniquely named UTC backup session under the scan root. Backup directories use 0700 and files 0600. Only then does a same-directory temporary file replace the target. Existing permission bits are retained; new targets use 0600.”

The temporary stream is flushed, chmodded and fsynced before `os.replace`. This is per-target replacement, not a transaction across the portfolio. New and unchanged targets do not create backups. A failure before replacement preserves that target; partial backups may remain. Other pairs continue. Backup contents remain sensitive plaintext; the local `*` gitignore and permissions are not encryption or access control beyond filesystem permissions.

**Follow-up:** Is it crash-durable or safe with concurrent writers? The parent directory is not fsynced, there is no lock or recheck against concurrent changes, and ownership/ACLs/xattrs/timestamps are not preserved. Static symlink rejection does not eliminate filesystem races between checks and reads/replacement.

## 8 Failure scenarios and available evidence

| Scenario | Implemented response / boundary |
| --- | --- |
| Invalid example or target | Handled pair error; unchanged target; continue; final 1 |
| No matching example | Skip unchanged; not an error |
| Backup failure | No target replacement; partial backups can remain |
| Replace failure | Original target remains; cleanup attempted; backups may remain |
| Discovery permission error | Record error, process discovered pairs, final 1 |
| Writer changes target during processing | No coordination; overwrite is possible |
| Example omits externally consumed key | Remove it; source/runtime usage is not consulted |

Most discovery/processing OSErrors are handled. `run` does not wrap every possible exception: recursion exhaustion in very deep trees or output failures can escape; do not promise an exit 0/1/2 mapping for every environmental failure. A cleanup failure can leave a temporary file. Filename/key metadata is not a complete secrecy boundary.

The checked-in suite has 22 `unittest` cases covering caller directories/default root, overrides, recursive/ignored/hidden discovery, exclusions, symlinks, variant precedence/creation, exact blocks and backups, permissions, idempotence, malformed/unreadable input, failure continuation, injected backup/replace failures, preview snapshots, collision-safe backups and retired flags/settings. The presentation update on 2026-10-10 executed all 22 successfully using isolated temporary fixtures. [Verification](../testing/verification.md) retains previously recorded executions separately. Some test cases launch Python subprocesses or exercise synchronization only inside temporary fixtures; no real environments were synchronized.

## 9 Decisions, alternatives and limits

| Implemented choice | Benefit | Cost | Learning alternative / trigger |
| --- | --- | --- | --- |
| Filesystem recursion | Finds ignored runtime inputs | Traverses unexcluded storage; deep recursion | Explicit include roots for large workspaces |
| Script-derived root | Stable scope across caller directories | Installation-layout coupling | Required root for independently installed CLI |
| Authoritative per-target examples | Deterministic structural contract | Omitted required keys are removed | Typed schema when value validation is needed |
| Ordered literal blocks | Preserves values/formatting | Limited grammar and retained duplicates | Concrete-syntax parser for broader syntax |
| Plan shared by previews/writes | Same transformation logic | Preview cannot prove write success | Additional preflight with explicit requirements |
| Backup then atomic replace | Recovery and individual-file visibility | Sensitive copies; no global rollback/lock | Locking or staged transaction for coordinated writers |

## 10 Ordered study roadmap

1. Read the CLI contract and trace `main`, `resolve_root`, `discover`; explain caller-relative overrides and ignored-file discovery.
2. Work through base/specific references, missing targets/references and empty examples on paper.
3. Trace `parse` and `plan` with empty, duplicate and multiline assignments; distinguish key membership from values.
4. Trace preview, backups and replacement; explain per-file atomicity, failure continuation and exits.
5. Read the 22 tests and separate their assertions from historical results and untested concurrency/crash behavior.
6. Rehearse alternatives only after explaining current limits: typed schemas, parser libraries, locks, include policies and retention.

This ordering is suggested study work. It creates no studied/mastered/completed markers.

## 11 Thirty-second answer and deeper questions

“This portfolio CLI keeps environment-file key contracts aligned with authoritative examples. Filesystem recursion finds ignored and nested inputs; a script-derived default root makes invocation scope stable. It preserves allowed literal values, adds missing example assignments and removes absent keys, with backups and individual atomic replacement. Preview aliases let me inspect the same plan. It does not validate runtime usage, secret safety, value types or global transactional behavior.”

Practice follow-ups: Why is idempotence different from runtime correctness? What happens with an empty example? Why must a preview succeed even when changes are proposed? Why can a symlink check race? How would you coordinate writers? Which guarantees require real filesystem/crash tests beyond the existing fixtures?

## Additional source-grounded interview deep dives

Original questions and answers above are preserved. IDs below identify this additional sequence; they do not renumber the retained material. Levels guide rehearsal, not implementation status. Follow-ups include answers so this sequence is self-contained.

### Q001 — Introductory: What does a successful synchronization actually prove?

**Answer:** Implemented: the selected example determines key membership. Existing allowed literal blocks remain, missing assignments come from that example and absent keys disappear. A successful transformation proves neither runtime validity nor that every removed key was unused: the CLI never reads application source or evaluates values. For example, an empty existing value survives even if a database client needs a nonempty password. Theory: structural validation, semantic validation and runtime verification are different contracts. A typed schema could validate ranges or required nonempty values, but would require another maintained specification and might change preservation semantics. That improvement is hypothetical. This distinction matters because reporting “configuration fixed” would promise more than the code delivers.

Follow-up: Could an empty example delete all active assignments? Yes, while preserving target comments. Review the authoritative example before writing. Follow-up: Would running twice prove correctness? No. Idempotence means the transformation reaches a stable result for unchanged inputs; a stable invalid configuration can still be unusable.

### Q002 — Intermediate: Why preserve ordered blocks rather than parse into one dictionary?

**Answer:** Implemented: `Document` stores raw bytes and ordered key/text blocks, including keyless comments and quoted multiline assignments. A dictionary would collapse duplicate keys and lose ordering and formatting unless augmented with concrete syntax. The current plan uses sets for membership and Counter for reference duplicates, while emitting retained target blocks literally. This preserves an empty value and all duplicates of an allowed target key; duplicate examples fail because the reference contract would be ambiguous. Whole multiline blocks are removed together, rather than accidentally leaving fragments. Theory: abstract syntax is useful for meaning; concrete syntax is useful for round-trip editing. A parser library might handle more dotenv variants but must be evaluated for round-trip preservation, not merely value extraction.

Follow-up: Does a comment belong semantically to the next key? The representation does not encode that relationship, so comments may remain after removal. Follow-up: Is the parser a shell interpreter? No. It validates a limited literal grammar without interpolation or execution, which narrows scope and avoids treating data as code.

### Q003 — Intermediate: How does filesystem discovery interact with repository boundaries?

**Answer:** Implemented: discovery recursively scans filesystem entries, not Git tracking. The script-derived default root is the parent workspace, so siblings and nested/hidden directories can be included unless their exact names or path suffixes are excluded. Targets and references still match only within the same directory; there is no cross-repository key union or runtime communication. This choice finds ignored environment files but may scan unexcluded cache/storage directories. Sorting provides deterministic traversal/report ordering at per-directory sorting cost. Theory: discovery scope and business ownership are different boundaries. Explicit include roots or Git-aware discovery could narrow scans, but Git-only scanning would miss ignored runtime files and require another mechanism.

Follow-up: Does invoking from scripts change the default root? No, `__file__` determines it. An explicit relative root is caller-relative. Follow-up: Could moving the installed script change scope? Yes; installation layout is part of the current CLI behavior. Packaging it as a general command would need an explicit root policy rather than assuming this workspace layout.

### Q004 — Challenging: Is backup plus atomic replacement a transaction and a durability guarantee?

**Answer:** Implemented: before replacing a changed existing target, the CLI writes original and removed-block backups in a unique private session. It writes a same-directory temporary file, flushes/fsyncs it, applies mode bits and uses `os.replace`. Readers normally see the old or new individual file rather than a partially overwritten file. That is not an all-workspace transaction: another pair may fail after an earlier replacement succeeds. Nor is it a demonstrated power-loss guarantee, because the parent directory is not fsynced and storage behavior was not tested. Backup permissions reduce access but the bytes remain plaintext.

Follow-up: What if backup succeeds and replacement fails? The original target remains and backup artifacts may remain; other pairs continue. Recovery is operator-directed. Follow-up: What if another editor changes the target after it was read? There is no lock/recheck, so replacement can lose that edit. A lock with change detection and directory fsync could strengthen guarantees, but introduces coordination/portability requirements and is not implemented. A multi-file rollback would also need a defined failure policy, not just more backups.

### Q005 — Challenging: How would you test failure handling without touching real environment files?

**Answer:** Implemented evidence: the existing suite uses temporary fixture trees and injected failures to exercise parsing, previews, variant precedence, backups, replacement, permissions and continuation. A meaningful preview test snapshots the entire fixture tree before and after and asserts no target or backup appeared; it must also verify the calculated changes, otherwise doing nothing would pass. For writes, compare exact retained multiline bytes and recoverable originals. Inject backup failure before replacement and replace failure after backup, then assert target state and continued processing independently. These prove bounded fixture behavior, not power-loss durability or every filesystem.

Follow-up: Is mocking `os.replace` enough to prove atomicity? No; it verifies call ordering/error handling. Real filesystem and crash experiments would test different guarantees and remain gaps. Follow-up: How would you inspect performance? First separate traversal, parsing and plan costs using synthetic trees under separate authorization. Large numbers of missing keys can expose list-membership costs; deeply nested trees can expose recursion limits. No benchmark ran here, and the application test suite was not rerun.

## Source reconciliation — 2026-10-18

`000949ff926fcc71428855193a2a029520f7e887`. The source, API/CLI entry points, persistence/resource boundaries and test definitions were reviewed statically. The existing explanations and interview answers remain applicable within their recorded limits. No runtime test results were produced. See the project’s standalone [implementation and interview path](../guides/implementation-study.md).
