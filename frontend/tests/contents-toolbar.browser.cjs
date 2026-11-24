/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
(async () => {
 const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
 try {
  for (const width of [1440, 768, 390, 320]) {
   const context = await browser.newContext({ viewport: { width, height: 900 } });
   const page = await context.newPage();
   let bookmarks = [], nextId = 1;
   await page.route('**/api/bookmarks{,?*,/**}', async route => {
    const req = route.request();
    if (req.method() === 'GET') return route.fulfill({ json: { bookmarks, csrf_token: 'fixture' } });
    if (req.method() === 'POST') {
     const saved = { ...req.postDataJSON(), id: nextId++ }; bookmarks.push(saved);
     return route.fulfill({ status: 201, json: saved });
    }
    bookmarks = bookmarks.filter(b => b.id !== Number(new URL(req.url()).pathname.split('/').pop()));
    return route.fulfill({ status: 204 });
   });
   await page.goto(`${process.env.BROWSER_BASE_URL || 'http://localhost:3000'}/projects/engineering-library?lang=en`);
   const ready = async () => { await page.locator('.reader[data-pagination="ready"]').waitFor(); await page.locator('.reader-stage[aria-busy="false"]').waitFor(); };
   await ready();
   const leaves = page.locator('.reader-pages > .reader-leaf');
   const tools = leaves.locator('.reader-toolbar');
   assert.equal(await tools.count(), 1);
   assert.equal(await tools.locator('button').count(), 5); // Includes the inactive ribbon.
   await tools.getByRole('button', { name: 'Chapter index', exact: true }).click();
   assert.ok(await page.locator('dialog a[href*="/docs/"]').count() > 0);
   await page.locator('dialog a[href*="/docs/"]').first().click();
   await page.waitForURL(/\/docs\//); await ready();
   await page.goBack(); await ready();
   await tools.getByRole('button', { name: 'Search', exact: true }).click();
   await page.getByRole('searchbox').fill('architecture');
   await page.locator('dialog a[href*="/docs/"]').first().waitFor();
   const result = page.locator('dialog a[href*="/docs/"]').first();
   assert.ok((await result.getAttribute('href')).includes('lang=en'));
   assert.ok((await result.getAttribute('href')).includes('#'));
   await result.click(); await page.waitForURL(/\/docs\//); await ready();
   assert.ok(page.url().includes('/docs/'));
   await page.goBack(); await ready();
   for (let i = 0; i < await leaves.count(); i++) {
    await leaves.nth(i).getByRole('button', { name: 'Bookmark page', exact: true }).click();
    await leaves.nth(i).locator('.bookmark-ribbon--saved').waitFor();
    assert.equal(await leaves.nth(i).locator('.reader-bookmark-toggle').count(), 0);
   }
   assert.equal(bookmarks.length, width > 920 ? 2 : 1);
   assert.ok(bookmarks.every(b => b.document === '@contents' && !/^\d+$/.test(b.anchor)));
   await page.reload(); await ready();
   assert.equal(await leaves.locator('.bookmark-ribbon--saved').count(), bookmarks.length);
   const anchor = bookmarks.at(-1).anchor;
   await tools.getByRole('button', { name: 'My Bookmarks', exact: true }).click();
   await page.locator(`dialog a[href$="#${encodeURIComponent(anchor)}"]`).click(); await ready();
   await page.waitForFunction(id => [...document.querySelectorAll('.reader-pages [data-unit-id]')].some(el => el.dataset.unitId === id), anchor);
   await page.setViewportSize({ width: width > 920 ? 390 : 1440, height: 900 }); await ready();
   await page.waitForFunction(id => [...document.querySelectorAll('.reader-pages [data-unit-id]')].some(el => el.dataset.unitId === id), anchor);
   await leaves.locator('.lang').filter({ hasText: 'Português' }).click(); await page.waitForURL(/lang=pt-BR/); await ready();
   assert.ok(page.url().includes('lang=pt-BR'));
   await page.waitForFunction(id => [...document.querySelectorAll('.reader-pages [data-unit-id]')].some(el => el.dataset.unitId === id), anchor);
   const geometry = await leaves.evaluateAll(nodes => nodes.map((leaf, index) => {
    const body = leaf.querySelector('.reader-body').getBoundingClientRect();
    const header = leaf.querySelector('header');
    const control = leaf.querySelector('.reader-page-bookmark');
    const probe = document.querySelector(index ? '.reader-probe--right .reader-body' : '.reader-probe--left .reader-body');
    return { clear: body.top >= (header || control).getBoundingClientRect().bottom, equal: Math.abs(body.height - probe.getBoundingClientRect().height) < 1 };
   }));
   assert.ok(geometry.every(g => g.clear && g.equal), JSON.stringify(geometry));
   assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
   await page.screenshot({ path: `/tmp/contents-toolbar-${width}.png` });
   console.log(`contents toolbar ${width}: passed`);
   await context.close();
  }
 } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
