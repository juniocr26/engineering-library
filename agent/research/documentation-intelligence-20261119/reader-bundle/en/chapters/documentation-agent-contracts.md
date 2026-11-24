# Documentation agent: source, identity and ownership contracts

Codex-authored source correction, pending owner review. Baseline and exact source cards: [review packet](../references/ref-1c024ddebac892088347.md).

## Observed baseline and evidence identity

The historical section below is a Codex-authored correction based on twelve local-agent passes from the previous campaign. Those counts are not current-campaign calls and do not claim that the local model produced a reliable chapter. The experiment used the existing project workflow, the approved llama3.2:3b identity, an 8192 context setting, four CPU threads and at most five facts per pass. It completed twelve requests in 1523.449 seconds. Nine section responses passed the writer; three were refused. Full review of all forty returned English/Portuguese fact pairs approved no complete response. Passing structural and citation checks therefore does not establish factual correctness.

The source revision recorded in the plan is the observed Git HEAD fe2d062f7c791fa35288929bf27c7c1cf2055bf8. The inspected implementation includes current working-file changes, frozen in a separate caller snapshot. Its command version is 1.9.39 and its project workflow version is 1.0.7. The plan's Git value does not assert that those working bytes belong to that commit. Exact selected-file hashes, original physical ranges and raw requests are preserved in the experiment protocol and review packet. This chapter uses those frozen implementation bytes; later experimental metadata is outside this source cut.

## Selection is a bounded contract

The ordinary evidence collector enumerates supported extensions and explicitly named manifest files. It excludes configured directory names, skips symbolic links and stops at nested repositories. Explicit file selection and automatic sampling take different failure paths. An explicitly selected invalid UTF-8 file or a file containing NUL causes refusal before inference. Automatic sampling may skip such a file. Describing both as silent filtering loses the distinction that protects a requested complete source selection.

For ordinary explicit selection the collector uses a 24576-byte context budget and a twelve-file limit. Automatic sampling uses a 6144-byte budget and four files. A selected complete unit is subject to a separate 6144-byte quotation limit. These are byte limits, so multibyte text must be measured with bytesize rather than character count. Complete-unit selection is not a declaration that the surrounding imports, helpers or runtime dependencies have been supplied. Project section ranges have their own smaller bounds: one to four physical ranges, each nonempty quotation at most 1900 bytes. A range card deliberately keeps complete_unit false.

## What enters the model context

The method skill_context has an immediate baseline branch returning a two-element array: an empty String and an empty Hash. It does not return an empty Array. In skills mode, the method reads exactly three fixed paths under the agent directory: skills/evidence/SKILL.md, skills/authoring/SKILL.md and skills/review/SKILL.md. It extracts the marked English context block when one exists, otherwise uses that file's full text, and joins the resulting texts with blank lines. The second return value maps relative skill paths to digests of the complete skill-file text.

Those operations do not discover arbitrary installed skills, load every research note or establish compatibility with a plugin standard. Portuguese prose stored in other files is not automatically included merely because the model writes a Portuguese answer. Research receipts and corrected chapters are durable evidence for this campaign, but no inspected consumer automatically feeds that entire archive into the local model or a trainer. The baseline's description of an array of texts and paths was consequently wrong about both the data shape and the actual consumer boundary.

## Metadata checks and runtime identity have separate owners

The method model_recovery_lock reads recovery/manifest.json, rejects a symlink, validates the containing directory and parses a schema_version equal to integer 1. Optional mode can return nil when the file is absent. Invalid JSON and missing metadata are wrapped as model-integrity errors. This method loads metadata; the selected body does not checksum active skills or contact Ollama. Assigning those later operations to this loader was an actual baseline error.

The method approved_model_identity checks the model record, the requested model name and the shape of its expected runtime digest. A syntactically valid expected digest is not a live runtime match. The method verify_model_identity performs the additional checks: it compares the request's model, requires the three active skill entries, validates each skill's SHA-256, queries the configured endpoint's tags and requires exactly one matching installed model with the expected digest. The transport calls identity verification before and after inference. These are identity checks, not proof of application behavior or training quality. A changed or missing model is refused rather than silently replaced.

