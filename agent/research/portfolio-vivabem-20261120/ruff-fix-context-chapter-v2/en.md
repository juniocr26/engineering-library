# Ruff: from rule fix availability to selected source edits

`astral-sh/ruff` · `0222c19dd8e0c9a927f2e47bf3774a108431da25`

Status: CANDIDATE_FOR_SOURCE_REVIEW; not owner-approved, not Gold, not training data.

## Scope and evidence

This chapter describes the selected Ruff revision, not every released version. It follows rule metadata, diagnostic storage, fix policy and source reconstruction across separate crates. The repository is development-exposed. All conclusions below are source inferences; no Rust compilation, macro expansion, Ruff execution, upstream test execution or source-file modification was performed.

## Metadata is a separate interface

`ViolationMetadata` declares rule identity, explanation, status, category, declaration file and line. The selected `violation_metadata` generator emits those methods and requires status and category metadata, returning a `syn::Error` when either is missing. Its selected output does not attach a `Fix` or implement `FIX_AVAILABILITY`. This is a bounded statement about this generator, not a claim that fixes are absent everywhere.

[S1](#s1) [S2](#s2)

## Availability describes a rule

`FixAvailability` has `Sometimes`, `Always` and `None`. `Violation::FIX_AVAILABILITY` defaults to `None`; `fix_title` also defaults to `None`. The blanket implementation for `AlwaysFixableViolation` sets availability to `Always` and wraps its title in `Some`. These declarations do not themselves construct edit contents or store a fix in each diagnostic.

[S1](#s1)

## Converting a violation does not attach a fix

`Violation::into_diagnostic` calls `create_lint_diagnostic` with the fix argument set to `None`, even when the title is present. `Diagnostic::new` initializes its fix to `None`; the helper calls `set_fix` only when its optional fix argument is `Some`. A help title and an attached edit collection are therefore distinct in this selected path.

[S1](#s1) [S3](#s3) [S5](#s5)

## Storage setters have different meanings

`Diagnostic::fix` returns an optional borrowed fix. `set_fix` assigns `Some(fix)` through `Arc::make_mut` and contains a `debug_assert!` requiring a primary span. Do not describe that assertion as an unconditional release-mode validation. `set_optional_fix(None)` does nothing and does not clear an existing fix; `remove_fix` explicitly stores `None`.

[S4](#s4)

## Constructors label and organize edits

`Fix` stores edits, applicability and isolation. The safe, unsafe and display-only constructors assign the corresponding classification and default isolation; constructors accepting multiple edits sort them by start and end. `applicable_edit` and `applicable_edits` accept a classification explicitly. These bodies store data; they do not run the edits or prove that the author selected the correct semantic classification.

[S6](#s6) [S7](#s7)

## The AST diagnostic guard adds policy

`DiagnosticGuard::set_fix` first checks `should_fix(self.rule)`. When false it removes the diagnostic fix and returns. Otherwise it resolves applicability using the settings table and attaches the reclassified fix. This is a selected AST-checker path, not proof that every direct `Diagnostic::set_fix` call passes through the same policy.

[S9](#s9)

## Fallible construction still calls its closure

`try_set_fix` invokes `func()` before matching its result. `Ok(fix)` delegates to `set_fix`; `Err` logs a debug message instead. Thus the rule-selection check inside `set_fix` does not establish that the construction closure is skipped. `try_set_optional_fix` additionally leaves the current state unchanged on `Ok(None)`. No observed closure side effects or panic recovery are claimed here.

[S9](#s9)

## Safety overrides preserve display-only fixes

`FixSafetyTable::resolve_applicability` preserves `DisplayOnly`. For an input classified as `Safe` or `Unsafe`, it consults forced-unsafe first, then forced-safe, otherwise retaining the input. This describes the resolver body; it does not certify that reclassification validates edit semantics or that both sets can actually contain the same rule through normal construction.

[S10](#s10)

## Applicability is an ordered threshold

`Applicability` derives `Ord` and `PartialOrd`, with implicit discriminants in declaration order: `DisplayOnly < Unsafe < Safe`. `Fix::applies` compares the stored classification with the argument using `>=`. The ordering follows the official Rust contract for derived enum ordering, not a local compiler observation. The method alone would admit a display-only fix at a display-only threshold.

[S6](#s6) [S8](#s8)

## The selected caller narrows the threshold domain

`UnsafeFixes::required_applicability` returns `Unsafe` for `Enabled`, and `Safe` for both `Disabled` and the default `Hint`. Therefore the selected `fix_file` policy admits safe fixes in all three modes, also unsafe fixes in enabled mode, and no display-only fixes. This is an admission filter; overlap and isolation can still prevent edits from being selected. No global claim about every possible `applies` caller is made.

[S8](#s8) [S11](#s11) [S12](#s12)

## The selected function constructs a result

`fix_file` filters diagnostics with an attached, admissible fix. With none it returns `None`; otherwise it returns `Some(apply_fixes(...))`. `FixResult` contains reconstructed code, fix counts and a source map. Despite its nearby comment mentioning writing to disk, the selected body does not perform a filesystem write. Outer persistence and repeated lint/fix iterations are outside this chapter.

[S12](#s12) [S13](#s13)

## Ordering, duplicate edits and conflicts

`apply_fixes` sorts fixes with `cmp_fix`, including special rule precedence, start position and selected tie breakers. It removes edits already present in the applied-edit set before checking whether a first new edit remains. For a first new edit, it checks isolation group membership and then rejects a start position when `last_pos >= first.start()`. Do not reduce this boundary check to a generic interval-overlap theorem or claim every admitted diagnostic changes the text.

[S13](#s13) [S14](#s14)

## Group reservation precedes positional rejection

For a fix with a new edit and `IsolationLevel::Group(id)`, the code inserts the group ID before checking `last_pos`. A positional rejection afterwards does not remove that ID in the selected body. Thus the source does not support a simplified description saying groups are reserved only after successful edit application. This ordering observation is not an executed counterexample or an assessment of the maintainers’ intended policy.

[S13](#s13)

## Reconstruction is not semantic verification

For selected edits the implementation appends untouched slices, replacement contents or an empty replacement, records source-map markers and advances `last_pos` to the edit end. After the fix it extends the applied-edit set and increments a diagnostic count; it finally appends the remaining source. Counting a diagnostic is distinct from counting newly emitted edits, including when all its edits were duplicates. These bodies do not establish whole-program correctness of the resulting Python.

[S13](#s13)

## Existing tests and actual observations

The selected module contains a `#[cfg(test)]` test module, a helper constructing diagnostics, and an `empty_file` test asserting empty output, zero counts and an empty source map. These are inspected test declarations, not passing test results from this campaign. The actual observations were read-only Git source retrieval and editorial source tracing. The host PATH lookup for `rustc` returned no command; this does not establish the absence of every Rust installation or container toolchain. No installation or repository build was attempted.

[S15](#s15)

## FAQ

### Does Always mean every diagnostic already has edits?

No. The blanket implementation sets rule availability and a title, whereas `into_diagnostic` passes `None` as the fix. An attached fix is separate optional state.

[S1](#s1) [S3](#s3) [S5](#s5)

### Does Safe prove correctness or guarantee application?

No. The constructors assign a classification without semantic verification, and the consumer still enforces admission, isolation and positional checks. Classification expresses policy and author intent; it is not an observed correctness proof.

[S7](#s7) [S12](#s12) [S13](#s13)

### Can display-only fixes pass applies?

The method alone returns true at a `DisplayOnly` threshold. The selected `fix_file` caller obtains only `Safe` or `Unsafe` from `required_applicability`, excluding display-only fixes there. The method domain and caller domain must be distinguished.

[S6](#s6) [S8](#s8) [S11](#s11) [S12](#s12)

### Does try_set_fix avoid construction when fixing is disabled?

Its selected body does not establish that. It invokes `func()` first and delegates only an `Ok` result to `set_fix`, where the rule-selection check occurs. An error is logged rather than attached as a fix.

[S9](#s9)

### Does a skipped positional conflict leave the group unreserved?

Not necessarily in the selected body. When a new edit remains, group insertion precedes the positional check, and that later rejection has no corresponding group removal. This is a source-order observation, not an executed Ruff scenario.

[S13](#s13)

### Did this campaign run fixes, tests or filesystem writes through fix_file?

No. Source and test bodies were inspected without executing Ruff. The selected `fix_file` body constructs an optional result; it does not itself write a file. No upstream passing-test, macro-expansion, persistence or whole-program semantic claim follows from this review.

[S12](#s12) [S15](#s15)

## Read-only reproduction example

The equivalent Git retrieval was executed during source acquisition. Run from the Ruff checkout only to display the pinned source; it does not invoke the program. This is not a Rust example or a test result.

```sh
git -c core.fsmonitor=false show 0222c19dd8e0c9a927f2e47bf3774a108431da25:crates/ruff_linter/src/fix/mod.rs
```

## Source references and rights

<a id="s1"></a> [S1: crates/ruff_linter/src/violation.rs:14–117](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_linter/src/violation.rs#L14-L117)

<a id="s2"></a> [S2: crates/ruff_macros/src/violation_metadata.rs:8–60](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_macros/src/violation_metadata.rs#L8-L60)

<a id="s3"></a> [S3: crates/ruff_db/src/diagnostic/mod.rs:60–80](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_db/src/diagnostic/mod.rs#L60-L80)

<a id="s4"></a> [S4: crates/ruff_db/src/diagnostic/mod.rs:373–402](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_db/src/diagnostic/mod.rs#L373-L402)

<a id="s5"></a> [S5: crates/ruff_linter/src/message/mod.rs:82–135](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_linter/src/message/mod.rs#L82-L135)

<a id="s6"></a> [S6: crates/ruff_diagnostics/src/fix.rs:8–55](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_diagnostics/src/fix.rs#L8-L55)

<a id="s7"></a> [S7: crates/ruff_diagnostics/src/fix.rs:57–141](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_diagnostics/src/fix.rs#L57-L141)

<a id="s8"></a> [S8: crates/ruff_diagnostics/src/fix.rs:143–185](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_diagnostics/src/fix.rs#L143-L185)

<a id="s9"></a> [S9: crates/ruff_linter/src/checkers/ast/mod.rs:3889–3933](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_linter/src/checkers/ast/mod.rs#L3889-L3933)

<a id="s10"></a> [S10: crates/ruff_linter/src/settings/fix_safety_table.rs:23–42](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_linter/src/settings/fix_safety_table.rs#L23-L42)

<a id="s11"></a> [S11: crates/ruff_linter/src/settings/types.rs:125–168](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_linter/src/settings/types.rs#L125-L168)

<a id="s12"></a> [S12: crates/ruff_linter/src/fix/mod.rs:20–51](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_linter/src/fix/mod.rs#L20-L51)

<a id="s13"></a> [S13: crates/ruff_linter/src/fix/mod.rs:53–128](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_linter/src/fix/mod.rs#L53-L128)

<a id="s14"></a> [S14: crates/ruff_linter/src/fix/mod.rs:130–170](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_linter/src/fix/mod.rs#L130-L170)

<a id="s15"></a> [S15: crates/ruff_linter/src/fix/mod.rs:172–213](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_linter/src/fix/mod.rs#L172-L213)

[R1: Rust derived enum ordering](https://doc.rust-lang.org/std/cmp/trait.Ord.html#derivable). Current primary-language reference, not evidence of executing a historical toolchain.

The full root LICENSE, including third-party notices, is retained with the source package. The selected repository uses an MIT root license; no blanket file-level, training or public-publication authorization is inferred. Campaign artifacts remain restricted internal review material.
