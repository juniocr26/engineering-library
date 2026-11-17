# Source-reference verification — 2026-10-18

Implementation scope: Engineering Library only. The user explicitly approved referenced source snapshots from all six existing documented projects, excluding sensitive/configuration material. Sibling repositories were read without modifications. No staging, commit, push or publication was performed.

| Project | Markdown documents inspected | Recognized occurrences | Integrated | Missing | Excluded | Verification actually executed |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| engineering-library | 44 | 46 | 20 | 0 | 26 | EN/PT catalog + Chromium search/line navigation |
| env-auditor | 44 | 18 | 18 | 0 | 0 | EN/PT catalog + Chromium search/line navigation |
| go-image-optimizer | 54 | 54 | 48 | 0 | 6 | EN/PT catalog + Chromium search/line navigation |
| payment-reconciliation-lab | 64 | 54 | 40 | 0 | 14 | EN/PT catalog + Chromium search/line navigation |
| rust-event-relay | 158 | 426 | 369 | 0 | 57 | EN/PT catalog + Chromium search/line navigation |
| url-shortener | 56 | 70 | 58 | 0 | 12 | EN/PT catalog + Chromium search/line navigation |
| Total | 420 | 668 | 553 | 0 | 115 | Every documented project |

Counts include repeated occurrences and both languages. Unique source-file metadata records total 146. Excluded references include configuration/non-code resources and files rejected by the snapshot policy; they are not reported as integrated. Each project's `links/catalog.json` records individual paths, status and associated documentation. Genuine external links are outside the internal-source inventory.

Executed successfully:

- Frontend unit/integration suite: 33 tests, followed by the six identity tests including the additional real-catalog synchronization check. Together these cover 34 distinct tests. All passed.
- TypeScript check and ESLint; production `npm run build` completed successfully after the final application changes.
- Rails: 13 tests, 237 assertions, zero failures/errors/skips.
- Documentation/catalog Python tools: 27 tests, all passed.
- Chromium: 200 synthetic code lines traversed without duplication or omission at 390, 768 and 1440 pixels. Checked bounded page dimensions, partial-page fill through measured-flow tests, horizontal scrolling, independent repeated disclosures, exact matching line, red highlight, resize, continued expansion, bookmark restoration and complete collapse removal.
- Chromium: real approved source-search result navigation in every project. Representative catalog content spans Python, Go, Java, Rust, Ruby/TypeScript; grammar tests explicitly cover Rust, Go, Python, Ruby, JavaScript and TypeScript.
- Real catalog checks verify every file record's full canonical project/path identity and all occurrence-to-record associations. Synthetic collisions distinguish directory and project, line ranges, repeated occurrences, bilingual IDs, content changes, unavailable revisions and corrupted snapshots.
- Traversal, escaping symlinks, binary/oversized files, configuration exclusion and synthetic secret-pattern rejection were exercised without private fixtures.
- A desktop source continuation screenshot was visually inspected; the manuscript surface and shared spread/page controls remained intact.

Limits: Chromium uses emulated viewport sizes, not physical devices or Safari/Firefox. Browser bookmark transport is mocked; Rails persistence tests are separate, not an end-to-end browser/database durability test. Snapshot refresh is explicit and reviewed. Unknown pinned revisions remain unavailable rather than substituting current source. New projects need explicit source approval; their Markdown discovery and frontend rendering use the same shared mechanism. Reordering otherwise indistinguishable repeated references may change their occurrence ordinal. Screening does not independently certify publication safety.

Suggested commit (not executed): `feat(reader): integrate collision-safe paginated source references across projects`