## Request construction does not validate its response

The fact_limit method accepts a String consisting of exactly one digit from 1 through 5, then converts it to an integer. The source_model_request method constructs a JSON schema with evidence IDs and paired en/pt-br fields. It requests temperature 0, seed 42, the selected context setting and at most 1800 generated tokens. Chat transport separates system and user messages; generate transport combines text in a prompt. An explicit authoring question is labeled as a task, not as a verified answer. Feedback, when present, is labeled assisted revision.

The method prepare_model_request optionally adds num_thread and always sets keep_alive to zero. The reduced-context byte check belongs to call_model, not that preparation method. The actual call validates HTTP status, response type and UTF-8, envelope shape, done true, done_reason stop, matching model and String content before parsing the result JSON. It also repeats the identity check after the response. A valid transport envelope can still contain a false statement, an omitted contract or a copied prompt template. The project-assembly baseline demonstrated the last case: all five returned entries repeated the explanation placeholders and were refused by the writer.

## Ownership and source consistency are checked at specific moments

The atomic helper creates a sibling temporary file exclusively, writes and flushes the bytes, synchronizes the file and renames it over the target. It preserves existing permission bits and refuses a symlink target. This supports replacement of an individual file; it does not lock the destination against every other writer, freeze a collection of source files or prove crash durability for an entire directory transaction. The check_ownership method separately compares current owned outputs or navigation blocks with recorded hashes and rejects human edits, unowned files or removed owned outputs.

ProjectCommand first compares the observed repository HEAD with the plan. It then stages selected working-file bytes while recording hashes. Version 1.0.7 keeps the first hash seen for each relative path, refuses a later conflicting read before replacing staged source, rechecks a section's originals after generation and rechecks every collected source before assembly. These checks close the observed mixed-source failure paths. They are not an atomic filesystem snapshot. A change after the last check remains outside that guarantee. Likewise, lifecycle temporary marks the isolated evaluation workflow; it does not promise automatic deletion of valuable drafts or evidence.

## Reuse, deterministic facts and public references remain distinct

Selected-unit model-result reuse requires explicit complete units for every selected file and offline, unassisted generation. Comparing sorted unit keys with sorted file paths checks equality of selected sets; it does not require the owner's input keys to arrive sorted. The cache identity includes the caller version and implementation hash, model identity, context, skill hashes and prepared request. A matching context alone is insufficient: stored result shape, result checksum and origin metadata are validated. Reuse revalidates a preserved result; it is not another inference or a newly trained capability. Nonempty public references cannot be mixed into this reuse path.

The explicit Python source-fact profile invokes a bounded producer, checks exact source/quotation provenance and emits deterministic bilingual explanations without model inference. The Go path invokes a Python launcher for a packaged Go parser and verifies selectors, source hash, producer identities and exact quoted spans. Its syntax proof does not resolve imports, helper semantics, types or runtime bindings. Neither path justifies arbitrary prose beyond its supported profile. The standalone JavaScript producer's later optional ordered-guard packet is a separate tool output; this frozen ordinary writer does not acquire a new production JavaScript consumer.

Public research has another boundary. The value 524288 is this client's response-body limit, not a property of Ruby and not a request-body limit. URL validation restricts schemes, ports, hostnames and resolved addresses. The resolver merely obtains addresses under a three-second timeout; the validation method checks that the returned set is exclusively allowed public addresses. The request helper pins the selected address, uses the URL hostname for TLS and applies its own timeouts and byte bound. The baseline incorrectly transferred both ownership of the limit and filtering behavior of the resolver.

## What this correction establishes

The corrected chapter separates source checks, model transport, prose validation and independent review. The twelve baseline passes expose real failures in method ownership, return shape, concurrency guarantees, source citation and bilingual precision. The correction is an authored research artifact pending owner review, not an automatic training label. This experiment changes no model weights, installs no Harness or MCP server and creates no production retrieval route. Its source family is the agent repository itself, so it cannot serve as an independent held-out family for evaluating these same development decisions.

