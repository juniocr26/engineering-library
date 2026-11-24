# Cobra positional validators — section-composed candidate

Isolated generated research output; review pending. Source: spf13/cobra, revision adbc8813901bba65827259daa8e22ff94ec1f30e, args.go. Scope: the five selected API groups, not the whole repository or command routing.

## simple

These functions check for specific conditions in the argument slice without modifying it.

Source ranges: args.go:41-47, args.go:68-84.

## allowlist

OnlyValidArgs checks if all positional arguments are valid and returns an error if not.

Source ranges: args.go:49-65.

## bounds

The MinimumNArgs, MaximumNArgs, ExactArgs, and RangeArgs factories return validators that enforce inclusive boundaries and unordered-bound uncertainty. The branch conditions for these factories are based on the length of the input arguments.

Source ranges: args.go:86-124.

## composition

MatchAll allows combining PositionalArgs to work together, while ExactValidArgs checks for exact positional args and validity.

Source ranges: args.go:126-144.

## legacy

The PositionalArgs function type and legacyArgs control branches are defined. The legacyArgs function checks for subcommands and validates arguments accordingly.

Source ranges: args.go:22-39.

## Example

Synthetic statements inside an existing Go function with github.com/spf13/cobra imported as cobra; syntax parsed with the existing Go parser, not typechecked or executed.

```go
validator := cobra.MatchAll(cobra.ExactArgs(2), cobra.OnlyValidArgs)
cmd := &cobra.Command{ValidArgs: []string{"red", "blue"}}
err := validator(cmd, []string{"red", "blue"})
_ = err
```

## Written test evidence

args_test.go exists in the pinned source snapshot; its tests and this example were not executed. Presence of assertions is not a passing result.

## FAQ

### Q001 — How do the NoArgs, NoDuplicateArgs, and ArbitraryArgs functions handle branch conditions?

The NoArgs function returns an error if any arguments are included, while NoDuplicateArgs returns an error if there are any duplicate positional arguments. ArbitraryArgs never returns an error. Branch conditions are checked using if statements and error returns.

### Q002 — What happens if there are no valid arguments?

If there are no valid arguments, OnlyValidArgs returns an error. This is because the function checks if all arguments are in the valid arguments list. If the list is empty, it cannot determine if an argument is valid or not. The error message indicates that there are no valid suggestions for the command.

### Q003 — How do the MinimumNArgs, MaximumNArgs, ExactArgs, and RangeArgs factories handle the case where the number of arguments is exactly equal to the expected value?

The ExactArgs factory returns nil when the number of arguments is exactly equal to the expected value, indicating that the command has the required number of arguments.

### Q004 — What is the difference between MatchAll and ExactValidArgs?

MatchAll allows combining multiple PositionalArgs to work together, while ExactValidArgs checks for exactly N positional args and their validity against the `ValidArgs` field of the `Command`. ExactValidArgs is deprecated in favor of using MatchAll with ExactArgs and OnlyValidArgs.

### Q005 — How does the legacyArgs function handle root commands with subcommands?

The legacyArgs function checks if the command has a parent and if there are arguments. If the command has a parent and there are arguments, it returns an error indicating an unknown command. Otherwise, it returns nil.

## Limitations and preservation

The shallow clone lacks a local parent revision, so historical MODIFY remains INCONCLUSIVE without earlier verified source and matching documentation. Missing symbols in partial source never authorize REMOVE. No general runtime guarantee or production integration was tested. Existing project documentation remains unchanged. Apache-2.0 notices are preserved with the source. No owner approval, publication or training use is authorized.
