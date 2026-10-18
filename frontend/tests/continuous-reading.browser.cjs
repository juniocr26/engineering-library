/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const base = process.env.BROWSER_BASE_URL || 'http://localhost:3000';
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  try {
    for (const width of [390, 768, 1440]) for (const language of ['en', 'pt-BR']) {
      const context = await browser.newContext({ viewport: { width, height: 900 }, reducedMotion: width === 768 ? 'reduce' : 'no-preference' });
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      const ready = () => page.locator('.reader[data-pagination="ready"] .reader-stage[aria-busy="false"]').waitFor();
      const controls = () => page.locator('.reader-pages .reader-controls');
      const indicator = () => controls().locator('span[aria-live]').innerText();
      const first = () => controls().locator('button').first();
      const last = () => controls().locator('button').last();
      async function cross(button, href, direction) {
        await button.click();
        if (width === 768) assert.equal(await page.locator('.turn-sheet').count(), 0);
        if (width !== 768) {
          await page.locator(`.turn-sheet--${direction}`).waitFor();
          assert.equal(await button.getAttribute('aria-disabled'), 'true');
        }
        await page.waitForURL(url => url.pathname + url.search === href);
        await ready();
      }
      try {
        const toc = `/projects/engineering-library?lang=${language}`;
        await page.goto(`${base}${toc}`); await ready();
        const order = await page.locator('.reader-probe--left a[href*="/docs/"]').evaluateAll(links => links.map(link => new URL(link.href).pathname + new URL(link.href).search));
        assert.ok(order.length > 2);
        // Ordinary physical-page turns retain their indicator and history location.
        const initial = await indicator();
        await last().click(); await page.waitForFunction(text => document.querySelector('.reader-pages [aria-live]')?.textContent !== text, initial); await ready();
        await first().click(); await page.waitForFunction(text => document.querySelector('.reader-pages [aria-live]')?.textContent === text, initial); await ready();
        await page.goto(`${base}${toc}&edge=end`); await ready();
        const tocEnd = await indicator();
        assert.ok(await last().locator('svg').count());
        await cross(last(), order[0], 'forward');
        assert.match(await indicator(), /(?:Page|Página) 1(?:–2)? (?:of|de) \d+/);
        await cross(first(), `${toc}&edge=end`, 'backward');
        assert.equal(await indicator(), tocEnd);
        await cross(last(), order[0], 'forward');
        await page.goto(`${base}${order[0]}&edge=end`); await ready();
        const docEnd = await indicator();
        await cross(last(), order[1], 'forward');
        await cross(first(), `${order[0]}&edge=end`, 'backward');
        assert.equal(await indicator(), docEnd);
        await page.goBack(); await ready(); assert.equal(new URL(page.url()).pathname + new URL(page.url()).search, order[1]);
        await page.goForward(); await ready(); assert.equal(await indicator(), docEnd);
        // Last document terminates the book without wrapping.
        await page.goto(`${base}${order.at(-1)}&edge=end`); await ready();
        assert.equal(await last().getAttribute('aria-disabled'), 'true');
        assert.equal(await last().locator('svg').count(), 0);
        // Direct document URLs start on their first physical page.
        await page.goto(`${base}${order[1]}`); await ready();
        assert.match(await indicator(), /(?:Page|Página) 1(?:–2)? (?:of|de) \d+/);
        assert.ok(await first().locator('svg').count());
        // Cross a category boundary using the actual canonical metadata rendered by the TOC.
        const boundary = order.findIndex((href, index) => index > 0 && href.split('/docs/')[1].split('/')[0] !== order[index - 1].split('/docs/')[1].split('/')[0]);
        assert.ok(boundary > 0);
        await page.goto(`${base}${order[boundary - 1]}&edge=end`); await ready();
        await cross(last(), order[boundary], 'forward');
        await cross(first(), `${order[boundary - 1]}&edge=end`, 'backward');
        await page.setViewportSize({ width: width === 1440 ? 390 : 1440, height: 900 }); await ready();
        assert.equal(await last().getAttribute('aria-disabled'), 'false');
        assert.deepEqual(errors, []);
        console.log(`PASS continuous reading ${width}px ${language}, motion=${width === 768 ? 'reduced' : 'normal'}`);
      } finally { await context.close(); }
    }
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