## Current consumer boundary reviewed in this campaign

The preserved historical cut above remains versioned separately. The current core source was independently compared with the committed owner baseline: caller 1.9.40, project workflow 1.0.8 and Python source-fact profile v4. The Go producer actually used for the new syntax extractions reports 1.6.1. Exact source cuts and hashes are recorded separately in the accompanying source evidence.

The current optional `require_selected_evidence_coverage` setting is a strict Boolean and defaults to false. When enabled, it checks that selected cards fit the fact limit, requests a corresponding minimum, and rejects a result omitting any selected evidence ID. The setting participates in the fingerprint and project forwarding. Covering every ID still does not establish a true explanation or complete dependency reasoning.

| Scope | Explicit bound or boundary |
| --- | --- |
| Ordinary explicit source | 12 files and 24576 bytes |
| Automatic sample | 4 files and 6144 bytes |
| Complete selected unit | 6144 quotation bytes |
| Project physical ranges | At most 4 cards, each at most 1900 quotation bytes |
| New helper prototype | Explicit frozen registry, default 4 extraction steps and 6144 bytes per complete quote |
| New lifecycle prototype | Explicit source/claim packet; technical recommendation and isolated candidate only |

The optional lifecycle prototype is now version `0.3.3`. Its new `parameter = value` default-claim form preserves digits in parameter names; an ambiguous older concatenated form requires review. It checks explicit keyword-only defaults and distinguishes a positively declared required parameter from an unresolved name. A separate restricted FAQ tool prepares memory-only candidates under an explicit question registry. The [default-claim receipt](../references/ref-5e7a297019d7b0ab49b1.md) and [FAQ demonstration](../references/ref-b32ce7950c2a3039d14c.md) record those source-bound controls. The [Go binding study](../references/ref-e655163bba280abaad01.md) is another optional experiment, conditional on a complete build-filtered census and valid compilation. None changes the ordinary writer or establishes neural learning.

The later source-ownership review also refuses a registry and function sharing one module name, avoiding the preserved false-retirement recommendation. Retrieval version `0.1.2` binds completed results to exact request, registry, extractor and physical quotation evidence before suppressing a duplicate. Missing receipts or older results remain recoverable without automatic retry or migration. The [binding regression](../references/ref-b2c7b26daf47a6eab564.md), [cache-integrity study](../references/ref-546e8ddd83f1bebec8d6.md) and [new-family extraction](../references/ref-ed41d59e2a232403f619.md) retain the before/after evidence. Checksums provide integrity comparisons, not authenticated authorship; a lexical quote still does not prove a helper's runtime semantics.

## Engineer FAQ

<!-- reading-section: faq:research-not-training -->
### Does preserving research automatically train or improve the model?

No inspected ordinary consumer automatically loads this archive into a trainer. The new two-arm [owned adapter study](../references/ref-b73070f5fc0865b428fe.md) retrieved helpers but did not demonstrate improved generated coverage. Preserved evidence, deterministic tools, model inference and optimizer-based training remain separate activities.

<!-- reading-section: faq:human-content-boundary -->
### Does the new lifecycle planner publish changes or overwrite human prose?

Its explicit packet API recommends an action. The separate managed-candidate and owned-workspace prototypes require their own ownership, source and history checks and prepare isolated candidates. They do not authorize publication, commits or training gold. The ordinary Ruby routing remains unchanged by these new tools.

<!-- reading-section: faq:helper-not-autonomous-mcp -->
### Is the helper prototype already an autonomous MCP integration?

It is an optional internal read-only registry API with durable request records, bounded extraction and duplicate suppression. The comparison used operator-frozen helper requests. It did not install an MCP ecosystem or create autonomous production tool routing. Syntax extraction still does not resolve every dependency or runtime binding.

The fresh offline Ruby suite passed 262 tests and 1787 assertions in a recovered runtime with documented path support; [the recovery receipt](../references/ref-d41894a8cc4210b8dd62.md) retains the earlier environment failures and exact adaptation. A test pass remains distinct from owner approval, complete factual validation or an unchanged cold deployment environment.
