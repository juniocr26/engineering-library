# Map argument binding: presence, order and the prefix returned on error

Codex-authored source-reviewed correction; pending owner approval. SQLx revision 41dac167fdad5e3fd81d66cafba0951dc6823a30, named.go. Actual local-agent baseline: sqlx-bind-map. Exact evidence: [source excerpt](source-excerpts.json). No SQLx application was compiled or executed.

## The two inputs have different jobs

The declaration `bindMapArgs(names []string, arg map[string]interface{}) ([]interface{}, error)` receives an ordered slice of names and a map of corresponding values. It builds a positional argument slice. The selected body does not receive a query string, a connection or a transaction. Its behavior must not be confused with parsing named placeholders, rewriting SQL or executing a database operation elsewhere in the package.

The actual local-agent baseline recognized the high-level map lookup and accumulation. It did not fully describe the accumulated prefix returned on error, the presence flag when a value is nil, duplicate names or empty input. This correction preserves those valid baseline observations while making the missing cases explicit. The source is frozen; the examples below are source-derived consequences under normal Go map/slice semantics, not observed database executions.

## Allocation starts with zero accumulated values

The first statement initializes `arglist` with `make([]interface{}, 0, len(names))`. The length argument is zero; `len(names)` supplies initial capacity. This does not prepopulate the result with one zero value per name. Values enter the result only through the later append statement. Describing this as a fixed-size result array would therefore lose both the slice type and its growing length.

The loop ranges over names. It does not iterate the map and does not sort the supplied names. Thus the positional order follows the supplied name sequence on the ordinary successful path. This is important when a caller expects its placeholder order to match the resulting values, but the selected function itself does not verify any placeholder cardinality or query text.

## Presence is checked separately from the stored value

Each iteration performs `val, ok := arg[name]`. Its guard is `!ok`. It does not test whether `val` is nil, zero, false or an empty string. A key that exists with a nil interface value therefore follows the same append path as any other present value. Missing and present-but-nil are different cases. Replacing the presence test with a value test would change this contract.

Under ordinary Go map semantics, reading a nil map is also distinct from writing to one. For a requested name, the lookup has no matching key and reaches the missing-name path; this body performs no map assignment. Empty names produces no lookup at all. These observations describe the shown path and do not promise freedom from every possible runtime failure or concurrent mutation.

## The first missing name returns the existing prefix

The missing-name branch returns `arglist` together with `fmt.Errorf("could not find name %s in %#v", name, arg)`. The already accumulated slice is retained in that written return. The body does not clear it or substitute a nil slice before returning. If the error expression completes normally, this return exits the function before processing later names.

For example, consider names containing a, missing and b in that order, with values available only for a and b. After appending the value for a, the second lookup reaches the error branch. The returned slice contains that first value; the later value for b is not appended by this invocation. A summary that says only “returns an error when a key is missing” omits a material part of the two-result contract.

## Duplicates and empty input are preserved cases

When the key is present, the body appends `val` and proceeds. It contains no deduplication set, deletion from the map or consumption marker. Repeated names can therefore append the same mapped value repeatedly. The output is not guaranteed to contain unique values merely because a map is used for lookup. Appending interface values also does not demonstrate a deep copy of referenced objects.

After the loop, the final written statement is `return arglist, nil`. With no names, the loop body is skipped and the initially empty allocated slice reaches that return. The function's ordinary completed result has one appended value per successfully processed name, including duplicates. Caller handling of an error, subsequent SQL execution, object ownership and thread safety remain separate contracts. The corrected chapter is pending owner review, with no automatic training approval or claim that the local model learned these distinctions.

