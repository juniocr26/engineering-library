# Rails request methods: getter ownership, memoization and symbol lookup

Codex-authored source-reviewed correction, pending owner approval. Source: installed actionpack 8.1.4, exact file checksum in [source evidence](source-excerpts.json). Actual local-agent cases: rails-baseline and rails-hinted.

## Similar names do not identify the same body

The inspected file declares `ActionDispatch::Request`. Four nearby methods have deliberately different expressions: `request_method`, `request_method_symbol`, method and `method_symbol`. The actual baseline saw partial body ranges, and a later lexical-metadata arm supplied their enclosing names. That arm still assigned the original-method header lookup to `request_method`. Correct structural ownership information did not make the resulting explanation faithful to its selected body.

This correction expands the evidence to include method headers, the lookup-table construction and `check_method`. The package identity is the installed actionpack 8.1.4 dependency plus the exact source checksum. It is not an application Git revision. The source-inspection experiment did not invoke these request methods or start a Rails server; ordinary framework use by authorized backend tests is a separate activity.

## The application-visible method delegates through super

The `request_method` body is `@request_method ||= check_method(super)`. When the stored value is truthy, that expression reuses it. Otherwise, it evaluates the shown super delegation and validation call before assigning the result. The selected body does not directly read `rack.methodoverride.original_method` or `REQUEST_METHOD`. Attributing that explicit two-key lookup to this method transfers code from a sibling method.

The nearby comment describes the application-visible, potentially overridden method. The body itself delegates upstream for its input. Without the ancestor implementation and actual receiver dispatch, this inspection does not establish which upstream method supplies the value or whether an override has occurred. The memoization expression also does not prove exactly one evaluation for every possible stored value: false and nil do not satisfy its truthy-cache path.

## The original-method path also has a reflective fallback

The method declaration accepts `*args`. Its zero-argument branch is guarded by `args.empty?` and memoizes a `check_method` call in `@method`. Inside that call, the first expression is `get_header("rack.methodoverride.original_method")`, with `get_header("REQUEST_METHOD")` selected by the written || fallback. This is a truthiness choice between returned values, not an explicit key-presence test. An empty String is truthy in ordinary Ruby and therefore does not automatically select the second operand.

When arguments are present, this body reaches bare super instead. The source comment associates that path with `Object#method` for debugging, but the actual next implementation depends on the runtime ancestor chain. It is safer to preserve the written delegation than to promise a particular reflective result for every receiver. These source keys belong to request-environment access; their names alone do not establish literal network headers. The four selected bodies also do not demonstrate automatic cache invalidation after arbitrary environment changes.

## Symbol lookups preserve their chosen getter

The body of `request_method_symbol` evaluates `HTTP_METHOD_LOOKUP[request_method]`. The body of `method_symbol` evaluates `HTTP_METHOD_LOOKUP[method]`. Swapping those expressions in Portuguese is not an equivalent translation: each lookup obtains its key through a different written method call. Neither symbol method has its own ||= assignment in the shown body, although the underlying getters have their separate memoized fields.

The supplied table-building code iterates `HTTP_METHODS`, lowercases each listed method String, replaces hyphens with underscores and converts the result to a symbol before assigning it under the original String key. That explains the written representation mapping. It does not establish an immutable global table or prove that arbitrary runtime receivers cannot override the participating operations.

## Validation returns the input name rather than the mapped symbol

The helper `check_method` receives name. For a truthy input, it evaluates `HTTP_METHOD_LOOKUP[name] || raise(ActionController::UnknownHttpMethod, ...)`. After that conditional, the final expression is name. Therefore the shown successful validation path returns its input name; it does not return the lookup symbol merely because that lookup was used as a test. Falsy input bypasses that conditional and reaches the same final expression.

This distinction connects the getters and symbol wrappers without merging their responsibilities. The original partial baseline omitted these helper and table details, while its Portuguese response also substituted one getter for the other. The corrected EN/PT chapter records the separate bodies, truthiness guards, return expression and unresolved runtime boundaries. It remains an experimental reviewed candidate, with no production metadata integration, neural training or automatic gold approval.

