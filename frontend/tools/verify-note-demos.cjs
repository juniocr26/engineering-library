/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const inspectAnchors = require('./demo-anchors.cjs');
const assert = require('node:assert/strict');
(async () => {
  const base = process.env.BROWSER_BASE_URL || 'http://localhost:3099';
  if (!['localhost', '127.0.0.1'].includes(new URL(base).hostname)) throw Error('Local development only');
  const browser = await chromium.launch({ executablePath: process.env.PLAYWRIGHT_EXECUTABLE_PATH, headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  page.setDefaultTimeout(90000);
  try {
    let checked = 0;
    for (const language of ['en', 'pt-BR']) for (const document of ['architecture/current-state.md', 'img/visual-components.md']) {
      const path = `${base}/projects/engineering-library/docs/${document}?lang=${language}`;
      await page.goto(path); await page.locator('.reader[data-pagination="ready"]').waitFor();
      const demos = await (await page.request.get(`${base}/api/note-demos?${new URLSearchParams({ project: 'engineering-library', document, language })}`)).json();
      const canonical = items => items.filter(item => item.demo_key?.startsWith('visual-'));
      const demoNotes = new Set(canonical(demos.notes).map(item => item.id));
      const notes = (await page.evaluate(async ({ language, document }) => (await (await fetch(`/api/notes?project=engineering-library&document=${encodeURIComponent(document)}&language=${language}`)).json()).notes, { language, document })).filter(item => demoNotes.has(item.id));
      const anchors = await inspectAnchors(page, document, language);
      assert.equal(anchors.filter(item => !item.valid).length, 0, JSON.stringify(anchors.filter(item => !item.valid)));
      assert.ok(anchors.length >= 33);
      assert.equal(notes.length, 15);
      const data = await page.evaluate(async ({language, document}) => {
        const query = new URLSearchParams({project: 'engineering-library', document, language});
        const highlights = (await (await fetch(`/api/highlights?${query}`)).json()).highlights;
        const bookmarks = (await (await fetch(`/api/bookmarks?language=${language}&project_slug=engineering-library`)).json()).bookmarks.filter(item => item.document === document);
        return {highlights, bookmarks};
      }, {language, document});
      data.highlights = data.highlights.filter(item => canonical(demos.highlights).some(demo => demo.id === item.id));
      data.bookmarks = data.bookmarks.filter(item => canonical(demos.bookmarks).some(demo => demo.id === item.id));
      assert.equal(data.highlights.length, 15);
      assert.equal(new Set(data.highlights.map(item => item.color)).size, 7);
      assert.equal(data.bookmarks.length, 3);
      assert.equal(notes.filter(note => note.highlight_id === null).length, 1);
      console.log(`Checking ${language} ${document}: 15 notes, 15 highlights, 3 bookmarks`);
      for (const bookmark of data.bookmarks) {
        await page.goto(`${path}#${encodeURIComponent(bookmark.anchor)}`);
        await page.locator('.reader[data-pagination="ready"]').waitFor();
        await page.waitForFunction(anchor => Array.from(document.querySelectorAll('.reader-pages [data-highlight-block]')).some(block => block.getAttribute('data-highlight-block') === anchor), bookmark.anchor);
      }
      const physicalPages = new Set();
      for (const note of notes) {
        await page.goto(`${path}#${encodeURIComponent(note.segments[0].block)}`);
        await page.locator('.reader[data-pagination="ready"]').waitFor();
        physicalPages.add(await page.locator('.reader-controls:visible span').first().innerText());
        await page.locator(`[data-note-id="${note.id}"]`).click();
        assert.equal(await page.locator('#note-draft').inputValue(), note.body);
        await page.getByRole('button', { name: language === 'en' ? 'Preview' : 'Pré-visualizar', exact: true }).click();
        const preview = page.locator('dialog.note-preview'); await preview.waitFor();
        for (const diagram of await preview.locator('.reader-diagram').all()) await diagram.locator('img').waitFor();
        assert.equal(await preview.getByRole('alert').count(), 0);
        for (const src of ['/assets/writer-library.jpg', '/api/shared-assets/diagrams/reader-storage.svg', 'https://www.w3.org/Icons/w3c_home.svg']) {
          if (!note.body.includes(src)) continue;
          const graphic = preview.locator(`img[src="${src}"]`).first();
          await graphic.waitFor();
          await page.waitForFunction(element => element.complete && element.naturalWidth > 0, await graphic.elementHandle());
        }
        await page.screenshot({ path: `/tmp/note-demo-${String(++checked).padStart(2, '0')}.png` });
        if (note.body.includes('Worker 35')) {
          assert.ok(await preview.locator('.reader-table').evaluate(n => n.scrollWidth > n.clientWidth));
          await preview.getByRole('button', { name: language === 'en' ? 'Expand table' : 'Ampliar tabela', exact: true }).click();
          await page.locator('dialog.table-viewer').waitFor(); await page.keyboard.press('Escape');
        }
        if ((note.body.includes('Review 12') || note.body.includes('Revisão 12'))) {
          const stage = preview.locator('.note-preview-scroll');
          assert.ok(await stage.evaluate(n => n.scrollHeight > n.clientHeight));
          for (let i = 0; i < 3; i++) await preview.getByRole('button', { name: language === 'en' ? 'Zoom in' : 'Ampliar', exact: true }).click();
          const rect = await stage.boundingBox();
          await page.mouse.move(rect.x + 120, rect.y + 180); await page.mouse.down();
          await page.mouse.move(rect.x + 50, rect.y + 100, { steps: 8 }); await page.mouse.up();
          assert.ok(await stage.evaluate(n => n.scrollTop > 0 || n.scrollLeft > 0));
        }
        await page.keyboard.press('Escape');
        await page.getByRole('button', { name: language === 'en' ? 'Close note' : 'Fechar nota', exact: true }).click();
      }
      assert.ok(physicalPages.size > 1, 'annotations must span physical reader pages');
    }
    console.log(`PASS ${checked} persisted demonstrations opened through actual indicators and parchment previews, including complex Mermaid, wide tables and long scrolling notes`);
  } finally { await context.close(); await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
