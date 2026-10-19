# Engineering Library frontend

Next.js App Router with TypeScript, a bilingual antique-book catalog and an internal Markdown reader. Shared browser-measured pagination and page turning support desktop spreads and mobile single pages. Reader panels provide project search, chapters and anonymous PostgreSQL bookmarks via the same-origin Rails proxy.

Use the repository-root Compose configuration. See [development documentation](../docs/projects/engineering-library/docs/en/guides/application-development.md) for setup, dependency recovery, lint, type checks and builds.

See [reader architecture and validation](../docs/projects/engineering-library/docs/en/guides/book-frontend.md) for routes, Markdown safety, logical anchors, bookmark cookies/CSRF and browser test commands.

### Fullscreen documentation media

Markdown images (including SVG image resources) and rendered Mermaid diagrams have
an accessible expand button. The viewer fits media to the viewport, supports zoom
from 1× to 8×, bounded dragging, wheel zoom, two-pointer pinch, reset and Escape.
Native modal dialog behavior traps focus and blocks background interaction; closing
returns focus to the expand button. The viewer is portaled outside the book.

Run the optional browser regression against a running frontend with Playwright
installed externally:

```sh
PLAYWRIGHT_MODULE=/path/to/playwright node tests/media-viewer.browser.mjs
```

`MEDIA_DOCUMENT_URL` can select another document containing a rendered diagram or
image. The script checks desktop, tablet and mobile sizes, opening/closing, zoom,
reset, dragging, keyboard focus and preservation of URL and physical page content.

### Embedded source references

All documented projects share collision-safe source identities, independent
expandable occurrences, measured code continuation, collapsed-source search and
fingerprint-aware bookmarks. See [source-reference architecture](../docs/projects/engineering-library/docs/en/architecture/source-references.md)
and the [Portuguese version](../docs/projects/engineering-library/docs/pt-BR/architecture/source-references.md).
Generate approved snapshots explicitly with `tools/build-source-catalog.ts`;
the reader never reads sibling repositories at runtime.
