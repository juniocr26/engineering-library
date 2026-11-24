# Ruff maintenance: explanation presence, content and fix-policy boundaries

`astral-sh/ruff`: `47a28e3a2e2cfcc711f6f68eb7267731478e4a81` → `0e1bf0d2f6bf100ec93f164efcd98514fb12b348`

READY_FOR_OWNER_REVIEW · source-only · no owner approval, Gold, neural inference or training.

## A real revision, with bounded conclusions

This manually reviewed maintenance note compares a local parent/child revision of development-exposed Ruff. The commit changes ten files; the preserved source packet contains eleven selected files at each revision. Five changed dependency files were read alongside unchanged fix-policy files. No Rust compiler, generated macro output, Ruff application, upstream tests, linker or binary-size experiment was executed. The EN/PT clauses below are authored after inspection, not blind predictions or an autonomous maintenance-agent result.

## The explanation interface changes

Before: `ViolationMetadata::explain` returns `Option<&'static str>`. After: it returns `&'static str`. The selected metadata generator changes from wrapping the collected docs in `Some` to emitting the docs directly, and the generated `Rule::explanation` signature changes correspondingly. A clause documenting the optional return type needs modification for the after revision. This is a source-level interface change, not an observed downstream compile failure.

## URL construction no longer consults explanation

Before: `Rule::url` returns `Option<String>` and constructs the URL conditionally on `self.explanation().is_some()`. After: it returns `String` using the same homepage/rule-name formatting pattern without that explanation call. The diagnostic helper correspondingly changes from passing `rule.url()` to passing `Some(rule.url())`. The optional storage API is not shown becoming mandatory. The source comment gives avoiding retention of documentation strings as motivation; this campaign did not measure allocation, linking, binary size or speed.

## A string return type is not a nonempty-content proof

The inspected `get_docs` implementation starts with an empty string, appends recognized doc attributes and returns the accumulated string. With no such attributes it contains no selected-body rejection of an empty result. Before, the selected generator already wrapped that string in `Some`, which can still contain an empty string. The registry test changes from checking `is_some()` to checking `!trim().is_empty()`. That strengthens the inspected assertion about content, but the test was not executed and does not establish that all current rule documentation passed.

## Unchanged fix-policy bodies support a local retained clause

The complete files defining `Fix`, `fix_file`/`apply_fixes` and `FixSafetyTable` are byte-identical across this pair. The settings file is also byte-identical across the pair; its selected `UnsafeFixes` enum/implementation additionally matches the later HEAD snapshot even though that entire later settings file differs. Thus the source-scoped clause about `Enabled` selecting `Unsafe` and `Disabled`/`Hint` selecting `Safe` can remain textually unchanged for this pair. This does not prove whole-program behavioral equivalence or unchanged call reachability.

## Maintenance actions depend on the exact clause

For an explanation-return or URL-return signature clause, the action is `MODIFY`. For the selected fix-threshold body description, the semantic text action is `NO-OP` within this source-only scope. If a document must cite the new target revision, its source pin and bound evidence must still be updated even for retained text. The entire chapter must not be labelled unchanged solely because selected fix files match. No `ADD` or `REMOVE` claim, actual agent decision or independent score is inferred from these authored clauses.

## FAQ

### Did the before generator necessarily return None for missing docs?

No. Its selected output wraps the collected string in `Some`; the collection body can produce an empty string. Optionality and nonempty content are different properties.

### Does the new string signature guarantee all docs are nonempty?

No. The return type alone does not express nonempty content. The strengthened registry test checks trimmed content, but this campaign only inspected its declaration.

### Did diagnostic URL storage lose its optional type?

That does not follow. The selected caller now explicitly wraps the returned URL in `Some`. This note does not establish a storage-schema migration or execute a consumer.

### Did the fix application files change in this commit?

The selected complete `fix.rs`, `fix/mod.rs` and safety-table files did not change. Other files did, including metadata interfaces and consumers; local equality is not whole-commit equivalence.

### Can unchanged prose keep stale source pins?

Not when the documentation contract requires the new revision. Retaining a semantic clause and refreshing its provenance are separate maintenance decisions; hashes must bind the actual target bytes.

### Was the claimed documentation-retention benefit measured?

No. The changed call path and its source comment were inspected. There was no build, linker observation, binary comparison or benchmark; the intended benefit remains unmeasured here.

## Evidence and reproduction

Read-only Git retrieval and diff inspection were performed. The source-cards JSON preserves eighteen file-bound excerpts with native line ranges; the manifest preserves twenty-two selected source files, including both full root licenses and third-party notices. The commands below inspect the interface change and do not run Ruff.

```sh
git -c core.fsmonitor=false diff --no-ext-diff --no-renames 47a28e3a2e2cfcc711f6f68eb7267731478e4a81 0e1bf0d2f6bf100ec93f164efcd98514fb12b348 -- crates/ruff_linter/src/violation.rs
```

[before: crates/ruff_linter/src/violation.rs](https://github.com/astral-sh/ruff/blob/47a28e3a2e2cfcc711f6f68eb7267731478e4a81/crates/ruff_linter/src/violation.rs)

[before: crates/ruff_macros/src/violation_metadata.rs](https://github.com/astral-sh/ruff/blob/47a28e3a2e2cfcc711f6f68eb7267731478e4a81/crates/ruff_macros/src/violation_metadata.rs)

[before: crates/ruff_linter/src/registry.rs](https://github.com/astral-sh/ruff/blob/47a28e3a2e2cfcc711f6f68eb7267731478e4a81/crates/ruff_linter/src/registry.rs)

[before: crates/ruff_macros/src/map_codes.rs](https://github.com/astral-sh/ruff/blob/47a28e3a2e2cfcc711f6f68eb7267731478e4a81/crates/ruff_macros/src/map_codes.rs)

[before: crates/ruff_linter/src/message/mod.rs](https://github.com/astral-sh/ruff/blob/47a28e3a2e2cfcc711f6f68eb7267731478e4a81/crates/ruff_linter/src/message/mod.rs)

[after: crates/ruff_linter/src/violation.rs](https://github.com/astral-sh/ruff/blob/0e1bf0d2f6bf100ec93f164efcd98514fb12b348/crates/ruff_linter/src/violation.rs)

[after: crates/ruff_macros/src/violation_metadata.rs](https://github.com/astral-sh/ruff/blob/0e1bf0d2f6bf100ec93f164efcd98514fb12b348/crates/ruff_macros/src/violation_metadata.rs)

[after: crates/ruff_linter/src/registry.rs](https://github.com/astral-sh/ruff/blob/0e1bf0d2f6bf100ec93f164efcd98514fb12b348/crates/ruff_linter/src/registry.rs)

[after: crates/ruff_macros/src/map_codes.rs](https://github.com/astral-sh/ruff/blob/0e1bf0d2f6bf100ec93f164efcd98514fb12b348/crates/ruff_macros/src/map_codes.rs)

[after: crates/ruff_linter/src/message/mod.rs](https://github.com/astral-sh/ruff/blob/0e1bf0d2f6bf100ec93f164efcd98514fb12b348/crates/ruff_linter/src/message/mod.rs)

Internal review artifact; rights and independence remain restricted as recorded in the campaign.
