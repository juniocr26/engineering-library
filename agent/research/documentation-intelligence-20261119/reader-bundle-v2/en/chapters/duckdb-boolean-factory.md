# Boolean factory and constructor have different roles

Codex-authored correction reviewed against pinned source; pending owner approval.

Repository: duckdb; revision: e41515de6f7efb19b43293ab49cb967cd64ab9f9; baseline: duckdb-boolean-factory. [Exact source excerpts](../references/ref-b0f5f20a13f3fa739199.md).

## Read the declaration before naming the role

The actual local-agent baseline called `Value::BOOLEAN` a constructor. The selected definition instead begins `Value Value::BOOLEAN(bool value)`: it has an explicit `Value` result type and an explicit return of a local result. Those details identify a factory function in the selected evidence. A constructor has a different declaration shape. This distinction matters because conflating the two hides the sequence of initialization followed by mutation.

The source packet includes the `Value(LogicalType)` constructor and the Boolean factory as separate excerpts from the same pinned file. The original selected packet did not establish whether the factory was static from its out-of-class definition alone. This campaign adds the matching declaration header, which explicitly declares the factory static. It also does not claim a SQL query was parsed or evaluated: no DuckDB application was compiled or executed here.

## The constructor establishes an intermediate state

The selected constructor is `Value::Value(LogicalType type)`. Its initializer list initializes `type_` with `std::move(type)` and `is_null` with true. This records the written initialization of those members. It does not show every representation invariant of `Value` or establish that every constructor in the class initializes a Boolean payload. Nearby overloads have their own bodies and must not be silently merged into this one.

The factory starts its local result with `Value result(LogicalType::BOOLEAN)`. Under the shown constructor contract, the requested logical type and the initial null flag are distinct pieces of state. The true null flag at construction is an intermediate state in this factory's execution. Reporting that flag as the final result of the factory would stop the trace before its next two assignments.

## Payload, null flag and returned object

The next statement is `result.value_.boolean = value`. It stores the supplied bool in the Boolean member of the local object's payload. The following statement sets `result.is_null = false`. The source therefore writes the payload and the null marker separately. It does not derive the null marker from whether the input is true or false: both ordinary bool inputs reach the same false null-marker assignment.

The last statement is `return result`. The declared result is a `Value` object, rather than a bare bool, a pointer or the intermediate null marker. The selected code does not demonstrate dynamic conversion from an arbitrary string, integer or SQL expression. Any conversion before the bool parameter is supplied belongs to other evidence. It would also be incorrect to interpret the returned object's false null marker as a false Boolean payload.

## A correction with a deliberately narrow scope

For a conceptual true input, the shown payload assignment stores true and the null-marker assignment stores false. For a conceptual false input, the payload becomes false while the null marker again becomes false. These are source-derived traces, not observed runtime tests. They explain why value and nullness need separate sentences in a useful contract.

No optimizer behavior, allocation cost, exception guarantee or copy-elision performance was measured. The evidence supports the sequence written in these excerpts, not a universal account of DuckDB values. The baseline's correct observations about storing the input and changing nullness are retained, while its declaration-role error is corrected. The bilingual chapters remain source-reviewed candidates pending owner approval; neither becomes training gold simply because its structure and code-span parity were checked.

## Engineer FAQ and the declaration boundary

<!-- reading-section: faq:static-factory-identity -->
### Is BOOLEAN a constructor or a static factory?

The added public header declares `DUCKDB_API static Value BOOLEAN(bool value);`. This establishes the static factory declaration at the frozen revision. The constructor is separately declared with a logical-type argument. The definition and declaration now support different roles without guessing from the uppercase name.

<!-- reading-section: faq:false-versus-null -->
### Does a false payload mean SQL null?

The payload and null flag are different written members. Both ordinary bool input paths assign `result.is_null = false`. A false payload therefore does not make that assignment a null result.

<!-- reading-section: faq:no-query-pipeline-proof -->
### Does this source demonstrate a query or conversion pipeline?

It shows construction, two assignments and return of a local Value. It does not parse SQL, execute a database statement or prove conversion, allocation, performance or exception guarantees for arbitrary inputs.

| Conceptual bool input | Written payload assignment | Written final null flag |
| --- | --- | --- |
| true | true | false |
| false | false | false |

These table rows are source-derived traces, not observed DuckDB executions. The additional type header declares the Boolean logical-type identifier and the logical-type conversion constructor; full build and overload verification remain outside this review.
