# Documentation checks, application tests and execution evidence

[Contents](../index.md) | [Português brasileiro](../../pt-br/testing/documentation.md)

Reviewed/executed 2026-11-10. Audience: maintainers and documentation reviewers. Structural success is not technical completeness, production acceptance or semantic translation approval.

<!-- reading-section: static -->
## Existing static fixture suite

From the repository root:

```sh
python3 -B -m unittest discover -s tools -p 'test_*.py' -v
```

Actual exit 0: **28 tests passed**. tools/test_catalog.py and tools/test_check_docs.py use owned temporary trees and synthetic fixtures for catalogs, bilingual variables/questions, relative files/anchors, unsafe paths, symlinks, encoding, CLI failures and read-only behavior. This execution tests validator behavior, not the real corpus's correctness. It does not modify application databases or run catalog sync.

<!-- reading-section: application -->
## Application suites inspected, not executed

Backend includes test/integration for catalog, bookmarks, highlights, notes and annotations, migration tests and offline Ruby tests. The inspected offline/catalog_files_offline.rb covers contained reads, unsafe bios, traversal/symlinks, missing files and binary data; offline/note_identity_offline.rb checks logical range identity independent of relocation context. Those definitions are not a new Ruby pass result.

Frontend package.json defines Node --experimental-strip-types --test tests/*.test.ts, typecheck/lint/build and separate browser scripts. Browser/notes-demo commands can create data or require services; never treat every script as a harmless static check. Host Node is unavailable; Rails, frontend, browser and database suites were not executed in this continuation. No dependency/runtime was installed.

<!-- reading-section: corpus -->
## Corpus validation and history

check_docs.py checks configured source documentation; check_catalog.py checks collections plus historical inventory/import provenance. Their full runs may inspect sibling sources and reject historical manifest drift. They are different from the fixture suite and from scoped in-memory link/anchor/parity checks. No historical provenance or snapshot was regenerated and no full-corpus pass is claimed here.

The 2026-10-19 report of 27 tests and six initial reachability findings remains historical in its dated audit record; this invocation observed 28 tests. Keep dates/scopes separate. Recheck both languages after validator, parser, test commands or runtime boundaries change. Review source-backed accuracy, security and translations in addition to automated structure.

## Corpus invocation during ecosystem reconciliation

Executed from the ecosystem workspace root on 2026-11-10:

```sh
python3 -B engineering-library/tools/check_docs.py --workspace "$PWD"
python3 -B engineering-library/tools/check_catalog.py
```

The first returned exit 1: 580 documents, five errors and four warnings. Findings comprise four unsafe repository locations outside the selected workspace, one README/index finding caused by lexical pt-br/pt-BR comparison, restricted vendor references and an unchecked anchor. The collection check returned exit 1: 778 Markdown files, 4806 relative links, one historical project-inventory mismatch and 26 warnings. These are failed full-corpus gates, not passing validation. No manifest, provenance or snapshot was changed.

An in-memory comparison using HEAD versions of modified documents and excluding newly authored pages found 80 errors/four warnings before these changes, with zero introduced findings. The comparison normalizes case for HEAD substitution and excludes new files from traversal. The collection's error was identical to HEAD and no new warning was introduced. Targeted checks separately validate changed pages, bilingual section identities, relative links/anchors and index reachability; they do not certify unreviewed legacy semantics or external URL availability. Portal Portuguese index links now use paths relative to that language directory, eliminating its 55 reachability findings. The README already links the Git-tracked `docs/pt-BR/index.md`; its remaining validator finding must not be “fixed” by introducing a nonexistent lowercase path on case-sensitive filesystems. Repository casing remains as tracked, without a case-only rename.
