# SQLX: named binding before query execution

This chapter covers selected public source from `jmoiron/sqlx` at revision `41dac167fdad5e3fd81d66cafba0951dc6823a30`. The topic is ad-hoc named binding, mapper/placeholder dependencies and the direct execution wrappers. Prepared-statement lifecycle, result scanning, transactions and concrete driver behavior are outside this scope. The module declares `github.com/jmoiron/sqlx` and a Go 1.10 directive in `go.mod`; that directive is not evidence of an installed compiler or runtime. The family has sixteen historical development records, so this is not an independent-family evaluation.

The pinned MIT notice in `LICENSE` is retained. This manually authored research candidate is isolated from the active catalog, is not an owner-approved training target, and does not authorize publication or training. No database, credentials or private application records were accessed.

## Public entry points and the execution boundary

Package `Named` calls `bindNamedMapper` using `QUESTION` and the package mapper (`named.go:417-435`). It returns a query string, positional arguments and an error; it has no database handle from which to select a driver format. Package `BindNamed` accepts an explicit binding type and is marked deprecated in the selected source. The similarly named `DB.BindNamed` method instead uses the database object's driver name and mapper (`sqlx.go:300-303`). These entry points must not be conflated.

The `DB.NamedExec` and `DB.NamedQuery` convenience methods forward to the package wrappers (`sqlx.go:305-315`). Those wrappers use `BindType(e.DriverName())` and `mapperFor(e)`, return a binding error before their selected executor call, then delegate to `e.Exec` or `e.Queryx` (`named.go:441-458`). They are execution APIs, not merely formatting helpers. The `Ext` interface composes binding, querying and execution capabilities (`sqlx.go:89-101`); this source does not determine the concrete driver's effects or results.

This is a statement about explicit calls in the selected library path, not a global absence-of-I/O or purity guarantee. Custom interface methods and mapping callbacks remain separate behavioral boundaries.

## Driver format and named compilation

The binding registry starts with driver defaults and can be changed through `BindDriver`; an unregistered driver name yields `UNKNOWN` (`bind.go:15-54`). In the selected named compiler, that unknown case uses the question-mark form, rather than proving a driver is supported or rejecting every unregistered name. The public package binding helper also deliberately selects that form. A database-specific wrapper selects from the registry, but valid execution still depends on its driver and query.

The compiler walks bytes, collects each parameter-name occurrence in order and emits a placeholder according to the selected binding type (`named.go:331-405`). Repeated occurrences are not deduplicated. There are special paths for doubled colons and colon-equals, but this is not a complete SQL lexer or validator. The selected comments warn about byte-wise Unicode handling. The separate `Rebind` routine searches for question marks and rewrites them for selected formats; its selected comments also note escaping limitations (`bind.go:56-89`). Neither helper establishes the semantics of arbitrary quoted strings, comments or SQL statements.

## Argument shape, field lookup and errors

The dispatcher distinguishes convertible string-keyed maps, arrays/slices and the default struct-binding path (`named.go:152-168,421-435`). A string-keyed map still must be convertible to the expected map representation. A conversion failure has a returned error; this does not mean every other unsupported or nil input is uniformly guarded.

Map binding looks up values in compiled-name order. It appends each occurrence, including repeats, and returns an error when a name is absent (`named.go:197-207`). The low-level map helper can return the arguments collected before that missing name. The map-binding wrapper returns the compiled query, that list and its error; the struct-binding wrapper instead discards its query/list on a returned lookup error (`named.go:213-225,304-312`). A nonempty result component must not be mistaken for successful binding when an error is present. Selected missing-name errors format the supplied argument value; this chapter records only source behavior and uses invented data.

Struct binding dereferences pointers, obtains mapper traversals and reads the corresponding fields (`named.go:173-194`). The selected reflection traversal requires a struct and can panic through `mustBe`; the read-only field helper does not allocate nil nested pointers (`reflectx/reflect.go:181-200,223-227,246-250`). This chapter does not promise that all invalid inputs return an ordinary error or enumerate every reflection failure.

## Mapper state and callbacks

The default package mapper uses lowercase field names and the `db` tag. Mapper configuration can differ, and `mapperFor` uses the selected database/transaction mapper when the argument is a supported concrete database or transaction type; other types take the package mapper path (`sqlx.go:22-49,146-159`). Mapping configuration is therefore a dependency, not a fixed property of every caller.

