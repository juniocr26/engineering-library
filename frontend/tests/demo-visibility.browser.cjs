/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const { runDemos } = require('../tools/note-demos.cjs');
const inspectAnchors = require('../tools/demo-anchors.cjs');
const base = process.env.BROWSER_BASE_URL;
const ready = async page => { await page.locator('.reader[data-pagination="ready"]').waitFor(); await page.waitForFunction(() => document.querySelector('.reader-stage')?.getAttribute('aria-busy') === 'false'); };
const read = (page, language) => page.evaluate(async language => ({
  ...(await (await fetch(`/api/annotations?project=engineering-library&language=${language}`)).json()),
  ...(await (await fetch(`/api/bookmarks?project_slug=engineering-library&language=${language}`)).json()),
}), language);
(async () => {
  assert.equal(process.env.SHARED_ANNOTATIONS_TEST, '1', 'Use an explicitly isolated QA installation; never clear real collections to run this test.');
  assert.ok(base && ['localhost', '127.0.0.1'].includes(new URL(base).hostname));
  const browser = await chromium.launch({ executablePath: process.env.PLAYWRIGHT_EXECUTABLE_PATH, headless: true });
  const first = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
  const second = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
  const page = await first.newPage(), other = await second.newPage();
  page.setDefaultTimeout(90000); other.setDefaultTimeout(90000);
  const visit = async (page, doc = 'architecture/current-state.md', language = 'en') => { await page.goto(`${base}/projects/engineering-library/docs/${doc}?lang=${language}`); await ready(page); };
  try {
    await visit(page);
    for (const language of ['en', 'pt-BR']) { const data = await read(page, language); assert.equal(data.counts.all, 0, 'QA database must be empty before seeding'); assert.equal(data.bookmarks.length, 0); }
    await page.getByRole('button', { name: 'Highlights and Notes', exact: true }).click();
    await page.getByText('No highlights or notes in this project.', { exact: true }).waitFor(); await page.keyboard.press('Escape');
    await page.getByRole('button', { name: 'My Bookmarks', exact: true }).click();
    await page.getByText('No bookmarks saved for this project.', { exact: true }).waitFor(); await page.keyboard.press('Escape');
    await runDemos({ base }); await runDemos({ base });
    for (const language of ['en', 'pt-BR']) {
      for (const current of [page, other]) {
        await visit(current, 'architecture/current-state.md', language);
        const data = await read(current, language);
        assert.deepEqual(data.counts, { yellow: 6, blue: 4, pink: 4, orange: 4, purple: 4, red: 4, green: 4, notes: 30, all: 32 });
        assert.equal(data.bookmarks.length, 6);
        await current.locator('[data-note-id]').first().waitFor(); await current.locator('.bookmark-ribbon--saved').first().waitFor();
        const anchors = await inspectAnchors(current, 'architecture/current-state.md', language);
        assert.equal(anchors.length, 33); assert.ok(anchors.every(item => item.valid));
        const english = language === 'en';
        await current.getByRole('button', { name: english ? 'My Bookmarks' : 'Minhas marcações', exact: true }).click();
        await current.locator('.reader-saved-bookmark').nth(5).waitFor(); await current.keyboard.press('Escape');
        await current.getByRole('button', { name: english ? 'Highlights and Notes' : 'Destaques e notas', exact: true }).click();
        await current.locator('.annotation-entry').first().waitFor();
        const labels = english ? ['Yellow', 'Blue', 'Pink', 'Orange', 'Purple', 'Red', 'Green', 'Notes'] : ['Amarelo', 'Azul', 'Rosa', 'Laranja', 'Roxo', 'Vermelho', 'Verde', 'Notas'];
        for (let i = 0; i < labels.length; i++) {
          const count = i === 0 ? 6 : i === 7 ? 30 : 4;
          await current.getByRole('button', { name: english ? 'Filter annotations' : 'Filtrar anotações', exact: true }).click();
          await current.getByRole('menuitemradio', { name: `${labels[i]} (${count})`, exact: true }).click();
          await current.waitForFunction(n => document.querySelector('.annotation-list')?.getAttribute('aria-busy') === 'false' && document.querySelectorAll('.annotation-entry').length === Math.min(n, 20), count);
        }
        await current.screenshot({ path: `/tmp/shared-annotations-${language}-${current === page ? 'first' : 'second'}.png` });
        await current.keyboard.press('Escape');
      }
    }
    assert.equal((await first.cookies()).length, 0); assert.equal((await second.cookies()).length, 0);
    // Manual CRUD uses the actual selection toolbar, note editor and page ribbon.
    await visit(page, 'README', 'en');
    await page.waitForFunction(() => !document.querySelector('.reader-bookmark-toggle')?.disabled);
    await page.getByRole('button', { name: 'Bookmark page', exact: true }).first().click();
    await page.locator('.bookmark-ribbon--saved').first().waitFor();
    await page.locator('.reader-pages [data-highlight-block]:not([data-highlight-unsupported]) p:not(:has(a)):not(:has(img))').first().evaluate(p => {
      const text = document.createTreeWalker(p, NodeFilter.SHOW_TEXT).nextNode();
      const range = document.createRange(); range.setStart(text, 0); range.setEnd(text, Math.min(20, text.length));
      getSelection().removeAllRanges(); getSelection().addRange(range);
      document.dispatchEvent(new Event('selectionchange')); p.dispatchEvent(new MouseEvent('mouseup', { bubbles: true })); p.dispatchEvent(new PointerEvent('pointerup', { bubbles: true }));
    });
    await page.getByRole('button', { name: 'Green', exact: true }).click();
    await page.waitForFunction(() => CSS.highlights.get('reader-green')?.size > 0);
    const hit = await page.evaluate(() => { const rect = [...CSS.highlights.get('reader-green')][0].getClientRects()[0]; return { x: rect.x + 2, y: rect.y + rect.height / 2 }; });
    await page.mouse.click(hit.x, hit.y); await page.getByRole('button', { name: 'Open note', exact: true }).click();
    await page.locator('#note-draft').fill('Manual shared note 📚'); await page.getByRole('button', { name: 'Save', exact: true }).click();
    await page.getByText('Note saved successfully.', { exact: true }).waitFor(); await page.getByRole('button', { name: 'Close note', exact: true }).click();
    await visit(other, 'README', 'en');
    await other.locator('[data-note-id]').first().click();
    assert.equal(await other.locator('#note-draft').inputValue(), 'Manual shared note 📚');
    await other.locator('#note-draft').fill('Updated in another browser ✅'); await other.getByRole('button', { name: 'Save', exact: true }).click();
    await other.getByText('Note updated successfully.', { exact: true }).waitFor(); await other.getByRole('button', { name: 'Close note', exact: true }).click();
    await page.reload(); await ready(page); await page.locator('[data-note-id]').first().click();
    assert.equal(await page.locator('#note-draft').inputValue(), 'Updated in another browser ✅'); await page.getByRole('button', { name: 'Close note', exact: true }).click();
    assert.equal((await read(page, 'pt-BR')).counts.notes, 30);
    await runDemos({ base, cleanup: true });
    await other.reload(); await ready(other);
    const after = await read(other, 'en'); assert.equal(after.counts.notes, 1); assert.equal(after.counts.green, 1); assert.equal(after.bookmarks.length, 1);
    assert.equal((await read(other, 'pt-BR')).counts.all, 0);
    await other.locator('[data-note-id]').first().click(); await other.getByRole('button', { name: 'Delete note', exact: true }).click();
    await other.getByRole('dialog', { name: 'Delete note?', exact: true }).getByRole('button', { name: 'Delete note', exact: true }).click();
    await other.locator('dialog.note-editor').waitFor({ state: 'detached' });
    await page.reload(); await ready(page); assert.equal(await page.locator('[data-note-id]').count(), 0);
    assert.equal((await read(page, 'en')).counts.green, 1);
    // Remove only the remaining manual fixture IDs through shared APIs.
    await page.evaluate(async () => {
      const query = new URLSearchParams({ project: 'engineering-library', document: 'README', language: 'en' });
      const data = await (await fetch(`/api/highlights?${query}`)).json();
      for (const item of data.highlights) await fetch(`/api/highlights/${item.id}?${query}`, { method: 'DELETE', headers: { 'X-Annotation-CSRF': data.csrf_token } });
    });
    await page.locator('.bookmark-ribbon--saved').first().click();
    await page.getByRole('button', { name: 'Bookmark page', exact: true }).first().waitFor();
    await other.reload(); await ready(other);
    assert.equal((await read(other, 'en')).counts.all, 0); assert.equal((await read(other, 'en')).bookmarks.length, 0);
    console.log('PASS shared PostgreSQL: clean startup, CLI seeds/idempotency, two cookie-free browsers, EN/PT-BR filters, manual UI CRUD across refreshes, demonstration-only cleanup');
  } catch (error) { await page.screenshot({ path: '/tmp/shared-annotations-failure.png' }); console.error(await page.locator('[role=toolbar], dialog, .reader-notice').allTextContents()); throw error; } finally { await first.close(); await second.close(); await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
