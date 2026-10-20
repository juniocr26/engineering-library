/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const inspectAnchors = require('../tools/demo-anchors.cjs');
const base = process.env.BROWSER_BASE_URL || 'http://localhost:3099';
const documents = ['architecture/current-state.md', 'img/visual-components.md'];
const ready = page => page.locator('.reader[data-pagination="ready"]').waitFor();
const read = (page, language) => page.evaluate(async language => {
  const annotations = await (await fetch(`/api/annotations?project=engineering-library&language=${language}`)).json();
  const bookmarks = await (await fetch(`/api/bookmarks?project_slug=engineering-library&language=${language}`)).json();
  return { counts: annotations.counts, bookmarks: bookmarks.bookmarks };
}, language);
(async () => {
  assert.ok(['localhost', '127.0.0.1'].includes(new URL(base).hostname));
  const browser = await chromium.launch({ executablePath: process.env.PLAYWRIGHT_EXECUTABLE_PATH, headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
  const page = await context.newPage(); page.setDefaultTimeout(90000);
  const visit = async (doc, lang) => { await page.goto(`${base}/projects/engineering-library/docs/${doc}?lang=${lang}&noteDemos=1`); await ready(page); };
  const seed = async () => {
    await page.locator('.note-demo-tools summary').click();
    await page.getByRole('button', { name: 'Seed current reader', exact: true }).click();
    await page.locator('.note-demo-tools [role=status]').filter({ hasText: /cases saved|casos salvos/ }).waitFor();
  };
  try {
    await visit(documents[0], 'en');
    assert.equal((await read(page, 'en')).counts.all, 0);
    assert.equal((await read(page, 'en')).bookmarks.length, 0);
    await page.getByRole('button', { name: 'My Bookmarks', exact: true }).click();
    await page.getByText('No bookmarks saved for this project.', { exact: true }).waitFor();
    await page.keyboard.press('Escape');
    for (const lang of ['en', 'pt-BR']) for (const doc of documents) {
      await visit(doc, lang); await seed();
      assert.equal((await inspectAnchors(page, doc, lang)).filter(item => !item.valid).length, 0);
      // No reload: both the toolbar's existing bookmark state and live indicators refresh.
      await page.locator('[data-note-id]').first().waitFor();
      await page.locator('.bookmark-ribbon--saved').first().waitFor();
      await page.getByRole('button', { name: lang === 'en' ? 'My Bookmarks' : 'Minhas marcações', exact: true }).click();
      const expected = doc === documents[0] ? 3 : 6;
      await page.waitForFunction(expected => document.querySelectorAll('.reader-saved-bookmark').length === expected, expected);
      await page.keyboard.press('Escape');
      await page.getByRole('button', { name: 'Seed current reader', exact: true }).click();
      await page.locator('.note-demo-tools [role=status]').filter({ hasText: /cases saved|casos salvos/ }).waitFor();
      // Wait for the second run to finish, not the first run's status text.
      await page.getByRole('button', { name: 'Seed current reader', exact: true }).waitFor({ state: 'visible' });
      await page.waitForFunction(() => !Array.from(document.querySelectorAll('button')).find(b => b.textContent === 'Seed current reader').disabled);
      console.log(`PASS immediate refresh and idempotence: ${lang} ${doc}`);
    }
    for (const lang of ['en', 'pt-BR']) {
      await visit(documents[0], lang);
      const data = await read(page, lang);
      assert.deepEqual(data.counts, { yellow: 6, blue: 4, pink: 4, orange: 4, purple: 4, red: 4, green: 4, notes: 30, all: 32 });
      assert.equal(data.bookmarks.length, 6);
      const english = lang === 'en';
      await page.getByRole('button', { name: english ? 'Highlights and Notes' : 'Destaques e notas', exact: true }).click();
      const panel = page.locator('.annotation-list'); await panel.locator('.annotation-entry').first().waitFor();
      const names = english ? ['Yellow', 'Blue', 'Pink', 'Orange', 'Purple', 'Red', 'Green', 'Notes'] : ['Amarelo', 'Azul', 'Rosa', 'Laranja', 'Roxo', 'Vermelho', 'Verde', 'Notas'];
      for (let i = 0; i < names.length; i++) {
        const count = i === 0 ? 6 : i === 7 ? 30 : 4;
        await page.getByRole('button', { name: english ? 'Filter annotations' : 'Filtrar anotações', exact: true }).click();
        await page.getByRole('menuitemradio', { name: `${names[i]} (${count})`, exact: true }).click();
        await page.waitForFunction(n => document.querySelector('.annotation-list')?.getAttribute('aria-busy') === 'false' && document.querySelectorAll('.annotation-entry').length === Math.min(n, 20), count);
      }
      await page.screenshot({ path: `/tmp/demo-visibility-${lang}.png` });
      await page.keyboard.press('Escape');
      await page.reload(); await ready(page);
      assert.equal((await read(page, lang)).counts.notes, 30);
    }
    const stranger = await browser.newContext(); const other = await stranger.newPage();
    await other.goto(`${base}/projects/engineering-library/docs/${documents[0]}?lang=en`); await ready(other);
    assert.equal((await read(other, 'en')).counts.all, 0); await stranger.close();
    // Cleanup is explicitly invoked only for the temporary context created by this test.
    await page.locator('.note-demo-tools summary').click();
    await page.getByRole('button', { name: 'Remove demonstration records', exact: true }).click();
    await page.locator('.note-demo-tools [role=status]').filter({ hasText: /removed|removidas/ }).waitFor();
    await page.waitForFunction(() => !document.querySelector('[data-note-id]') && !document.querySelector('.bookmark-ribbon--saved'));
    for (const lang of ['en', 'pt-BR']) {
      const data = await read(page, lang); assert.equal(data.counts.all, 0); assert.equal(data.bookmarks.length, 0);
    }
    console.log('PASS fresh reader, project listing, seven colors, language isolation, reload, reader isolation and explicit temporary-reader cleanup');
  } finally { await context.close(); await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
