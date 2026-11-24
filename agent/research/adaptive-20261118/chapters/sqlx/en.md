# SQLx: wrappers, errors and data destinations

Experimental chapter authored by Codex after source review. This is a correction draft, not unchanged local-model output. Human factual and bilingual approval is pending; it is not a positive training answer.

Source revision: `41dac167fdad5e3fd81d66cafba0951dc6823a30`.

## 1. A wrapper is different from a connection check

The `DB` declaration embeds `*sql.DB` and adds `driverName string`, `unsafe bool` and `Mapper *reflectx.Mapper`. This is the written structure of the wrapper. These fields describe an embedded handle and auxiliary state; a successful network connection requires separate evidence. [sqlx.go:243–248](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L243-L248)

`NewDb` accepts an existing `db *sql.DB` and a `driverName string`. Its return expression builds `&DB{DB: db, driverName: driverName, Mapper: mapper()}`. The supplied body contains no explicit query rewriting or connection check. The behavior of `mapper()` needs its own source. [sqlx.go:254–256](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L254-L256)

`Open` declares `(*DB, error)` and first calls `sql.Open(driverName, dataSourceName)`. A non-nil error returns `nil, err`. Otherwise it constructs the wrapper with the returned handle and `mapper()`, returning that wrapper together with `err`. This wrapper contains no explicit ping; the called library and driver behavior are outside this excerpt. [sqlx.go:264–270](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L264-L270)

`MustOpen` declares only `*DB`. It calls `Open`, executes `panic(err)` when the returned error is non-nil, and otherwise returns `db`. Its signature is not a two-result error-returning API. [sqlx.go:273–279](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L273-L279)

## 2. Connection checking and cleanup

`Connect` calls `Open(driverName, dataSourceName)` and immediately returns `nil, err` if opening reports an error. It then assigns the result of `db.Ping()` to `err`. A ping error leads to `db.Close()` before `nil, err`; the close result is not checked here. The remaining return is `db, nil`. No particular database vendor is selected by this body. [sqlx.go:640–651](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L640-L651)

`MustConnect` declares `*DB`, calls `Connect`, panics on its non-nil error and returns the handle otherwise. It does not add an error result to its own signature. The panic policy is the visible difference from the two-result wrapper. [sqlx.go:654–660](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L654-L660)

## 3. Query helpers return status and write through destinations

`Preparex` calls `p.Prepare(query)`. An error returns `nil, err`; the other path builds `&Stmt{Stmt: s, unsafe: isUnsafe(p), Mapper: mapperFor(p)}` and returns it with `err`. The supplied definition names preparation and wrapper construction, not row scanning or query execution. The two helper calls need separate evidence for their internal behavior. [sqlx.go:663–669](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L663-L669)

`Select` declares an `error` result. It calls `q.Queryx(query, args...)`, returns an opening error immediately, then registers `defer rows.Close()`. Its final expression is `scanAll(rows, dest, false)`. Results are passed toward `dest`; this signature does not return a result slice. The scanning helper implementation is not included here. [sqlx.go:676–684](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L676-L684)

`Get` also declares `error`. It assigns `q.QueryRowx(query, args...)` to `r` and returns `r.scanAny(dest, false)`. The body supplies a destination to a helper; it does not return a row value, prove uniqueness of database data or expose the helper implementation. [sqlx.go:691–694](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L691-L694)

## 4. File execution has distinct failure boundaries

`LoadFile` declares `(*sql.Result, error)`. It calls `filepath.Abs(path)` and then `ioutil.ReadFile(realpath)`; either error returns `nil, err` before execution. It supplies `string(contents)` to `e.Exec` once, with no additional arguments in this call, and returns `&res, err` even when that execution reports an error. This code contains no SQL statement-splitting loop. Parsing or execution of multiple statements depends on the invoked implementation. [sqlx.go:707–718](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L707-L718)

`MustExec` passes `query, args...` to `e.Exec`. It executes `panic(err)` for a non-nil error and otherwise returns `res`, whose declared type is `sql.Result`. This contract belongs to this definition; it must not be attributed to the file loader citation. [sqlx.go:722–728](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L722-L728)

## 5. Scanning separates allocation, helper calls and dereferencing

`SliceScan` first asks for `r.Columns()`. That error path returns `[]interface{}{}` with the error. It allocates a `values` slice sized by the column count and fills its entries with `new(interface{})` before calling `r.Scan(values...)`. A scan error returns the current container before this function runs its explicit dereference loop. On the remaining path it replaces each entry with the pointed-to value and returns `values, r.Err()`. The scan call is assigned to `err`; it does not itself return the result slice. [sqlx.go:805–828](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L805-L828)

`MapScan` obtains column names, allocates pointer destinations and calls `r.Scan(values...)`, returning either earlier error before its assignment loop. The loop writes `dest[column] = *(values[i].(*interface{}))` in column order, then the function returns `r.Err()`. Repeated column names assign the same map key again; this loop contains no duplicate-name rejection. It also does not initialize the caller map or check that it is writable. [sqlx.go:837–859](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L837-L859)

## 6. Reflection helpers expose a bounded contract

`baseType` assigns `reflectx.Deref(t)` back to `t` and compares `t.Kind()` with `expected`. A mismatch returns `nil` and a formatted error; the other return is `t, nil`. The dereferencing helper is called, not defined, in this excerpt. There is no local nil-input or helper-panic recovery. [sqlx.go:1012–1018](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L1012-L1018)

`fieldsByTraversal` applies `reflect.Indirect(v)` and rejects a non-struct kind with `argument not a struct`. For an empty traversal it stores `new(interface{})` and continues. Otherwise it obtains `f` through `reflectx.FieldByIndexes(v, traversal)` and stores `f.Addr().Interface()` when `ptrs` is true or `f.Interface()` otherwise. It returns `nil` after the loop. Destination slice length, addressability and helper behavior are not validated by these explicit guards. [sqlx.go:1026–1045](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L1026-L1045)

`missingFields` scans `transversals` in input order. Its first entry with `len(t) == 0` returns that index and `missing field`; completing the loop returns `0, nil`. A zero index accompanied by a nil error is the visible success form, not evidence of a missing first field. No uniqueness property is checked. [sqlx.go:1047–1054](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/sqlx.go#L1047-L1054)

## Evidence and limits

The cited definitions were inspected statically. No upstream application, database, server or test suite was executed to establish runtime behavior. External helpers need their own source and assumptions. These chapters expand and correct research drafts; they have not been placed in the public catalog. Source licenses and exact quotations/hashes are retained in the campaign evidence.

Source project license: [LICENSE](https://github.com/jmoiron/sqlx/blob/41dac167fdad5e3fd81d66cafba0951dc6823a30/LICENSE). The exact license text and its checksum are retained with the source evidence.
