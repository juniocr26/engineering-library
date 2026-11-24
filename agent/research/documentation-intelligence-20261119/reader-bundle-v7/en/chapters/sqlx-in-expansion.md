# SQLx In: slice expansion, helper boundaries and mismatch errors

Codex-authored source-reviewed correction; pending owner approval.

SQLx revision 41dac167fdad5e3fd81d66cafba0951dc6823a30; actual completed baseline: sqlx-in-expansion-recovery. [Exact source evidence](../references/ref-4a1991de42b648e8194e.md).

## The three results are not database execution

The declaration is `In(query string, args ...interface{}) (string, []interface{}, error)`. It prepares a query string and argument slice. The shown body does not receive a connection, invoke a database statement or prove that the resulting query is valid SQL. The local-agent baseline correctly recognized the parameter and result shapes, but invented an error when more than thirty-two arguments are supplied and misdescribed the argument count.

The completed recovery response followed a power interruption that left the first request without a preserved response. That original attempt remains separately recorded as interrupted; its tokens and success are unknown. The replacement response was actually received and retained. The writer refused it for omitting the required qualified name `sqlx.In`, and source review independently rejects its critical allocation and control-flow claims. This chapter is a Codex correction, not a claim that the model learned the contract.

## The stack array is an allocation choice, not a limit

The local `stackMeta` has thirty-two metadata entries. When the number of arguments fits, meta uses a slice of that array. Otherwise the code allocates `make([]argMeta, len(args))`. There is no error return in that allocation-choice branch. Saying that more than thirty-two arguments are rejected confuses the small local buffer with a public cardinality limit.

The first pass processes arguments in order. For an argument satisfying `driver.Valuer`, it calls Value and immediately returns an empty string, nil arguments and the received error when that call reports an error. The transformed local argument then enters slice classification. `flatArgsCount` accumulates the length of each expandable slice and one for each non-slice; it is not merely the count of non-slice arguments. This preparation pass happens before query rewriting.

## A dereferenced type is not a dereferenced value

`asSliceForIn` first rejects a nil interface. It obtains `reflect.ValueOf(i)`, passes that value's type to `reflectx.Deref`, requires a slice kind and excludes the exact type `reflect.TypeOf([]byte{})`. The baseline omitted the byte-slice exception and generalized the helper as accepting every slice. The exact-type comparison should not be silently expanded into an unsupported rule about every named byte-slice type.

The supplied `Deref` helper contains one if, not a loop: for a pointer kind it replaces the local type with its element type, then reaches the single final return. It does not repeatedly strip arbitrary pointer depth. It also does not modify the `reflect.Value` held by `asSliceForIn`. That helper returns the original value. A description must therefore not promise transparent pointer-to-slice value handling merely because a type was dereferenced. The calling In body subsequently uses the returned value's Len method; full runtime behavior for such inputs was not tested here.

## Empty slices and the no-slice path occur before scanning

For a classified expandable slice, In records its length and rejects length zero with an empty string, nil arguments and the empty-slice error. This happens during the first pass, before searching the query for question marks. It is not conditional on reaching a matching placeholder later. An empty exact byte slice follows the helper's byte-slice exclusion instead of this expandable-slice branch.

If no expandable slice was found, the fast path returns `query, args, nil`. Those are the original argument slice and the original query. The earlier preparation loop has already run, so this does not mean no Valuer was called. It also means the later placeholder-count checks are skipped on this path. A blanket statement that every invocation verifies argument and placeholder counts would be wrong.

## The rewriting path preserves argument order

With at least one expandable slice, the body creates `newArgs` and a string builder, then searches successive query suffixes for the question-mark byte. A scalar metadata entry appends its stored value and advances the offset. A slice entry writes the prefix through that placeholder, adds comma-separated question marks for additional elements and delegates element appending to `appendReflectSlice`. The remaining query suffix is then processed in the same argument order.

The manually expanded `appendReflectSlice` evidence handles interface slices by variadic append, integer and string slices by ordered loops, and other cases by indexed reflection. The selected baseline did not receive this helper body, so these details are correction evidence rather than model discoveries. The question-mark search shown here is not a SQL lexer that excludes quoted strings or comments; no such parsing state appears in these selected functions.

## Mismatch errors are distinct from the successful tuple

During rewriting, encountering another placeholder after all metadata entries have been consumed returns an empty string, nil arguments and the more-bind-variables error. After scanning, metadata entries left unused produce the fewer-bind-variables error with the same empty-string/nil-result shape. These are separate written branches. They do not return the partially accumulated `newArgs` prefix as `bindMapArgs` does in its different missing-name contract.

The successful final statement returns `buf.String(), newArgs, nil`. Describing that last result merely as “an error” loses the explicitly written nil success value. The whole corrected contract remains conditional on ordinary completion of invoked helpers and reflection operations. No SQLx application or database was executed, and no model weights changed. Exact source, retained license notices and bilingual code-span parity support review; owner approval and training rights remain separate gates.

## Engineer FAQ

<!-- reading-section: faq:metadata-array-not-argument-cap -->
### Are more than 32 arguments rejected?

No such rejection is written in the allocation branch. Larger input allocates metadata sized to the argument count. Normal allocation and helper completion remain assumptions; the stack-buffer size is not the public limit claimed by the historical baseline.

<!-- reading-section: faq:valuer-before-no-slice-fast-path -->
### Does the no-slice path skip every helper and validate placeholder counts?

The preparation loop has already run, including any applicable Valuer call. When no expandable slice is found, the function returns the original query and argument slice before the rewriting mismatch checks. It does not substitute all transformed local values into that original slice.

<!-- reading-section: faq:byte-scan-not-sql-parser -->
### Does question-mark scanning understand SQL quotes and comments?

The selected implementation searches bytes with `strings.IndexByte`; no SQL quoting or comment state is shown. Likewise, the exact byte-slice exclusion should not be generalized to every separately defined slice type without its own evidence. The result still requires appropriate downstream placeholder handling and database execution elsewhere.
