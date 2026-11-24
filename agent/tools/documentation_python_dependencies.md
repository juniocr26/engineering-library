# Closed Python dependency observer

`documentation_python_dependencies.ClosedDependencyObserver` is an optional
research API. Version 0.1.2 follows a small chain of zero-argument Python functions
through explicit imports in an operator-frozen flat registry. It never imports
or executes the inspected modules. Ordinary Ruby source selection is unchanged.

The admitted module contains only an optional leading docstring, explicit
absolute `from` imports and unique synchronous function declarations. Every
function has no arguments, annotations or decorators and returns either a
bounded integer literal or the result of a direct zero-argument call. All imports
must resolve inside the registry. Relative/star imports, module import cycles,
duplicate bindings, conditional bodies and dynamic expressions are refused.
The selected call chain must be acyclic and at most eight functions deep.

Ordinary single-underscore ASCII helpers and module names are admitted; hard
Python keywords and double-leading special names are refused. Import records
preserve exact physical lines, source identity and local/target alias mappings.
The explicit `entry_module` and `entry_symbol` identify the requested API even
when it is only an imported alias for a function declared in another module.

The result `STATIC_INTEGER_RETURN_UNDER_CLOSED_PROFILE` is conditional on the
supplied flat module and runtime binding assumptions. It does not prove actual
import search, `sys.modules`, import hooks, monkeypatching or runtime behavior.
It cannot describe a general adapter with parameters, classes or external effects.
Unsupported or insufficient evidence produces `INCONCLUSIVE`, preserving the
existing documentation. The observer never recommends `REMOVE` or writes docs.

The root is an absolute canonical directory supplied by the operator. The closed
registry has exactly `revision` and `modules`; each module has exactly `path`
and `sha256`. A module named `entry` must use `entry.py` directly below that root.
There is no search path, package discovery or network resolution. The caller must
compute and freeze hashes before observation; hashes supplied by model output
are not an authorization policy.

```python
from documentation_python_dependencies import ClosedDependencyObserver

# registry is an operator-reviewed JSON value bound to an existing source cut.
observer = ClosedDependencyObserver(absolute_registered_root, registry)
result = observer.observe("entry", "value")
```

This is an API sketch; the executable synthetic examples and exact registries are
retained under `.local-backups/documentation-intelligence-20261119/python-closed-dependencies-v1`.
No sketch variable is an environment variable or automatic root selection.

Successful results include exact physical function and import quotations, a call path, all
registered source hashes and two different keys. `evidence_key` binds the whole
registered registry, revision, entry selector, profile, extractor and workspace
implementation. A helper-only change invalidates it. Including unused registered
modules makes this deliberately conservative. `contract_key` represents only
the admitted integer-return fact; it is not a source identity, cache permission,
feature identity or approval token. Formatting can change evidence while leaving
that narrow contract unchanged. Profile versions participate in these keys; compare contract keys only within the same profile version, or compare the validated integer facts explicitly. No persistent cache is implemented here.

The parent verifies worker structure, graph bounds and quotations against physical
source. It rechecks every source and the root identity before exposing a result.
AST analysis runs in an existing Python subprocess with a maximum three-second
worker deadline. This is a trusted producer process, not a sandbox for executing
source. The parent performs no inspected AST parsing after that worker deadline.
The deadline does not bound total job filesystem time or cancel remote inference.

Limits are 16 modules, 65,536 bytes per module, 262,144 total source bytes, 4,096
AST nodes per module and 6,144 bytes per complete function/import quotation. At most 64 registered import aliases and 24,576 combined quotation bytes are admitted. All registered imports are witnessed; the function path covers the selected chain. These bounds can conservatively refuse a valid but larger source closure. Symlinks,
special files, stale hashes and replaced roots are refused through the shared
descriptor-based workspace API. Sources stay unchanged; only the caller may
choose to persist a returned research result.

The operator registry, root identity and worker timeout are pinned at
construction. Each call uses a local copy decoded from the initial canonical
registry. Changing public configuration fields before or during observation
refuses delivery, rather than rebinding a module to a different physical file.
An explicitly constructed new valid observer can authorize a different registered
module. This is configuration integrity within trusted operator code, not a
sandbox against arbitrary Python access to the process.

The earlier 0.1.0 development evaluation contains twelve synthetic cases: six
closed integer results and six safe inconclusive results. The 0.1.1 evaluation
adds private-helper and imported-entry cases, preserving all earlier references.
The entry/import proof cut matches fourteen references: eight conditional integer results and six safe inconclusive results, with 23 source files unchanged. The registry-guard evaluation adds controlled drift and explicit reconfiguration checks. No source module is executed by these observations. These are one coarse development family and not a
certified holdout. Test and evaluation results do not grant publication or training
approval. See the dated protocol and evaluation in
`agent/research/documentation-intelligence-20261119`.
