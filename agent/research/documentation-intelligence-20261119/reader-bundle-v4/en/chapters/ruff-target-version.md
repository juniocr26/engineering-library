# A Rust method selects a Python target version

Codex-authored correction reviewed against pinned source; pending owner approval.

Repository: ruff; revision: 0222c19dd8e0c9a927f2e47bf3774a108431da25; baseline: ruff-target-version. [Exact source excerpts](../references/ref-142456e64cf893e79bce.md).

## Implementation language and result domain

The actual local-agent baseline correctly associated the method with `FormatterSettings` and noticed a path-based helper followed by a fallback. It nevertheless described a target version for a Rust project. The selected signature explicitly returns `PythonVersion`. Rust is the implementation language of this method; it is not the version domain named by its result type. The same domain error appeared in both generated languages.

The selected method is `resolve_target_version(&self, path: &Path) -> PythonVersion`. Its receiver is shared and its path argument is borrowed. This declaration and the short body identify a settings lookup. They do not establish a formatter run, a parsed Python module, a project-language detection procedure or a compiler invocation. No Ruff executable or Rust project was run for this chapter.

## The helper result is followed by a fallback

The body calls `self.per_file_target_version.is_match(path)` and then applies `unwrap_or(self.unresolved_target_version)`. The spelling is important: there is no local conditional returning a Boolean and no numeric version literal in this method. Under the ordinary Option interpretation of the call chain, a supplied matching value is used; absent that value, the stored unresolved target supplies the fallback.

That describes the visible selection boundary. It does not reveal the helper's matching algorithm. The original selected packet did not include the implementation of `is_match`, so it did not establish glob precedence, first-versus-last match behavior, path normalization, filesystem access or reconciliation of overlapping rules. The additional source reviewed below establishes a narrower compiled-list selection order. A method name suggesting a match is not enough to fill those gaps with an invented algorithm.

## Stored settings are not numeric defaults

The accompanying field excerpt declares `unresolved_target_version` as `PythonVersion` and `per_file_target_version` as `CompiledPerFileTargetVersionList`. Their distinct types make the roles clearer: one stores a version value, while the other supplies per-file resolution behavior through a helper. The selected method reads them; the body contains no assignment that updates either field.

The word unresolved in the field name must not be translated into an error return. The declared method returns `PythonVersion`, and the visible expression supplies a stored fallback. Conversely, the presence of a fallback does not reveal its numeric value or prove it is the latest supported Python release. Establishing a concrete configured default would require the relevant construction and configuration evidence, rather than a guess from this field name.

## Document the result and keep the helper boundary

A useful caller-facing summary is that the method resolves a Python target version for the supplied path using a per-file lookup and the stored unresolved target as fallback. It should retain the `PythonVersion` result domain and identify the helper call without promising unsupported matching semantics. This is more informative than saying only that it resolves a target, while remaining within the selected evidence.

The correction reuses the original completed model response and its pinned source; it does not rerun a rejected prompt. The whole baseline remains unapproved despite its useful subclaims. Exact source hashes, license notices and bilingual review records accompany these chapters. Code-span parity checks translation consistency, but cannot by itself prove semantic truth, owner approval, training rights or improvement in the local model.

## Engineer FAQ with the helper implementation

<!-- reading-section: faq:optional-version-not-boolean -->
### Is the helper returning a Boolean match?

Its added declaration returns `Option<ast::PythonVersion>`. An empty compiled list returns `None`. Otherwise it asks the match iterator for its next value and copies that version. The caller then supplies the stored fallback when the option has no value.

<!-- reading-section: faq:first-matching-vector-entry -->
### Which matching entry is selected?

The inspected iterator walks the compiled vector in order. For each entry it checks basename, then absolute matching, with separate negation behavior. The helper chooses the first value yielded by that iterator. This establishes compiled-vector selection order; it does not establish the textual order or precedence of configuration files that created that vector.

<!-- reading-section: faq:file-name-expect-panic -->
### Can a method returning PythonVersion still fail?

For a nonempty compiled list, the match iterator obtains the path filename with `expect("Unable to parse filename")`. A missing filename can therefore reach a panic rather than a returned Result error. The empty-list shortcut returns before entering that iterator. No numeric fallback or actual formatter execution is established by these source observations.

The compiled-list constructor can report invalid glob construction through its own Result contract. That configuration-stage error and the resolver's PythonVersion result belong to different functions. Imported glob implementations, broader path normalization and runtime behavior remain outside this review.
