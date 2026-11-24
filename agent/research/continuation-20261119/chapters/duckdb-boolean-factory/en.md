# Boolean factory and constructor have different roles

Codex-authored correction reviewed against pinned source; pending owner approval.

Repository: duckdb; revision: e41515de6f7efb19b43293ab49cb967cd64ab9f9; baseline: duckdb-boolean-factory. [Exact source excerpts](source-excerpts.json).

## Read the declaration before naming the role

The actual local-agent baseline called `Value::BOOLEAN` a constructor. The selected definition instead begins `Value Value::BOOLEAN(bool value)`: it has an explicit `Value` result type and an explicit return of a local result. Those details identify a factory function in the selected evidence. A constructor has a different declaration shape. This distinction matters because conflating the two hides the sequence of initialization followed by mutation.

The source packet includes the LogicalType constructor and the Boolean factory as separate excerpts from the same pinned file. The chapter does not infer whether the factory is static from its out-of-class definition alone. No declaration header was added to the evidence for that claim. It also does not claim a SQL query was parsed or evaluated: no DuckDB application was compiled or executed here.

## The constructor establishes an intermediate state

The selected constructor is `Value::Value(LogicalType type)`. Its initializer list initializes `type_` with `std::move(type)` and `is_null` with true. This records the written initialization of those members. It does not show every representation invariant of `Value` or establish that every constructor in the class initializes a Boolean payload. Nearby overloads have their own bodies and must not be silently merged into this one.

The factory starts its local result with `Value result(LogicalType::BOOLEAN)`. Under the shown constructor contract, the requested logical type and the initial null flag are distinct pieces of state. The true null flag at construction is an intermediate state in this factory's execution. Reporting that flag as the final result of the factory would stop the trace before its next two assignments.

## Payload, null flag and returned object

The next statement is `result.value_.boolean = value`. It stores the supplied bool in the Boolean member of the local object's payload. The following statement sets `result.is_null = false`. The source therefore writes the payload and the null marker separately. It does not derive the null marker from whether the input is true or false: both ordinary bool inputs reach the same false null-marker assignment.

The last statement is `return result`. The declared result is a `Value` object, rather than a bare bool, a pointer or the intermediate null marker. The selected code does not demonstrate dynamic conversion from an arbitrary string, integer or SQL expression. Any conversion before the bool parameter is supplied belongs to other evidence. It would also be incorrect to interpret the returned object's false null marker as a false Boolean payload.

## A correction with a deliberately narrow scope

For a conceptual true input, the shown payload assignment stores true and the null-marker assignment stores false. For a conceptual false input, the payload becomes false while the null marker again becomes false. These are source-derived traces, not observed runtime tests. They explain why value and nullness need separate sentences in a useful contract.

No optimizer behavior, allocation cost, exception guarantee or copy-elision performance was measured. The evidence supports the sequence written in these excerpts, not a universal account of DuckDB values. The baseline's correct observations about storing the input and changing nullness are retained, while its declaration-role error is corrected. The bilingual chapters remain source-reviewed candidates pending owner approval; neither becomes training gold simply because its structure and code-span parity were checked.

