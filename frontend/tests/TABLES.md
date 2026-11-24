# Markdown table verification

All synthetic content is generated in `fixtures/tables.ts`. The fixtures contain 5, 30, 200 and 500 body rows, 8–12 columns, fictional long identifiers and values, links, inline code, wrapped multi-line descriptions and variable rendered row heights. They never read environment files or private project configuration. Stress routes exist only in an isolated temporary Next.js project created by the browser runner; they are not shipped or indexed.

## Running

From the repository root, start `docker compose up -d --build --wait --wait-timeout 300`. Browser tooling is included in the development image.

```sh
docker compose exec -T frontend npm test
docker compose exec -T frontend npm run typecheck
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm run build:check
# Existing frontend, internal localhost:3000:
docker compose exec -T frontend npm run test:tables:public
```

The synthetic `test:tables` runner starts a separate fixture server. It is outside the existing-services-only workflow; do not start it without approval. The public suite above uses the running frontend.

- Existing reader, media-viewer and bookmark-control browser suites remain separate. The media suite now waits for the reader's actual idle state after page turns instead of assuming a fixed animation duration.

The size matrix verifies exact row order and count, column count, repeated headers, bounded table/page dimensions, termination, keyboard scrolling, mouse dragging on desktop, emulated native touch scrolling on mobile/tablet, complete semantic fullscreen content, zoom/reset, Escape, focus return and viewport changes. Edge scenarios use rendered dimensions to exercise exactly one fitting row, insufficient remaining space near the bottom of a page, oversized rows and oversized headers. Unit tests also exercise alternating capacities and indivisible structures. The focused browser checks resolve row 117 at all three widths and instrument row measurements in a 500-row table: page turns and a height-only viewport change must perform zero additional row measurements.

## Implementation and limits

The existing `paginateMeasured` entry point accepts optional table measurements. The hidden probe measures the complete table once per relevant layout, reading row heights in a batch. Table measurements are reused when only the available page height changes; width, content, language, font loading and asset changes invalidate them. Ordinary page turns do not remeasure rows. No virtualization or independent navigation engine is introduced.

Segments retain the original header and fixed measured column widths. A body-row offset is a stable content location across viewport changes, not a stored physical page number. Original table anchors still resolve to the beginning. Search results can address a matching continuation row. Scroll offsets are shared between segments of the same document table and reset on viewport changes.

An indivisible oversized row (including its header) receives a bounded native scrolling region and access to the complete table viewer. An oversized header scrolls with that region. Unsupported independent-row structures use a whole-table scrolling fallback rather than unsafe splitting. Each pagination iteration consumes at least one row or flushes a nonempty page.

The current renderer supports GFM tables with one semantic header row; wrapped headings are supported. It deliberately skips raw HTML. Arbitrary HTML tables, multi-row headers, `rowspan`, `colspan`, nested block paragraphs and literal multi-line Markdown cell syntax are not newly supported. Tables nested in other Markdown blocks use the indivisible fallback. Do not infer support for those structures from the normal GFM table tests.

Browser verification uses Chromium and emulated viewports/touch, not physical devices or Safari/Firefox. Bookmark-control tests simulate their API; they do not establish database durability. The row-location tests establish continuation resolution independently of viewport page numbers.
