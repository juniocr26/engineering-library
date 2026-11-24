# DuckDB C API: result ownership and error boundaries

Source-scoped development candidate, not owner approved. The pinned public revision is `e41515de6f7efb19b43293ab49cb967cd64ab9f9` under the retained MIT notice. This chapter concerns the selected v1 C API header and C++ implementation, not the v2 surface or a complete database execution. The family already appears in eight historical dataset records and is not an independent holdout. No query, database, upstream test or example program was executed.

## The boundary and its state

The public header declares the C-facing functions and wraps declarations in `extern "C"` when included from C++. Its default API-version macros select 1.5.6; these are the inspected header's target macros, not a verified installed-library or released-version claim. `duckdb_result` contains deprecated metadata fields and an `internal_data` pointer; callers are directed to destroy a result with `duckdb_destroy_result`. [H1,H2]

The selected query wrapper casts the connection to `Connection *`, calls `conn->Query(query)` inside a try block, and moves the returned object into `DuckDBTranslateResult`. Its catch-all branch returns `DuckDBError`. That branch itself neither initializes the caller's output nor assigns an error message. The selected code does not establish safe use of arbitrary invalid connections or query pointers. [Q1]

`DuckDBTranslateResult` assumes a usable result object: it dereferences the incoming pointer before its written assertion. If `out` is null, the branch returns status from `result.HasError()` without creating a C output object. Otherwise it zeroes the output, allocates `DuckDBResultData`, moves the result into it, sets the result-set marker and stores its pointer in `out->internal_data`. An error result then supplies `deprecated_error_message` from the result's string and returns `DuckDBError`; the normal path records column metadata and returns `DuckDBSuccess`. This is written order, not a general allocation-failure or callback guarantee. [R1]

The internal declaration holds `result` and `stream` as `unique_ptr` members. `HasError()`, `GetError()` and `GetErrorType()` delegate to the stream when present, otherwise to the result. This connects the opaque C field to the selected C++ state owner; it does not prove every streaming transition or destructor side effect. [I1]

## Error messages and cleanup

The public query contract requires `duckdb_destroy_result` for the result object even on query failure, because stored error information also needs cleanup. That nominal result-object obligation must not be expanded into a promise that every arbitrary exception has populated every output byte. The translated-error branch and generic catch branch are different evidence. [H3,Q1,R1]

`duckdb_result_error` returns `nullptr` when its result pointer or `internal_data` is null. With internal data it returns no message when `HasError()` is false, otherwise the `c_str()` obtained through `GetError()`. The header explicitly says this returned message must not be freed separately and is cleaned up with the result. Treat it as borrowed and do not retain it as owned storage after destruction. `duckdb_result_error_type` has its own null/no-error guards returning `DUCKDB_ERROR_INVALID`. These guards do not establish universal null safety for other API functions. [H4,R3,I1]

The selected `duckdb_destroy_result` first accesses result fields without a null-result guard. It destroys deprecated column storage if present, deletes the object behind `internal_data` if present, then zeroes the result struct. Passing a null result pointer is therefore not a supported safety conclusion from this code. Zeroing the struct does not preserve the lifetime of previously borrowed pointers. The public header also documents streaming cancellation/transaction effects, but those wider effects are not verified by this selected implementation review. [R2,H5]

## An owned C usage fragment

This fragment assumes an already valid connection and query string. It zero-initializes its result, observes a borrowed message only before cleanup and returns the status; it does not create a connection, run a server or copy error text for later ownership.

```c
#include "duckdb.h"
duckdb_state query_with_cleanup(duckdb_connection connection, const char *query) {
    duckdb_result result = {0};
    duckdb_state state = duckdb_query(connection, query, &result);
    if (state == DuckDBError) {
        const char *borrowed = duckdb_result_error(&result);
        (void)borrowed;
    }
    duckdb_destroy_result(&result);
    return state;
}
```

The actual fragment was checked with the existing Apple Clang 21.0.0 against the copied frozen public header using C11, `-fsyntax-only`, and explicit declaration/pointer diagnostics. It was not linked or run. This checks the selected type/declaration use on this host; it does not validate a database, invalid-pointer behavior, complete exception safety, binary compatibility or Windows/Linux builds. [E1]

Four owned compiler controls had the expected outcomes: the example passed; wrong pointer level and a translated identifier failed; a deliberately unsafe manual free of the borrowed error pointer still passed the compiler. That last control is rejected against the header ownership contract. Compiler acceptance cannot substitute for semantic source review. [E1,H4]

## Written tests and preservation

The selected basic C API test contains explicit null-result assertions for the error getter and error-type getter. The regression case named for issue #2058 executes invalid SQL in its written body, expects `DuckDBError`, and calls result cleanup. Its historical segmentation-fault wording is not evidence that the current source crashed during this campaign. Another selected test contains successful queries followed by cleanup and an error query with a null output pointer. These are inspected test statements; the database tests were not run. [T1,T2,T3]

No external documentation, source, test, schema or active catalog changed. This separately authored chapter does not replace, repair or rescore the rejected H32 neural FAQ. Historical snapshots and failed outputs remain preserved.

## FAQ

**Must a nominal failed query result still be destroyed?** The header says yes, including stored error cleanup. That does not prove the generic catch branch always initialized arbitrary output memory. [H3,Q1]

**Should the caller free the error-message pointer separately?** No. The message is borrowed under the header contract and cleaned up with the result; keep any use within the supported lifetime. [H4,R3]

**Does the null-safe error getter make null destruction safe?** No. The getter's guard and the destructor's initial field access are different code paths. [R2,R3]

**Does the catch-all guarantee a populated error message?** No. The selected branch only returns `DuckDBError`; it contains no output initialization or message assignment. [Q1]

**Does a successful compilation prove correct ownership?** No. The unsafe-free control compiled but contradicts the inspected borrowed-message contract. [E1,H4]

## Evidence and limits

All paths are relative to the pinned public repository. H1: `src/include/duckdb.h`, lines 14–20 and 68–85. H2: same header 832–845. H3: 6509–6525. H4: 6651–6663. H5: 6527–6543. Q1: `src/main/capi/v1/duckdb-c.cpp`, 194–202. R1: `src/main/capi/v1/result-c.cpp`, 350–376. R2: 494–506. R3: 611–627. I1: `src/include/duckdb/main/capi/capi_internal.hpp`, 102–151. T1: `test/api/capi/v1/test_capi.cpp`, 122–132. T2: 696–716. T3: 673–682. E1: isolated `duckdb-capi-owned-c-example-observation-v1.json` and its frozen protocol.

Exact source hashes and snapshots accompany this candidate. The C++ relationships were reviewed from source text; no full C++ build or general semantic parser result is claimed. Scope, platform and runtime limitations apply to the entire chapter. Source review, syntax acceptance and same-campaign bilingual review are not independent human approval, training gold or publication authorization.
