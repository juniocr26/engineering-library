# Managed candidate construction

`documentation_candidates` version `0.1.2` prepares a separate document byte
string. `documentation_maintenance` version `0.1.4` uses it for explicitly
registered, owned synthetic workspaces. Neither entry point publishes documents
or changes the ordinary Ruby agent route.

The caller supplies one bounded UTF-8 document, its language and a list of
operations. Each operation pins the entire file, the source packet and the
logical claim identity. Source-supported replacements are paired in English and
Brazilian Portuguese. Caller-owned containers are copied before validation.

An addressed claim uses standalone `documentation-agent:claim:<id>:start` and
`documentation-agent:claim:<id>:end` HTML comment markers. Nested, duplicate or
unmatched markers refuse. These are explicit operator addresses; their presence
does not discover ownership or distinguish human prose from an illustrative
marker snippet. The caller must supply an appropriate reviewed document scope.

| Action | Required physical document relationship |
| --- | --- |
| ADD | One explicit insertion anchor, no existing block with that identity and no expected existing block hash |
| MODIFY | Existing addressed block, exact expected body hash, and body text equal to the packet's existing claim |
| REMOVE | The same existing-block checks plus the source planner's positive retirement decision |
| NO-OP | Existing addressed block, exact expected body hash, and body text equal to the source-supported packet claim |
| INCONCLUSIVE | Preserve the input bytes without certifying that the physical claim is correct |

NO-OP cannot be justified by a correct inline packet alone. A document saying
“returns 1” is not current merely because the caller submits a packet saying
“returns 2” against source returning 2. That mismatch refuses, even when the
whole-file and existing-body hashes accurately identify the stale document.
Missing block addresses or stale body hashes also refuse. Valid NO-OP returns
the original bytes and requires no history; the workspace does not create a new
candidate directory for that result. Unaddressed human documents require a
separate reviewed plan and are never silently adopted.

For actual edits, ownership metadata remains mandatory and human content outside
the selected edit ranges is preserved byte for byte. Changed output requires
history. The workspace separately checks physical sources and inventories,
archives every original document before writing candidate outputs, and refuses
new broken local Markdown file links. Fragment semantics remain unverified.

Before returning a prepared candidate, the workspace now rechecks the candidate
root and parent identities, reads back the exact active/history inventories and
contents, compares preconditions and the history index byte for byte, and verifies
the serialized result. Unchanged active documents retain their expected mode and
mtime. The checks occur before and after writing the result, alongside original
source rechecks. Unexpected files, corrupt copies, replaced roots or symlinked
output directories cause refusal. Partial evidence and replacement human files
are preserved; there is no automatic repair or cleanup.

The [output-closure study](../research/documentation-intelligence-20261119/candidate-output-closure-evaluation-v1.json)
preserves five prior false success reports, their controlled mutations and the
corrected refusals in fresh equivalent workspaces. File existence alone does not
establish completion: a result written before a final refusal may remain in a
partial candidate and requires review. Sequential readback does not protect
against another writer changing files after the final check.

These APIs support closed source/claim grammars, not arbitrary prose review or
complete repository semantics. In-process snapshots and sequential filesystem
rechecks are not a Python sandbox or an atomic multi-root transaction. A checksum
is an integrity comparison, not authenticated authorship or owner approval.

The [physical NO-OP study](../research/documentation-intelligence-20261119/noop-document-binding-evaluation-v1.json)
preserves two real pre-fix false reports, their frozen inputs and corrected
refusals. Earlier recovery capsules retain the earlier implementation and its
dated tests; recovery success does not certify a newly discovered behavior.
