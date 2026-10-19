/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require('/tmp/numbering-browser/node_modules/playwright');
const assert = require('node:assert/strict');
(async () => {
  const base = process.env.BROWSER_BASE_URL || 'http://localhost:3000';
  const context = await chromium.launchPersistentContext('/tmp/engineering-note-demo-browser', { headless: true, args: ['--no-sandbox'], viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  try {
    let checked = 0;
    for (const language of ['en', 'pt-BR']) {
      const path = `${base}/projects/engineering-library/docs/architecture/current-state.md?lang=${language}`;
      await page.goto(path); await page.locator('.reader[data-pagination="ready"]').waitFor();
      const notes = await page.evaluate(async language => (await (await fetch(`/api/notes?project=engineering-library&document=architecture%2Fcurrent-state.md&language=${language}`)).json()).notes, language);
      assert.equal(notes.length, language === 'en' ? 15 : 1);
      for (const note of notes) {
        await page.goto(`${path}#${encodeURIComponent(note.segments[0].block)}`);
        await page.locator('.reader[data-pagination="ready"]').waitFor();
        await page.locator(`[data-note-id="${note.id}"]`).click();
        assert.equal(await page.locator('#note-draft').inputValue(), note.body);
        await page.getByRole('button', { name: language === 'en' ? 'Preview' : 'Pré-visualizar', exact: true }).click();
        const preview = page.locator('dialog.note-preview'); await preview.waitFor();
        for (const diagram of await preview.locator('.reader-diagram').all()) await diagram.locator('img').waitFor();
        assert.equal(await preview.getByRole('alert').count(), 0);
        await page.screenshot({ path: `/tmp/note-demo-${String(++checked).padStart(2, '0')}.png` });
        if (note.body.includes('Worker 35')) {
          assert.ok(await preview.locator('.reader-table').evaluate(n => n.scrollWidth > n.clientWidth));
          await preview.getByRole('button', { name: 'Expand table', exact: true }).click();
          await page.locator('dialog.table-viewer').waitFor(); await page.keyboard.press('Escape');
        }
        if (note.body.includes('Review 12')) {
          const stage = preview.locator('.note-preview-scroll');
          assert.ok(await stage.evaluate(n => n.scrollHeight > n.clientHeight));
          for (let i = 0; i < 3; i++) await preview.getByRole('button', { name: 'Zoom in', exact: true }).click();
          const rect = await stage.boundingBox();
          await page.mouse.move(rect.x + 120, rect.y + 180); await page.mouse.down();
          await page.mouse.move(rect.x + 50, rect.y + 100, { steps: 8 }); await page.mouse.up();
          assert.ok(await stage.evaluate(n => n.scrollTop > 0 || n.scrollLeft > 0));
        }
        await page.keyboard.press('Escape');
        await page.getByRole('button', { name: language === 'en' ? 'Close note' : 'Fechar nota', exact: true }).click();
      }
    }
    console.log(`PASS ${checked} persisted demonstrations opened through actual indicators and parchment previews, including complex Mermaid, wide tables and long scrolling notes`);
  } finally { await context.close(); }
})().catch(error => { console.error(error); process.exit(1); });
