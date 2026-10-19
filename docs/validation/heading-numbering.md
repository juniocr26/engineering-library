# Canonical heading numbering verification — 2026-10-19

The existing `documentationEntries` tree remains the sole numbering authority.
`numberHeadingUnits` resolves document titles and sections by canonical document ID
and original Markdown AST anchor. It copies the resolved entry ID and number into
presentation metadata. TOC, project chapter links, local chapter links and Markdown
headings consume these numbers without counters in UI components. Typography runs
independently; heading source, search text and anchor identities remain unchanged.
Only an exact matching numeric prefix is deduplicated; unrelated numeric literals
are preserved. The same rendered headings enter the existing measured pagination.

## Complete catalog audit

The active backend catalog was checked across two API pages against all six local
collections. Inventory: 434 Markdown files, including excluded navigation, metadata
and legacy files. Both EN and PT-BR trees were scanned. No technical Markdown was
rewritten.

| Project | EN entries | PT-BR entries | Internal headings EN/PT-BR | Number/anchor errors |
| --- | ---: | ---: | --- | ---: |
| Engineering Library | 91 | 97 | 69 / 75 | 0 |
| Env Auditor | 75 | 83 | 54 / 62 | 0 |
| Go Image Optimizer | 179 | 183 | 153 / 157 | 0 |
| Payment Reconciliation Lab | 116 | 119 | 85 / 88 | 0 |
| Reliable Event Relay | 565 | 565 | 487 / 487 | 0 |
| URL Shortener | 202 | 293 | 175 / 266 | 0 |

The validator checks the complete navigation trees, original heading destinations,
reader number metadata and output of the shared HAST numbering transform. This is
an automated structural/rendering audit, not visual browser inspection of every
heading. Virtual categories have no corresponding Markdown heading.

Bilingual equivalence remains limited by the existing sources: 1,958 directed
heading findings lack verified cross-language canonical identities. URL Shortener
also has seven FAQ question identities Q001–Q007 with different parent numbering:
EN `6.80.1`–`6.80.7`, PT-BR `6.79.1`–`6.79.7` (14 directed findings). These are
reported source/tree differences, not inferred translations or repaired content.
Within each language the three rendering contexts use that language's canonical
number. No cross-language structural equivalence is claimed for these findings.

## Regression coverage and executed checks

- `npm test`: 80 tests passed, including a structural insertion fixture in both
  languages that changes resolved numbers while preserving heading anchors.
- New coverage checks all heading levels, document titles, nesting beyond nine,
  canonical IDs, FAQ/ADR/date literals and exact manual-prefix deduplication.
- `npm run lint`, `npm run typecheck`, `npm run build`: passed in the frontend
  container. An initial typecheck overlapped build regeneration of `.next/types`;
  the subsequent standalone check passed.
- `npm run audit:navigation`: passed; complete inventory and detailed bilingual
  findings are emitted to `/tmp/navigation-inventory.json` and
  `/tmp/navigation-audit.json` inside the frontend container.
- Chromium regression checks one deep section per project and language, including
  Env Auditor architecture, numbered visible headings, chapter panel links and
  desktop/mobile resize repagination. The expanded 12-case run also passed TOC
  link navigation back to the numbered reader heading. This is sampled layout
  coverage, not an
  exhaustive visual audit of every physical page.
- Existing `tests/book-reader.browser.mjs`: passed at 390, 768 and 1440px,
  including pagination, languages, documents, console and page-turn checks.

Browser test command (Playwright supplied by the test environment):

```sh
PLAYWRIGHT_MODULE=/path/to/playwright node tests/heading-numbering.browser.cjs
```
