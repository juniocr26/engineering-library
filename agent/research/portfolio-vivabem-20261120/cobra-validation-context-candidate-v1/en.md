# Cobra: positional validators in their command context

This isolated chapter covers selected written contracts in `spf13/cobra` at `adbc8813901bba65827259daa8e22ff94ec1f30e`. It connects validator factories, command selection and the ordinary execution path. Exact public source and Apache-2.0 notices are preserved. Source review, native Go syntax parsing and owner approval are different things; no Cobra code or tests were executed.

## Validators and factories

`PositionalArgs` is the function type taking a command pointer and a string slice and returning an error (`args.go:22`). `OnlyValidArgs` runs its membership checks only while `len(cmd.ValidArgs) > 0`. It keeps the portion of each allowlist entry before the first tab, then checks the supplied arguments. Outside that guarded block it returns `nil`; an empty allowlist does not by itself produce a validation error. The helper `stringInSlice` compares strings using equality. Evidence: `args.go:51–66`, `cobra.go:225–232`.

`ExactArgs(n)` returns a `PositionalArgs` function. That returned function checks `len(args) != n` when invoked; calling the factory is not itself validation of a later argument slice. The corresponding minimum and maximum validators reject lengths below or above their bounds, and the range validator rejects values outside its two endpoints. Evidence: `args.go:87–124`.

`MatchAll` returns another validator. Its loop invokes the supplied validators in order and returns immediately on the first non-`nil` error; it does not collect every error. `ExactValidArgs(n)` delegates to `MatchAll(ExactArgs(n), OnlyValidArgs)` and is marked deprecated in the selected source comment. `NoDuplicateArgs` writes a seen set and returns at its first repeated-argument branch. These are selected source contracts, not guarantees about arbitrary callbacks or invalid command pointers. Evidence: `args.go:69–79,127–144`.

## Two different command paths

`Command.ValidateArgs` returns `ArbitraryArgs(c, args)` when `c.Args == nil`; otherwise it calls `c.Args(c, args)`. The selected `ArbitraryArgs` body returns `nil`. It would be incorrect to describe `legacyArgs` as the default branch of this method. Evidence: `command.go:1172–1177`, `args.go:82–84`.

Separately, after its inner command lookup, `Command.Find` calls `legacyArgs(commandFound, stripFlags(a, commandFound))` when `commandFound.Args == nil`. The selected `legacyArgs` returns early when the command has no subcommands. Otherwise, its written error branch requires both `!cmd.HasParent()` and `len(args) > 0`. The two queried helpers return `c.parent != nil` and `len(c.commands) > 0`, respectively. This does not establish every caller or flag-stripping behavior. Evidence: `command.go:757–779,1601–1603,1677–1679`, `args.go:28–39`.

## Validation and hook order

In the selected `Command.execute` path, flag parsing occurs before the positional argument check; parsing errors can return earlier. The method later calls its lowercase `preRun` initializer helper and defers `postRun`. That initializer helper iterates `initializers`; it is distinct from the `PreRun` and `PersistentPreRun` hook fields. Evidence: `command.go:919–922,955–970,1047–1051`.

An error returned by `ValidateArgs` exits before the subsequent persistent pre-run and pre-run hook blocks. When control continues, required-flag and flag-group validation occur after those hook blocks and before the `RunE`/`Run` branch. Earlier returns and hook errors still matter. This is not a claim that every kind of flag handling waits until after hooks or that all hooks necessarily execute. Evidence: `command.go:968–1019`.

## An illustrative fragment

The following owned fragment creates and invokes a validator directly. It does not execute a command, register hooks or demonstrate the complete CLI path.

```go
validator := cobra.MatchAll(cobra.ExactArgs(2), cobra.OnlyValidArgs)
cmd := &cobra.Command{ValidArgs: []string{"red", "blue"}}
err := validator(cmd, []string{"red", "blue"})
_ = err
```

The fragment parses after wrapping it in an owned function with the Cobra import. The module declaration identifies `github.com/spf13/cobra`. Imports were not resolved, and the fragment was not typechecked or executed. No installer, startup or execution command is proposed here.

## Written tests

`TestOnlyValidArgs` and `TestOnlyValidArgs_WithInvalidArgs` contain success and invalid-argument helper calls around `executeCommand` (`args_test.go:155–165`). They are written test evidence, not passing observations in this campaign.

`TestMatchAll` composes `ExactArgs(3)` with a validator checking two-byte argument lengths. Its table includes a success case, a wrong-count case and a wrong-byte-length case, then checks whether errors match the expected failure flag (`args_test.go:477–523`). This illustrates intended composition coverage; it does not prove every branch, arbitrary callback behavior or the example's runtime result.

## FAQ

**Does an empty ValidArgs list itself reject input?** No. In the selected `OnlyValidArgs` body, membership validation is inside the nonempty-list guard and the subsequent return is `nil`.

**Does constructing ExactArgs validate a later slice?** No. The factory returns a validator; its returned function performs the length comparison when called.

**What does ValidateArgs use when Args is nil?** The selected method calls `ArbitraryArgs`, whose selected body returns `nil`. The `Find` path's `legacyArgs` call is separate.

**Does MatchAll continue after a validator returns an error?** No. Its loop returns that first error before later loop iterations.

**Must all flag validation precede pre-run hooks?** No. The selected required-flag and flag-group checks follow those hook blocks, while earlier flag parsing has its own error path.

## Maintenance and limits

The initial inventory recorded a shallow clone without its local HEAD parent. No missing revision was fetched and no historical change is invented here. Missing symbols in a selected scope do not authorize removal. Go declaration parsing establishes syntax, lexical identity and physical quotes; the selected contracts were reviewed separately. It is not a typecheck, runtime binding proof, complete project analysis or general semantic verifier. This chapter is a research candidate, excluded from training and active publication; owner approval and training gold remain false.
