# Cobra: positional argument validation and command execution

Isolated research candidate. Author source review only; separate verification and owner review pending. No publication or training approval.

spf13/cobra @ `adbc8813901bba65827259daa8e22ff94ec1f30e`. This chapter covers the selected contract, not the full repository. Evidence: `source-freeze-v1.json`; criteria: `acceptance-protocol-v1.json`.

## Architecture and behavior

**C01** — PositionalArgs is a function type taking *Command and []string and returning error. [C01: `args.go:22-22`]

**C02** — OnlyValidArgs validates membership only when Command.ValidArgs is nonempty; entries discard the description after a tab. [C02: `args.go:51-65`]

**C03** — NoDuplicateArgs returns an error at the first repeated positional argument. [C03: `args.go:68-79`]

**C04** — MinimumNArgs and MaximumNArgs enforce inclusive lower and upper count bounds; ExactArgs requires equal length. For min <= max, RangeArgs accepts both endpoints. The selected body does not separately validate whether the bounds are ordered. [C04: `args.go:86-124`]

**C05** — MatchAll invokes validators in order and returns the first error; ExactValidArgs delegates to MatchAll(ExactArgs(n), OnlyValidArgs). [C05: `args.go:126-144`]

**C06** — In this execution path, an error from ValidateArgs exits execution before persistent pre-run and pre-run hooks execute. [C06: `command.go:968-1005`]

**C07** — Required-flag and flag-group validation occur after pre-run hooks and before RunE or Run in this path. [C07: `command.go:1007-1019`]

## Example

Synthetic usage fragment, not executed. Resolve dependencies in a separately authorized environment before running. No startup or installer command is authorized here.

```go
validator := cobra.MatchAll(cobra.ExactArgs(2), cobra.OnlyValidArgs)
cmd := &cobra.Command{ValidArgs: []string{"red", "blue"}}
err := validator(cmd, []string{"red", "blue"})
_ = err
```

## Test evidence and limitations

`args_test.go` is preserved as written test evidence. No external suite, example, dependency installer or runtime was executed. Written assertions are not passing results. No benchmark, concurrency guarantee or release-wide API compatibility is established.

## FAQ

### Q001 — Does OnlyValidArgs require a nonempty allowlist?

OnlyValidArgs validates membership only when Command.ValidArgs is nonempty; entries discard the description after a tab. [C02]

### Q002 — Does MatchAll collect every validation error?

MatchAll invokes validators in order and returns the first error; ExactValidArgs delegates to MatchAll(ExactArgs(n), OnlyValidArgs). [C05]

### Q003 — Are all flags validated before pre-run hooks?

Required-flag and flag-group validation occur after pre-run hooks and before RunE or Run in this path. [C07]

## Maintenance and rights

This shallow clone has no local HEAD parent. A historical MODIFY decision is INCONCLUSIVE without a verified earlier source and matching documentation. Missing symbols in this selected scope do not authorize REMOVE. Existing project documentation remains unchanged.

Apache-2.0 / LICENSE.txt. Notices are preserved with the source snapshot. This artifact is evaluation-only, excluded from training and not owner-approved.
