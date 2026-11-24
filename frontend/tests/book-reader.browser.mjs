/* Run against a development server so React reconciliation warnings are enabled.
 * Playwright is supplied by the test environment; no application dependency is required.
 * Example: PLAYWRIGHT_MODULE=/path/to/playwright BOOK_READER_URL=http://localhost:3099 npm run test:browser
 */
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
const loadPlaywright = createRequire(import.meta.url);
const { chromium } = loadPlaywright(process.env.PLAYWRIGHT_MODULE || 'playwright');

async function ready(page) {
  await page.locator('.reader[data-pagination="ready"]').waitFor();
  await page.locator('.reader-stage[aria-busy="false"]').waitFor();
}

async function inspectTurn(page, direction) {
  const sheet = page.locator('.turn-sheet');
  await sheet.waitFor({ state: 'attached' });
  const state = await page.evaluate(() => {
    const leaves = [...document.querySelectorAll('.reader-pages > .reader-leaf')];
    const faces = [...document.querySelectorAll('.turn-face > .reader-leaf')];
    const concealed = [...leaves, ...faces].filter(leaf => leaf.dataset.contentConcealed === 'true');
    return {
      leaves: leaves.map(leaf => leaf.dataset.contentConcealed === 'true'),
      faces: faces.length,
      hidden: concealed.every(leaf => leaf.inert && leaf.getAttribute('aria-hidden') === 'true' &&
        [...leaf.querySelectorAll('.reader-body, .book-unit, a, button')].every(node => getComputedStyle(node).visibility === 'hidden')),
      parchment: concealed.every(leaf => getComputedStyle(leaf.querySelector('.manuscript-decorations')).visibility === 'visible'),
      geometry: concealed.every(leaf => leaf.getBoundingClientRect().height > 0 && leaf.querySelector('.reader-body').clientHeight > 0),
    };
  });
  assert.equal(state.faces, 2);
  assert.equal(state.hidden, true, 'turning and destination content must be hidden and inert');
  assert.equal(state.parchment, true, 'manuscript decorations must remain visible');
  assert.equal(state.geometry, true, 'concealing content must preserve layout');
  assert.deepEqual(state.leaves, state.leaves.length === 1 ? [true] : direction === 1 ? [false, true] : [true, false]);
}

async function turnAndReturn(page) {
  const leaves = page.locator('.reader-pages');
  const controls = leaves.locator('.reader-controls');
  const before = await controls.locator('[aria-live]').innerText();
  const identity = await leaves.locator('.reader-leaf').first().getAttribute('data-page-id');
  const next = controls.locator('button').last();
  assert.equal(await next.getAttribute('aria-disabled'), 'false', 'fixture must have multiple physical pages');
  await next.click();
  await inspectTurn(page, 1);
  await page.waitForFunction(text => document.querySelector('.reader-pages [aria-live]')?.textContent !== text, before);
  await ready(page);
  assert.notEqual(await leaves.locator('.reader-leaf').first().getAttribute('data-page-id'), identity);
  await controls.locator('button').first().click();
  await inspectTurn(page, -1);
  await page.waitForFunction(text => document.querySelector('.reader-pages [aria-live]')?.textContent === text, before);
  await ready(page);
  assert.equal(await leaves.locator('.reader-leaf').first().getAttribute('data-page-id'), identity);
  assert.equal(await leaves.locator('[data-content-concealed="true"]').count(), 0);
}

async function openDocument(page) {
  const link = page.locator('.reader-pages a[href*="/docs/guides/application-development.md?"]').first();
  while (!(await link.isVisible())) {
    const controls = page.locator('.reader-pages .reader-controls');
    const before = await controls.locator('[aria-live]').innerText();
    const next = controls.locator('button').last();
    assert.equal(await next.getAttribute('aria-disabled'), 'false', 'Document must be reachable through the table of contents');
    await next.click();
    await page.waitForFunction(text => document.querySelector('.reader-pages [aria-live]')?.textContent !== text, before);
    await ready(page);
  }
  await link.click();
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    for (const width of [390, 768, 1440]) {
      const context = await browser.newContext({ viewport: { width, height: 900 } });
      const page = await context.newPage();
      page.setDefaultTimeout(30_000);
      const errors = [];
      page.on('console', message => {
        if (message.type() === 'error' || message.type() === 'warning') {
          errors.push(message.text());
          console.error(message.text());
        }
      });
      page.on('pageerror', error => errors.push(error.message));
      try {
        const base = process.env.BOOK_READER_URL || 'http://localhost:3099';
        await page.goto(`${base}/?lang=pt-BR`);
        await page.locator('a[href*="/projects/engineering-library?"]').first().click();
        await page.waitForURL('**/projects/engineering-library?**');
        await ready(page);
        assert.equal(await page.locator('.reader').getAttribute('data-mode'), width > 920 ? 'spread' : 'single-page');
        assert.equal(await page.locator('.reader-pages .toc-header h1').innerText(), 'Sumário');
        assert.equal(await page.locator('.reader-probe--left .toc-header').count(), 1);
        await turnAndReturn(page);

        await page.emulateMedia({ reducedMotion: 'reduce' });
        const originalPage = await page.locator('.reader-pages [aria-live]').innerText();
        await page.locator('.reader-pages .reader-controls button').last().click();
        await ready(page);
        assert.notEqual(await page.locator('.reader-pages [aria-live]').innerText(), originalPage);
        assert.equal(await page.locator('.turn-sheet, .reader-pages [data-content-concealed="true"]').count(), 0);
        await page.locator('.reader-pages .reader-controls button').first().click();
        await ready(page);
        assert.equal(await page.locator('.reader-pages [aria-live]').innerText(), originalPage);
        await page.emulateMedia({ reducedMotion: 'no-preference' });

        await page.locator('.reader-pages .toc-header a[hreflang="en"]').click();
        await page.waitForFunction(() => document.querySelector('main')?.lang === 'en');
        await ready(page);
        assert.equal(await page.locator('.reader-pages .toc-header h1').innerText(), 'Table of Contents');
        await openDocument(page);
        await page.locator('.reader-pages .reader-document-header').waitFor();
        await ready(page);
        assert.equal(await page.locator('.reader-pages .reader-document-header').count(), 1);
        await turnAndReturn(page);

        await page.locator('.reader-pages .reader-document-languages a[hreflang="pt-BR"]').click();
        await page.waitForFunction(() => document.querySelector('main')?.lang === 'pt-BR');
        await ready(page);
        assert.equal(await page.locator('main').getAttribute('lang'), 'pt-BR');
        await page.locator('.reader-pages .reader-document-header > a').click();
        await page.locator('.reader-pages .toc-header').waitFor();
        await ready(page);
        assert.equal(await page.locator('.reader-pages .toc-header h1').innerText(), 'Sumário');
        assert.deepEqual(errors, [], 'reader navigation must not emit console warnings or errors');
        console.log(`PASS ${width}px: catalog, header, pagination, languages, documents and console`);
      } finally {
        await context.close();
      }
    }
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
