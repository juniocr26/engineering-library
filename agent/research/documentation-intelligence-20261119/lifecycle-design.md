# Bounded documentation lifecycle design

Status: authorized local development protocol, frozen before implementation. This
pipeline recommends technical changes; it cannot authorize publication, commits,
training gold or arbitrary source execution. Existing Ruby generation is separate.

Planning consumes two immutable source observations and a bilingual documentation
claim registry. Observations require exact source bytes, producer identity,
physical spans and full-file hashes. Neither generated prose nor a source hash
change proves a changed contract. Formatting, comments and local names may change
while admitted public facts remain identical.

Start with a small Python AST subset: written signatures, literal defaults,
direct constant/parameter returns and equivalent local-constant assignment plus
return. Unsupported decorators, conditional declarations, unresolved dependencies
or incomplete scope must refuse rather than claim semantic completeness. Other
languages may use existing verified syntax packets without claiming bindings.

| Action | Required evidence |
| --- | --- |
| ADD | Positive current contract, complete prior scope and explicitly complete documentation registry without a matching claim |
| MODIFY | Existing claim and changed admitted fact, or explicit rename/relocation evidence; patch only affected managed content |
| REMOVE | Positive retirement evidence in frozen approved registry, complete scope and rename/relocation checks; absent search alone never suffices |
| NO-OP | Current admitted facts already documented; preserve bytes/mtime and avoid inference |
| INCONCLUSIVE | Missing, stale, conflicting, unsupported or untrusted evidence; preserve current documentation |

Contract identity differs from path and display symbol. A move or rename is not
feature removal. Documentation already correct for current source remains NO-OP
even if previous source differs. Scope of claims limits invalidation.

Planning is read-only. A separate explicit candidate operation checks source and
document hashes, requires unique managed markers and equal language identities,
and preserves all bytes outside owned blocks. Unowned human content is retained
for review. Before REMOVE, archive original bytes by hash; active candidates and
historical/migration content have different identities. Navigation, FAQ and
examples are dependencies, not permission to erase historical evidence.

Freeze expected actions before evaluating all owner-listed scenarios. Report
five-outcome confusion, false additions/modifications/removals, missed changes
and unnecessary generation. Any false removal rejects the implementation.
Keep languages and correlated source families together. Development-exposed
synthetic cases are not certified holdout or owner-approved training data.

Observed runtime fallback: backend is stopped; server entrypoint executes
db:prepare and catalog:sync. Do not start it or mutate the database. Existing
serve-only Ollama was reactivated. Host stdlib tools and packaged native source
producers permit independent work. Historical Ruby262/1787 is not a fresh test.
No new containers, services, schema changes or external application access.


## Dated typed-input consistency correction

The direct planner is now 0.3.5. Managed candidate construction, owned workspace
preparation and restricted FAQ maintenance are 0.1.1. Each call copies its nested
input containers before validation and uses that local copy for subsequent
planning, replacement checks, source rechecks and recorded preconditions. The
workspace `prepare` argument is a strict Boolean; a truthy string does not request
filesystem output.

The [six-path regression](typed-input-snapshot-evaluation-v2.json) preserves the
actual pre-fix failures, including a REMOVE applied to an isolated memory
candidate after a correct MODIFY recommendation, two false NO-OP results and
source/document hash drift. No original or published document was removed.
Current copies prevent those controlled caller edits from rebinding the request;
a fresh explicitly valid plan remains supported. The canonical 24-case matrix
still matches 22 references, with the same two safe JavaScript abstentions.

The [safety-cut ledger](implementation-safety-cut-ledger.json) keeps earlier
recovery/test success separate from permission to resume known weaker code.
Historical sources, candidates, logs and capsules remain recoverable. These
controls do not create an arbitrary-Python sandbox or an atomic filesystem
snapshot, and no publication, Git action or training approval is implied.
