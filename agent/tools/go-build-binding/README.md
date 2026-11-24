# Optional Go build-filtered binding experiment

Version 0.1.0 is a bounded lexical experiment for bare calls to Go's predeclared
`min` and `max`. It does not replace the existing Go AST producer or change the
Ruby agent's default source selection.

The operator supplies a complete frozen census of immediate Go files in the
selected module package and any registered packages needed to identify
unaliased imports in the selected file. Each file and the module declaration
carry SHA-256 hashes. Request paths identify virtual source data; they are never
host filesystem paths. No inspected source is imported, compiled or executed.

The producer uses the official `go/build` file selection rules through a virtual
filesystem. Every filesystem callback is supplied. The module fallback that
could invoke a host `go` command is disabled by that configuration. A poisoned
PATH regression checks this boundary. CGO is disabled; supported targets are
Darwin/arm64 and Linux/arm64. The producer records compiler release and tool tags.

`LEXICALLY_UNSHADOWED_UNDER_PROFILE` means the supplied build-filtered package
declares no queried name, the selected function has no admitted local/signature
obstruction, and named imports do not introduce that name. Unaliased imports use
their actual declared package names, never path basenames. This remains
conditional on a complete supplied census and valid package compilation.

It does not prove a complete module graph, replacements, workspaces, vendor
selection, successful type checking, numeric operand validity, helper semantics,
runtime bindings or observed operation results. Unsupported or ambiguous source
returns `INCONCLUSIVE`. Malformed requests return `REFUSED` with exit code 2.
No result authorizes publication, commits or training.

## Reproduction

Run from the Engineering Library repository root. Pick the executable matching
the host; compare its SHA-256 with `manifest.json` before use. The input must be
a previously frozen UTF-8 JSON request, not a model-selected command.

```sh
agent/tools/go-build-binding/bin/go-build-binding-darwin-arm64 \
  < .local-backups/documentation-intelligence-20261119/go-build-binding-v1/sdk-darwin-request.json
```

That command was executed during the campaign. It reads a private local snapshot
of public SDK/toolchain sources. The snapshot is preserved but is not assumed to
exist in a fresh public checkout. The public census receipt records individual
source hashes, revisions and snapshot locations. It is not the source archive.

`documentation_go_binding.GoBindingObserver` adds an operator-pinned executable,
an explicit deadline, exact request/response identity checks and complete quote
and source-census validation. It is an opt-in Python API. It has no automatic
binary discovery, shell execution, model request routing or persistent cache.
All packet contents remain source data without instruction authority.

The native request limits are 16 MiB input, eight packages, 512 Go files per
package, 256 KiB per source file and a 6,144-byte complete selected function.
Output is limited to 1 MiB. The wrapper defaults to a 20-second deadline and
does not retry a failed or timed-out invocation. Requests are strict closed
objects; duplicate keys, unknown or incorrectly cased fields, null values,
invalid UTF-8 and lossy surrogate escapes are refused.

Both shipped executables were built offline with the preserved Go 1.27.4
toolchain, CGO disabled, `-trimpath` and `-buildvcs=false`. `GO-LICENSE` preserves
the Go runtime redistribution notice. The manifest pins source, tests and native
executables. No toolchain download or Git operation is needed to invoke them.

The SDK result is a development-exposed research case. Synthetic binding and
refusal controls are regression controls, not an independently certified holdout.