Preparation uses mutable cached mappings and locks. The selected `TypeMap` looks up its cache, may call `getMapping`, and stores the mapping (`reflectx/reflect.go:104-113`). Mapping can invoke configured callbacks. In particular, `parseName` calls the field-name mapper before inspecting the tag (`reflectx/reflect.go:282-319`); a field tag alone does not prove that callback is bypassed. This explains why “does not explicitly call a database executor” is a narrower statement than “globally side-effect-free.”

The cache method's unlock is written after mapping, rather than deferred. No recovered-callback-panic or lock-recovery guarantee is claimed here. The campaign did not run a fault observation on the original method. Callback behavior, concurrent configuration changes and complete cache synchronization remain outside this selected runtime proof.

## Array rewriting and context forwarding

Array/slice binding first compiles question-mark placeholders, rejects length zero, obtains arguments for each element and flattens those lists (`named.go:273-300`). For multiple elements it attempts to repeat a matching parenthesized values fragment, then rebinds if needed. The fragment matcher and bracket counter can leave the SQL unchanged when the selected pattern or closing bracket is not found (`named.go:227-268`). This is conditional text rewriting, not a guarantee that every array/query combination produces valid SQL or a successful bulk operation.

The context variants perform binding before calling `e.QueryxContext` or `e.ExecContext` with the context (`named_context.go:116-133`). Their `ExtContext` dependency combines the binding and context-aware executor interfaces (`sqlx_context.go:26-48`). No context check is shown inside this binding path. Forwarding a context does not prove that cancellation prevents all preceding binding work, or establish the concrete driver's cancellation timing.

## Invented binding-only example

This fragment uses a generic invented record and calls the package binding API if its function is invoked. It does not pass a database handle or call an executor. The campaign syntax-checked the fragment but did not invoke it, resolve its imports, type-check it or observe a binding result. Custom mapper behavior is not tested by this example.

```go
package examples

import "github.com/jmoiron/sqlx"

func BindWidget() (string, []interface{}, error) {
    return sqlx.Named("SELECT code FROM widgets WHERE id=:id", map[string]interface{}{"id": 7})
}
```

The exact fragment is preserved with the native Go syntax receipt. The producer identifies Go 1.27.4 and explicitly reports syntax-only analysis with no source execution; it is not evidence that a matching compiler was installed. A host PATH lookup found no Go compiler. No installation or upstream build was attempted.

## Written tests and observation limits

The selected `TestCompileQuery` table contains placeholder and occurrence-order expectations, and `TestFixBounds` contains values-fragment rewriting cases in `named_test.go`. The Unicode case at lines 56-65 is commented out. `TestEscapedColons` explicitly skips at line 125. Describing those cases as active passing coverage would be false. The file also contains database-oriented named-query tests; none of them ran in this campaign.

The campaign used the existing stateless native parser for 37 selected declarations across the dependency files. That validates bounded syntax/selection and preserves source quotations, not package typing, SQL validity, callback effects or database behavior. No SQLX installation, original program import/execution, database connection/query/migration or upstream test suite occurred.

## FAQ

**Does package binding automatically choose my driver's placeholders?** No. It selects the question-mark form; the database-specific binding method uses the object's driver registration and mapper.

**Does the execution wrapper only prepare a query?** No. After successful binding, the selected wrapper calls its executor. A binding error returns before that explicit call; arbitrary custom callbacks and interfaces are not globally characterized.

**Are all bad argument shapes ordinary returned errors?** No. Some selected paths return binding errors, while reflection paths can panic. Nil and unsupported shapes are not covered by a universal safe-error contract.

**Does a field tag avoid the custom name callback?** Not by itself. The selected name parser invokes that callback before tag handling.

**Does any nonempty array become a valid bulk query?** No. Argument flattening and conditional values-fragment rewriting do not validate arbitrary SQL or establish driver acceptance.

**Does a cancelled context necessarily avoid all binding work?** No such guarantee follows here. The selected wrappers bind first and pass the context to the subsequent executor call; driver and callback behavior require more evidence.

## Preservation and status

The actual source snapshots, existing comments/tests, native receipts and both complete language files are retained. No active documentation, permanent tests, application schema or external repository was changed. Complete source/bilingual review is required before readiness for owner review. Owner approval, training gold, neural learning, independent-family generalization and full application integration are not inferred from this candidate.
