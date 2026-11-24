# OpenCV Algorithm: virtual defaults and persistence boundaries

This chapter describes selected public source at OpenCV revision `5d0660acfed08650cafec4876b4792a369a20601`. It covers the base `cv::Algorithm` interface, selected persistence helpers and their dependencies, not the complete behavior of every derived algorithm or the storage subsystem. This source family has sixteen historical development records and is not an independent evaluation family. The text is manually authored research documentation, not a neural-model improvement or an owner-approved training target.

The source evidence retains root `LICENSE` and `COPYRIGHT` files together with the notices in the selected source files. The root contains Apache-2.0 text; the selected interface and implementation also contain BSD-style three-condition notices. Those notices are preserved rather than replaced by a blanket root-license claim. This is not a complete rights audit or permission to publish or train.

## Base interface and derived behavior

Here, `core.hpp` denotes `modules/core/include/opencv2/core.hpp`; `algorithm.cpp` denotes `modules/core/src/algorithm.cpp`. Supporting headers are under `modules/core/include/opencv2/core/`.

At `core.hpp:3333-3362`, the destructor and the selected state/serialization methods are virtual. The base `clear` body is empty. The base one-argument `write` and node-taking `read` use `CV_UNUSED`, whose selected definition is a void cast (`cvdef.h:147`). The base `empty` returns false. These are base defaults; they do not establish that each derived implementation clears state, serializes all parameters or reports emptiness the same way. In particular, the base false result alone is not proof that an algorithm has been correctly loaded or trained.

The header's existing documentation describes the base interface and the need for derived reading/writing implementations. Those comments provide intended usage context, but concrete derived behavior still requires its implementation. This chapter does not enumerate derived classes or resolve their runtime types.

## Named writing and dynamic dispatch

The two-argument `write(FileStorage&, const String&)` overload is not declared virtual at `core.hpp:3350`. Its selected implementation distinguishes an empty name from a named mapping (`algorithm.cpp:58-69`). With an empty name it calls the one-argument `write` and returns. Otherwise it emits the name and opening delimiter, calls that same one-argument method and emits the closing delimiter.

The inner method is virtual. A nonvirtual wrapper does not turn its inner call into a nonvirtual call or prove which concrete override will run. The owned language example below demonstrates that distinction for synthetic classes. It does not execute OpenCV. Overload visibility is also a separate issue: a derived declaration can hide a base overload; the owned negative compile control and the corresponding `using` control illustrate that language boundary without asserting the declaration choices of every OpenCV derived type.

## Reading and loading stages

The selected templates are static member functions. They call a type-specific `create`, invoke reading on the object and use its `empty` result to choose an object or an empty pointer. Expression compatibility, `Ptr` behavior and the selected derived implementation are dependencies; these helpers are not a general deserialization validator.

| Helper | Written stages in the selected body | Limit |
| --- | --- | --- |
| `read<_Tp>` | Create object, call node-reading method, return object when its emptiness predicate is false (`core.hpp:3375-3380`). | No explicit node-empty or null-create check is shown in this body. |
| `load<_Tp>` | Open with `FileStorage::READ`, invoke `CV_Assert(fs.isOpened())`, select the first top-level or named node, return an empty `Ptr` if the node is empty, then create/read/check (`core.hpp:3394-3403`). | The final pointer decision still depends on object behavior; it is not guaranteed successful reconstruction. |
| `loadFromString<_Tp>` | Open with `FileStorage::READ + FileStorage::MEMORY`, select node, then create/read/check (`core.hpp:3415-3422`). | It does not show the same explicit open assertion or empty-node early return as the selected file-loading body. |

The lack of an explicit guard in one body does not establish every invalid-input outcome. Constructors, node access, pointer operations, factories and overrides may have additional behavior or fail before a normal return. No input file, serialized model or image was opened to evaluate these helpers in this campaign. The owned compatible-template-shape control is not an actual OpenCV instantiation and does not settle all of its pointer or type requirements.

## Saving, naming and errors

The selected `save` and `getDefaultName` declarations are virtual (`core.hpp:3424-3430`). The base saving implementation creates a write-mode storage, opens a node using `getDefaultName`, calls the one-argument writer and closes the mapping (`algorithm.cpp:71-78`). The base naming implementation returns `my_object` (`algorithm.cpp:80-84`); that value is not evidence that every derived type shares the name or has a unique one. The protected `writeFormat` emits a format field with integer 3 (`algorithm.cpp:86-89`). The selected base saving body does not itself call that helper; derived behavior is not inferred from this absence.

