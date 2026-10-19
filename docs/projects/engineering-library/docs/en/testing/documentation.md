# Validation and limits

[Existing documentation validator](../guides/documentation-validator.md).


Use `python3 -B docs/validation/check_catalog.py` from the repository root for the current project catalog. Runtime tests are separate from static documentation checks.

## Audit validation — 2026-10-19

The existing isolated Python suite executed with 27 passing tests. It covers catalog fixtures, restricted paths, links/anchors, symlink handling, read-only validation and bilingual contract failures. Run from the repository root:

```sh
python3 -B docs/validation/check_catalog.py
python3 -B -m unittest discover -s tools -p 'test_*.py' -v
git diff --check
```

The first catalog run found six pre-existing reachability errors: two source-reference pages unreachable from both central/project indexes and two other unlinked verification pages. Current changes add index links. Final counts belong to the [audit record](../../../../../validation/documentation-audit-2026-10-19.json), rather than earlier execution reports.

Host `node` and `npm` were unavailable. No frontend build, typecheck, browser pagination or Rails/database suite ran in this audit. Existing backend tests define catalog sync/order and anonymous bookmark/CSRF boundaries; frontend tests define logical reading order. These source assertions are not new runtime results. Structural validation does not certify answer accuracy or equivalent translation.
