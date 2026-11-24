# Boltons file maintenance: depth filtering and rotation boundaries

Status: isolated source-reviewed **evaluation-only** candidate, pending owner
review. This chapter is not active documentation or an approved training target.
It describes Boltons revision `c23dbdadb6fecdf505eb4231559561913b84c13f`
(tag `25.0.0`) against `992a58c1036fcf4d52cbf3313b6217b7c07b11d9`
(`24.0.0`). It does not describe the latest upstream version.

## Purpose and context

The inspected `fileutils.py` is a Python filesystem utility module. This review
covers only `iter_find_files` and the newly declared `rotate_file`, plus the
written flush/fsync sequence in `AtomicSaver.__exit__`. It does not establish
application dependency wiring, a production deployment or cross-platform crash
durability. No database, service or private project was used.

Complete source snapshots and the upstream license are retained in
[25.0.0 source](../../public-sources/25.0.0/boltons/fileutils.py),
[24.0.0 source](../../public-sources/24.0.0/boltons/fileutils.py), and
[license](../../public-sources/25.0.0/LICENSE). Exact commit URLs and full-file
hashes are recorded in [provenance](../../public-sources/provenance.json).

## Public contracts and configuration

The older `iter_find_files` signature ends in `include_dirs=False`. The current
signature adds `max_depth=None`. The new parameter is used inside the `os.walk`
loop to skip processing a root when its separator-count difference from the
initial directory exceeds `max_depth`.

| Input | Written behavior | Limit |
|---|---|---|
| `max_depth=None` | No depth-based `continue` is selected | Other existing pattern filters still apply |
| `max_depth=0` | Roots below the starting directory are skipped for yielding | Traversal is not pruned by changing `dirs` in this branch |
| `max_depth=1` | The starting directory and one subdirectory level can contribute results | This is a written separator-count rule; filesystem/path edge cases were not executed |
| `include_dirs=False` | Existing directory-inclusion default is preserved | Adding a depth parameter is not evidence that every existing answer needs modification |

The implementation counts components using `os.path.sep`. Do not rewrite this
as a verified canonical-path depth algorithm. The skipped root is handled with
`continue`; the new branch does not clear or replace the traversal's `dirs` list.
Consequently, the source supports filtering emitted results, without proving
that deeper directories are never visited by `os.walk`.

## Newly added rotation function

The current module declares `rotate_file(filename, *, keep: int = 5)`; the older
module has no declaration with that name. The keyword-only position and literal
default are source facts. The annotation does not perform runtime validation.

The body raises `ValueError` for `keep < 1`, returns if the source does not
exist, and raises `ValueError` when an existing source is not a file. It builds
numbered names, renames in reverse order, and then removes the name at the
`keep` boundary if it exists. Filesystem failures can propagate; the selected
function has no rollback or exception handler.

The final removal matters. In the three confined normal-path controls, the
observed backup counts were:

| `keep` argument | Backups remaining | Original filename after rotation |
|---|---:|---|
| `1` | `0` | Absent |
| `2` | `1` | Absent |
| `5` | `4` | Absent |

The controls started with a current synthetic file and numbered backups through
the configured boundary. Their [operation traces](../../public-rotate-observation-v1.json)
show the last boundary backup being removed after the renames. With `keep=1`,
the renamed current file is itself removed. Do not promise that this inspected
revision retains `keep` backups. This is not a claim about later releases.

## Dependencies, errors and durability

`iter_find_files` delegates traversal to `os.walk` and pattern matching to the
module's existing matching machinery. `rotate_file` calls filesystem path
queries, `os.rename` and `os.remove`. These written calls identify dependency
direction; they do not verify every platform's replacement or failure behavior.

`AtomicSaver.__exit__` now calls `flush()` and `os.fsync()` on a present part file
before `close()`. This is a meaningful side-effect change. It does not prove an
atomic multi-operation filesystem transaction or crash recovery. The confined
rotation controls did not execute `AtomicSaver` or simulate power loss.

No specific numeric result for elapsed time, disk latency or performance follows
from this review. No model-generated explanation was used as a factual target.

## Examples and executed research commands

For the reviewed signature, `iter_find_files(directory, patterns, max_depth=0)`
selects the new depth filter, while `rotate_file(filename, keep=1)` selects the
observed boundary case. These are API illustrations, not instructions to rotate
real files. Use only disposable, owned paths for an execution experiment.

The campaign executed this bounded control from the library root:

```sh
python3 agent/research/documentation-intelligence-20261120/observe_public_rotate_v1.py
```

It compiled only the selected public AST function, not the complete module, and
supplied a confined filesystem facade over new synthetic directories. Existing
output roots are refused; rerunning in the same checkout is not a cleanup or
overwrite operation. The code, protocol, source hash and operation receipts are
preserved. Three normal-path controls do not establish crash safety, concurrent
writer safety or exhaustive error behavior. No diagram is needed to express
this bounded sequential algorithm.

## Engineer FAQ

### Does `max_depth=0` prevent all traversal below the starting directory?

The new branch skips processing and yielding from deeper roots. It does not
prune `os.walk` by editing `dirs`. Claiming that no deeper traversal occurs would
exceed the inspected evidence.

### Does `keep=1` preserve one rotated backup in the inspected revision?

No, in the confined normal-path control the function renames the current file
to the first backup name and then removes that boundary name. Zero backups
remain. The original filename is also absent after that execution.

### Does the new flush/fsync sequence prove crash-atomic saving?

No. The source establishes two calls before closing the present part file.
Neither their presence nor the rotation controls demonstrate crash-atomic
transactions, rollback or recovery after power loss.

### Should the existing default behavior FAQ be removed because the signature changed?

No. The new parameter defaults to `None`, and still-valid statements must be
reviewed individually. A source change is not automatic evidence for removal
or regeneration of unrelated documentation.

## Review and evidence limits

The planner's frozen public evaluation abstained on all eight selected Boltons
cases. That result is preserved; these source reviews are not retroactive model
successes. The family is locally unexposed under a bounded historical scan, but
the cases are correlated and lack independent human review. The chapter and its
four FAQ pairs remain evaluation-only, outside the preserved 77 prior FAQ pairs
and the V10 training-candidate lineage.