These written operations do not guarantee successful, complete, durable or atomic file persistence. The storage implementation and actual writer are outside this selected proof. The normal return does not provide a status value from the void saving method, and failures are not exhaustively modeled here.

The assertion configuration matters. In `exception.hpp:154-201`, `CV_STATIC_ANALYSIS` selects a simplified assertion that aborts on a false condition; the ordinary branch calls `cv::error` with `cv::Error::StsAssert`. The selected documentation distinguishes `CV_Assert` from the debug-only assertion form. This chapter does not promise a single exception or termination mode for all builds, callbacks and storage failures. It did not run either original assertion path.

A deprecated pointer-storage overload is declared only under `CV_VERSION_MAJOR < 5` (`core.hpp:3351-3354`). Its absence from the selected implementation file is not proof of global API removal or of the configuration of an installed library.

## Owned language example and observations

The following is the exact standalone source used in the owned base-reference wrapper observation. Its classes are synthetic and do not include or link OpenCV. The nonvirtual wrapper calls a virtual writer on the same object; the observed output has an emptiness value of 1 and a write count of 1.

```cpp
#include <cstdio>
struct Sink { int writes = 0; };
struct Base {
  virtual ~Base() = default;
  virtual void clear() {}
  virtual bool empty() const { return false; }
  virtual void write(Sink&) const {}
  void write(Sink& sink, const char*) const { write(sink); }
};
struct Derived : Base {
  void write(Sink& sink) const override { ++sink.writes; }
  bool empty() const override { return true; }
};
int main() { Derived derived; Base& base = derived; Sink sink; base.write(sink, "node"); std::printf("{\"empty\":%d,\"writes\":%d}\n", base.empty(), sink.writes); }
```

The actual compiler invocation, source and binary hashes, stdout and stderr are preserved under the owned observation evidence. Existing Apple clang 21 compiled with C++17 and strict warning/pedantic flags. Across six frozen controls, all six compile expectations matched: five successful compilations and one intended overload-hiding rejection. The five executed owned programs produced all five expected JSON results. A qualified-base control also demonstrated the base implementation result, while the visibility control added `using Base::write` to make the wrapper overload accessible through the derived object.

These observations validate those owned programs on this host. They do not prove that the actual OpenCV headers compile in this environment, that a particular algorithm override is selected, or that storage operations succeed. No OpenCV build, installation, server, migration or upstream test suite ran.

## Existing tests and coverage uncertainty

The initially guessed base-algorithm test path was absent at the pinned revision. A bounded textual search in `modules/core/test` for the selected algorithm helper names also found no matching paths. This is a discovery limit, not a repository-wide claim that tests or coverage do not exist. No original test result is inferred. The existing header comments and examples remain source documentation; the owned controls above are separate research observations, not additions to the permanent test suite.

## FAQ

**Does the base emptiness result prove a valid loaded model?** No. The base default returns false; a meaningful state predicate depends on the selected type and implementation.

**Does a nonvirtual named-write overload prevent virtual dispatch inside it?** No. Its selected body calls the virtual one-argument writer. Concrete target behavior is not established for every derived type.

**Do the file and string loading bodies contain identical guards?** No. The selected file-loading body has an explicit open assertion and empty-node early return that are not written in the selected string-loading body. Full failure behavior requires more evidence.

**Does saving guarantee a complete and atomic state snapshot?** No. The selected wrapper delegates storage and writing; no such guarantee follows from these bodies.

**Can a missing definition in the selected file justify removing the deprecated overload from documentation everywhere?** No. The header has a conditional declaration, and a partial selection does not establish global absence or an installed build's configuration.

**Were these language observations OpenCV tests?** No. They compiled and ran owned synthetic programs. No original library header, algorithm, serialized input or upstream suite was executed.

## Preservation and review status

All original source files, prior campaign artifacts, rejected outputs and owned observation evidence remain preserved. This candidate is isolated from the active catalog and external project documentation. Source-only reconstruction and complete bilingual review are required before readiness for owner review. Owner approval, training gold, publication, full application integration and neural learning are not inferred from this document.
