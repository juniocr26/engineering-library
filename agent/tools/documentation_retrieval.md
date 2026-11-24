# Optional bounded helper retrieval

Version 0.1.3 is a local Python API for explicitly registered Python/Go source.
It does not install a server, discover arbitrary repositories or change the
Ruby agent's default routing. The operator supplies canonical nonoverlapping
source/journal roots, immutable revision identities, full-file hashes, languages
and allowed lexical selectors. Requests contain exactly six string fields:
`request_id`, `source_id`, `revision`, `path`, `qualified_symbol` and
`expected_sha256`.

Reads use directory descriptors and no-follow flags, bounded regular files and
stable-read checks. Sources are limited to 64 KiB, complete callable quotes to
6,144 bytes and responses to 16 KiB. Python AST extraction runs in a worker with
a three-second deadline; the existing Go AST producer has a twenty-second
deadline. No supplied source, decorator, annotation, import or callable is
executed by retrieval.

The default budget is four extraction attempts and 24,576 cumulative quote
bytes **per tool instance**. A failed extraction consumes an attempt. Duplicate
requests do not repeat extraction or inject the quote again. A concurrent call
on the same instance returns an interrupted/in-progress status without another
reservation. Separate instances do not share a global step budget; an eventual
agent orchestrator must own its session budget.

## Durable results and recovery

Each reserved identifier owns three exclusive artifacts:

- `ID.request.json` binds the exact canonical request.
- `ID.result.json` records FOUND or INCONCLUSIVE with source/registry/extractor
  identity and budget accounting.
- `ID.receipt.json` binds the result bytes, request, registry, source and
  extractor through an independent checksum record.

Files and their parent directories are synchronized. This is a recoverable
sequence, not an atomic three-file transaction. A crash between writes can leave
a reservation or result without a receipt. Such a state is retained as
`IN_PROGRESS_OR_INTERRUPTED` and is never automatically retried.

Before reporting a duplicate, the tool rechecks current source bytes, receipt
integrity, exact result schema, request/registry/extractor identities and the
quote against physical source lines. It then rechecks source/root consistency.
Changed implementation files require an explicit operator reload. Journal root
replacement is refused within an existing instance.

Version 0.1.1 results are preserved as `LEGACY_RESULT_REVIEW_REQUIRED`. No
automatic migration, overwrite or fresh extraction occurs under the old ID.
If a new experiment is justified, the operator must create a new explicit
request ID or owned journal and preserve the prior evidence.

A checksum receipt is an integrity check, **not a signature or authenticated
history**. An operator with write access to both artifacts can replace both.
Physical-source and schema validation catch several such inconsistencies, but
there is no claim of protection against a fully compromised runtime or owner
filesystem. Use the separately preserved manifests and archives for recovery.

## Meaning of a result

FOUND means a complete physical lexical declaration was retrieved. It does not
establish a runtime method binding, decorator effect, inherited interface, helper
semantics or successful operation. Python conditional, duplicated, imported,
deleted and known conflicting bindings are refused. Pattern captures and known
assignment expressions in outer-evaluated declarations also obstruct ownership.
An inherited method or dynamically assigned attribute requires more evidence;
the tool does not invent a declaration for it.

The [new-family evaluation](../research/documentation-intelligence-20261119/helper-new-families-evaluation.json)
exercised Go path, Python context-manager and Python JSON decoder source:
six complete quotations and three safe refusals matched the manually frozen
structural references. These are new actual source families for this tool
evaluation, not a certified model holdout or proof of general semantics.

To roll back use, omit this optional API call and retain its journals and pinned
source. Ordinary Ruby behavior has not been redirected. The retained old tool
source is historical evidence, not a recommendation to resume its weaker cache
validation. No result approves publication, commits or training.


## Frozen operation configuration

Version 0.1.3 pins the initial canonical registry, its digest, journal identity and
configured limits. Every request uses an operation-local registry snapshot and
rechecks public configuration before delivery, including duplicate lookup.
Changing an instance allowlist cannot add an unregistered file while retaining
the old registry hash. A caller that needs a new source permission must construct
an explicit new valid helper. Path objects used for trusted roots normalize to
strings without modifying the caller's original dictionary.

A configuration drift during extraction retains the interrupted reservation and
withholds the quotation. No retry or migration is inferred. Earlier 0.1.2 cache
records remain preserved as legacy records requiring review. These guards address
accidental trusted-process configuration drift; they are not a multi-user
permission service or a sandbox against arbitrary Python code.
