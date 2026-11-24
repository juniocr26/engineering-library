# Optional Go syntax tool

This owned tool parses source text with Go's standard parser. It never resolves
imports, compiles the inspected project, or executes its code. The parser accepts
some forms beyond the Go language specification. Syntax output is not type or
runtime verification.

`manifest.json` records the source, BSD license, compiler image, build flags and
three executable hashes. The Python launcher verifies those inputs before choosing
a native binary. Its timeout is 15 seconds. Windows has no packaged native binary;
Linux AMD64 was validated through Docker emulation on an ARM64 host.

Version 1.1 added bounded sole-return syntax metadata. It records expression text
and returned function-literal signatures. Additional statements and unsupported
or oversized expressions yield no return contract. A returned callback can remain
explicitly unanalyzed. These records do not establish helper behavior or successful
execution. The source-fact renderer is a separate opt-in consumer.

Version 1.2 also selects complete standalone `type` declarations, including
structs, interfaces, aliases and generic constraints. Grouped `type (...)`
declarations remain unsupported. Type units add explicit context; they do not
resolve imports or type relationships. The sole-return fact profile refuses them.

## Rebuild and preserve

The cached compiler was `golang:1.27.4-alpine`, pinned by the image digest in the
manifest. A local export and its build cache are preserved in the private
`adaptive-20261118/go-ast-tool` campaign archive; they were never uploaded.
Builds used no network, a read-only container root, 2 CPU/2 GiB limits, source
mounted read-only, and separate writable output/cache directories.

For each target, the build environment was `CGO_ENABLED=0`, `GOTOOLCHAIN=local`,
`GO111MODULE=off`, `GOWORK=off`, and the appropriate `GOOS`/`GOARCH`. The command was
`gofmt /src/main.go > /out/main.formatted.go`, followed by
`go build -trimpath -buildvcs=false -o <new-output> /out/main.formatted.go`.
The readable formatted compiler-input bytes are retained as `main.go`. Targets were
`linux/arm64`, `linux/amd64` and `darwin/arm64`. No third-party packages are used.
Keep the compiler image, cache and previous binaries until a new release passes
source, checksum, parser-control and actual-consumer checks.

Install new executables through a new temporary file on the same filesystem,
verify its hash and mode, then atomically rename it into place. Do not truncate a
previously executed Mach-O file in place. In the campaign, identical validly signed
bytes executed from new files but received signal 9 at an overwritten old inode;
atomic replacement restored native tests. No signatures or OS protections were
changed. Refresh the tool manifest and recovery lock only after validation.
Local checksums provide consistency with owner-reviewed files, not external signing.


Version 1.3.0 also emits an optional `deferred_return_contract` for the exact
call/defer/return statement shape. This field is independent of the existing
`return_contract`; unsupported shapes receive no deferred contract. Matching
method spellings do not resolve a mutex type or prove concurrency safety.
The [Go specification](https://go.dev/ref/spec#Defer_statements) distinguishes
evaluation of a deferred call's operands from its postponed invocation.
The optional source-fact consumer records source syntax, never an execution
trace or guaranteed successful unlocking.

## Version 1.5.0 — bounded handler defer scope

The optional `handler_defer_contract` records one exact wrapper layout: a local
callback binding followed by its `http.HandlerFunc` return, with an argument-free
literal defer followed by `next.ServeHTTP(w, r)` in the same callback. Extra
statements, immediate inner scopes, deferred argument effects and computed call
arguments receive no such proof. The deferred body, imported types, helper
semantics and runtime completion remain unverified.

The existing Go AST Ruby consumer uses this proof to refuse the observed positive
EN/PT sentence that claims panic handling occurs before the next function is
called. It preserves negated descriptions and quoted source text. This is a narrow
refusal, not general natural-language control-flow validation. Native macOS ARM64
and Linux ARM64 each passed 31 parser/launcher tests; seven parser test methods and
a probe ran through existing AMD64 emulation. Windows was not tested.

For byte-exact reconstruction, use the exact compiler-input directory and basename
in the current manifest: `/work/go-handler-defer-v1/main.formatted.go`. The older
rebuild example above is historical. With `GO111MODULE=off`, Go 1.27.4 includes the
command-line package's local prefix in its action identity even with `-trimpath`.
A controlled relocation changed only Go build-ID data and associated Mach-O
signing bytes; rebuilding at the recorded historical path reproduced all three
original hashes. Do not patch binary headers to disguise this distinction.

The continuation preserves the cached compiler image and an extracted Linux
toolchain privately. It ran the compiler in the existing backend, with private
cache/output paths, `GOENV=off`, `GOTOOLCHAIN=local`, module downloads disabled,
`CGO_ENABLED=0`, `GOMAXPROCS=2`, `GOMEMLIMIT=512MiB`, and `go build -p 1 -trimpath
-buildvcs=false`. No new container or host-wide compiler installation was needed.


## Ordered guard-chain syntax — producer 1.6.1

An optional field records exactly two or three initializer-free if-return
statements followed by a final explicit return. Each guard has one return,
no else and no extra statement. Conditions, expressions, physical lines and
order are retained. Names, types, helpers and runtime completion remain unresolved.
The existing explicit Go if-return command renders this shape using profile v2;
the earlier one-guard paragraph remains unchanged.

Real Go Image Optimizer quality and SQLx scannability contracts produced
source-only drafts followed by no-ops. The first candidate's guard lines
incorrectly honored logical line directives; the failure is preserved and
1.6.1 uses physical positions. All 34 producer controls passed on native macOS
ARM64, Linux ARM64 and emulated Linux AMD64. The full Ruby suite passed
249 tests / 1,652 assertions. All three binaries were independently rebuilt
byte for byte with a fresh cache and the exact source path. See the
[integration receipt](../../research/continuation-20261119/go-ordered-guard-chain-integration.json).
