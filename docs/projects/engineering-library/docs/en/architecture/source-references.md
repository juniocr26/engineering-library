# Embedded source references

The shared reader discovers source links from the Markdown syntax tree for every documented project. Inline and reference-style links are supported, including line ranges. Each source is resolved in its own project; there is no basename lookup or first-match fallback. Markdown documents open inside the reader, section links retain their anchors, and genuine external resources retain their link behavior.

## Identity and catalog

Each project's `links/catalog.json` stores one authoritative file record per normalized repository-relative path, with project identity, approval state, SHA-256 and a snapshot location. Canonical source keys serialize `[project, fullPath, optionalRevision]`. Line ranges are locations inside that file and never select a different file. Content-addressed snapshots are stored under `links/snapshots/`; documentation text is not duplicated there.

A disclosure occurrence has a separate ID derived from project, language-independent document ID, canonical source identity, optional line range and repeated-occurrence ordinal. Repeated links, including identical links in one paragraph, have independent expansion state. English and Portuguese references in corresponding occurrence order share stable IDs; their prose and physical page numbers are excluded from identity.

Line anchors include occurrence ID, snapshot fingerprint and original source line. A changed snapshot invalidates an old line bookmark instead of silently opening a different line. Reordering indistinguishable repeated references changes their ordinal association; no semantic identity across such edits is inferred.

## Approval and deployment

On 2026-10-18 the user authorized snapshots of referenced code from the six existing documented projects, excluding sensitive material. Configuration files, environment files, dependency trees, binaries, files above 512 KB, escaping symlinks and detected secret patterns are excluded. Screening supplements approval; it does not establish that arbitrary content is safe to publish. Catalogs expose repository-relative paths only.

Generate snapshots explicitly from the frontend directory:

```sh
SOURCE_WORKSPACE=/path/to/portfolio \
APPROVE_REFERENCED_SOURCE=yes \
node --experimental-strip-types tools/build-source-catalog.ts
```

`DOCUMENTATION_ROOT` optionally selects the collection. `APPROVED_SOURCE_PROJECTS` is a comma-separated explicit approval scope; its default is the six projects authorized on that date. Future projects need approval before their code is included. The generator discovers documents automatically, validates real paths, reads source as text, removes obsolete generated snapshots and never executes referenced files. Review generated changes before publication.

The reader reads approved snapshots, checks hashes and never reads sibling repositories or fetches GitHub at runtime. Docker's existing read-only documentation mount includes catalogs and snapshots, so Rails and deployment need no sibling-repository mounts or generic file API. A GitHub revision is accepted only when it matches the approved record's revision or fingerprint. Unavailable pinned revisions produce an explicit state; current source is never silently substituted.

## Expansion, pagination and navigation

Source references are keyboard-operable buttons. Expansion inserts code after the containing Markdown unit; source-list entries are individual units. Multiple links inside one paragraph retain their inline controls and their expanded sections follow that paragraph in link order. Collapse removes all segments of that occurrence and repaginates near the original control.

Code lines extend the existing measured table/page flow. The browser measures headers, complete lines, wrapper spacing and alternating page capacities. Remaining room is consumed before continuation pages are created. Every continuation retains editor colors, original indentation and line numbers, and displays its source path and continuation range. It has no new disclosure. Horizontal scrolling preserves long lines; an oversized indivisible line has an accessible scrolling fallback. Page turns, manuscript surfaces and the responsive spread/single-page engine remain shared.

Highlight.js supplies read-only language grammars for Rust, Go, Python, Ruby, JavaScript, TypeScript, Java, C#, PHP, shell and SQL. Highlighted multiline spans are reopened at physical line boundaries without changing source text. Unsupported grammars display escaped plain text.

The existing project search scans approved source snapshots even when disclosures are collapsed. Source results retain project, full path, document, occurrence, revision/fingerprint, original line and excerpt. Selecting a result expands the exact occurrence, repaginates, turns to its line and applies the red highlight. Unapproved content is excluded from search. Search retains its existing 80-result cap; there is no new database or external search service.

Shared PostgreSQL bookmarks retain the existing architecture. Bookmarking a continuation stores its first logical line anchor. Restoring that anchor expands the correct occurrence after reflow. Missing or changed source locations show a fallback notice. Expansion survives page turning, resizing and font remeasurement. Session storage retains independent occurrences across document navigation, language changes and reloads in the same browser tab when storage is available. Collapse explicitly removes that occurrence from the saved expansion state.

## Verification

The generated `docs/source-reference-report.json` and each catalog enumerate candidate occurrences, integrated occurrences, excluded references and missing files project by project. Counts include repeated links and both languages; they are not counts of unique files. Markdown without source references uses the ordinary reader flow.

Focused tests cover file-name collisions, project isolation, bilingual identity, repeated disclosures, line ranges, exact search/bookmark locations, content changes, corrupt snapshots, traversal, symlinks and highlighting. Browser tests exercise synthetic 200-line code on mobile, tablet and desktop plus approved references from every catalog project. Run `npm test`, `npm run typecheck`, `npm run lint`, `npm run build` and `node tests/source-reader.browser.mjs` (with the environment's Playwright module/browser paths). Browser bookmark tests mock transport; the existing Rails tests exercise bookmark persistence separately.
