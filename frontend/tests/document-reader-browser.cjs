/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext();
  const page = await context.newPage();
  const base = process.env.BROWSER_BASE_URL || 'http://localhost:3000';
  const errors = []; page.on('pageerror', error => errors.push(error.message));
  const ready = () => page.waitForFunction(() => document.querySelector('.reader[data-pagination="ready"]'));
  const controls = () => page.locator('.reader-pages .reader-controls span');
  async function verifyMeasuredTotal() {
    await ready();
    const expected = await page.evaluate(() => {
      const left = document.querySelector('.reader-probe--left .reader-body');
      const right = document.querySelector('.reader-probe--right .reader-body');
      const spread = document.querySelector('.reader').dataset.mode === 'spread';
      const units = [...left.children];
      let total = 1, used = 0, entries = 0;
      units.forEach((node, index) => {
        const height = node.getBoundingClientRect().height;
        const following = node.querySelector('h1,h2,h3,h4,h5,h6') ? units[index + 1]?.getBoundingClientRect().height || 0 : 0;
        const capacity = spread && total % 2 === 0 ? right.clientHeight : left.clientHeight;
        if (entries && used + height + following > capacity) { total++; used = 0; entries = 0; }
        entries++; used += height;
      });
      return total;
    });
    assert.equal(Number((await controls().innerText()).match(/\d+$/)[0]), expected);
  }
  for (const width of [1440, 768, 390, 320]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto(`${base}/?lang=en`, { waitUntil: 'networkidle' });
    await page.locator('.project').filter({ hasText: 'Engineering Library' }).click();
    await ready();
    const link = page.locator('.reader-pages a[href*="/docs/architecture/current-state.md"]').first();
    assert.match(await link.getAttribute('href'), /^\/projects\//);
    await link.click();
    await page.waitForURL(/\/docs\/architecture\/current-state\.md/);
    await ready();
    assert.ok(page.url().startsWith(base));
    assert.match(await page.locator('.reader-pages').innerText(), /Engineering Library: current architecture/);
    assert.match(await controls().innerText(), /^Page 1(?:–2)? of \d+$/);
    await verifyMeasuredTotal();
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await page.reload({ waitUntil: 'networkidle' }); await ready();
    assert.match(await page.locator('.reader-pages').innerText(), /current architecture/);
    await page.goBack(); await ready();
    assert.ok(!page.url().includes('/docs/'));
    await page.goForward(); await ready();
    assert.match(await page.locator('.reader-pages').innerText(), /current architecture/);
    await page.locator('.reader-pages').getByRole('button', { name: 'Chapter index', exact: true }).click();
    await page.getByRole('dialog').getByRole('link', { name: 'Security and unresolved evidence', exact: true }).click();
    await page.waitForFunction(() => [...document.querySelectorAll('.reader-pages [data-unit-id]')].some(node => node.dataset.unitId === 'security-and-unresolved-evidence'));
    const anchor = 'security-and-unresolved-evidence';
    await page.setViewportSize({ width: width === 1440 ? 390 : 1440, height: 850 });
    await ready(); await page.waitForTimeout(200);
    assert.ok(await page.locator(`.reader-pages [data-unit-id="${anchor}"]`).count());
    await verifyMeasuredTotal();
    // Reopening the same hash after manually turning pages must jump again.
    const previous = page.locator('.reader-pages').getByRole('button', { name: 'Previous page', exact: true });
    if (await previous.getAttribute('aria-disabled') === 'false') {
      await page.emulateMedia({ reducedMotion: 'reduce' });
      await previous.click();
      await page.locator('.reader-pages').getByRole('button', { name: 'Chapter index', exact: true }).click();
      await page.getByRole('dialog').getByRole('link', { name: 'Security and unresolved evidence', exact: true }).click();
      await page.waitForFunction(() => [...document.querySelectorAll('.reader-pages [data-unit-id]')].some(node => node.dataset.unitId === 'security-and-unresolved-evidence'));
    }
    await page.screenshot({ path: `/tmp/document-reader-${width}.png`, fullPage: true });
  }

  // Project-scoped search resolves a block, its physical page, and a red highlight.
  await page.locator('.reader-pages').getByRole('button', { name: 'Search', exact: true }).click();
  await page.getByRole('searchbox').fill('PostgreSQL');
  const results = page.getByRole('dialog').locator('li a');
  await results.first().waitFor();
  assert.match(await results.first().getAttribute('href'), /^\/projects\/engineering-library\/docs\//);
  await results.first().click();
  await ready();
  await verifyMeasuredTotal();
  await page.locator('.reader-pages mark').first().waitFor();
  assert.match(await page.locator('.reader-pages mark').first().innerText(), /postgresql/i);
  const savedURL = page.url();

  // Both visible leaves expose independent stable bookmarks; the cookie is HttpOnly.
  const save = page.locator('.reader-pages').getByRole('button', { name: 'Bookmark page', exact: true }).first();
  await save.click();
  await page.locator('.reader-pages .bookmark-ribbon--saved').first().waitFor();
  assert.equal((await context.cookies()).length, 0);
  await page.reload({ waitUntil: 'networkidle' }); await ready();
  await page.locator('.reader-pages .bookmark-ribbon--saved').first().waitFor();
  await page.locator('.reader-pages').getByRole('button', { name: 'My Bookmarks', exact: true }).click();
  const bookmarkLink = page.getByRole('dialog').locator('li a').first();
  const bookmarkURL = await bookmarkLink.getAttribute('href');
  assert.match(bookmarkURL, /^\/projects\/engineering-library\/docs\/.*#/);
  await bookmarkLink.click(); await ready();
  assert.equal(new URL(page.url()).pathname, new URL(savedURL).pathname);
  await page.locator('.reader-pages .bookmark-ribbon--saved').first().waitFor();
  await page.locator('.reader-pages').getByRole('button', { name: 'My Bookmarks', exact: true }).click();
  await page.getByRole('dialog').getByRole('button', { name: 'Remove bookmark', exact: true }).click();
  await page.getByRole('dialog').getByText('No bookmarks yet.', { exact: true }).waitFor();
  await page.keyboard.press('Escape');
  assert.equal(await page.locator('dialog').count(), 0);

  // Relative Markdown links and a real Mermaid diagram use the same reader.
  await page.goto(`${base}/projects/env-auditor/docs/architecture/overview.md?lang=en`, { waitUntil: 'networkidle' });
  await ready();
  await page.locator('.reader-pages .reader-diagram svg').first().waitFor();
  await page.waitForTimeout(300);
  const changes = await page.evaluate(async () => {
    let mutations = 0;
    const observer = new MutationObserver(records => { mutations += records.length; });
    observer.observe(document.querySelector('.reader'), { attributes: true, attributeFilter: ['data-pagination'] });
    await new Promise(resolve => setTimeout(resolve, 600));
    observer.disconnect(); return mutations;
  });
  assert.equal(changes, 0, 'settled diagrams must not cause repagination loops');
  assert.equal(await page.locator('.reader-pages .reader-markdown a').filter({ hasText: 'README' }).first().getAttribute('href'), '/projects/env-auditor/docs/README?lang=en');
  await page.locator('.reader-pages .reader-markdown a').filter({ hasText: 'README' }).first().click();
  await page.waitForURL(/\/docs\/README/); await ready();
  await page.locator('.reader-pages .reader-document-languages').getByRole('link', { name: 'Português' }).click();
  await page.waitForURL(/lang=pt-BR/); await ready();
  assert.match(await controls().innerText(), /^Página \d+(?:–\d+)? de \d+$/);
  await page.emulateMedia({ reducedMotion: 'reduce' });
  const before = await controls().innerText();
  const next = page.locator('.reader-pages').getByRole('button', { name: 'Próxima página', exact: true });
  if (await next.getAttribute('aria-disabled') === 'false') { await next.click(); assert.notEqual(await controls().innerText(), before); }

  const invalid = await page.goto(`${base}/projects/env-auditor/docs/not-a-document.md?lang=en`);
  // Next's parent loading boundary can stream a 200 before notFound resolves.
  assert.ok([200, 404].includes(invalid.status()));
  await page.getByRole('heading', { name: /Document not found/ }).waitFor();
  assert.match(await page.locator('body').innerText(), /Document not found/);
  const traversal = await context.request.get(`${base}/api/document-assets/env-auditor/%252e%252e/secret.png`);
  assert.equal(traversal.status(), 404);
  const image = await context.request.get(`${base}/api/document-assets/engineering-library/bio/icon.svg`);
  assert.equal(image.status(), 200);
  assert.match(image.headers()['content-type'], /image\/svg\+xml/);
  assert.match(image.headers()['content-security-policy'], /sandbox/);
  const outsider = await browser.newContext();
  const response = await outsider.request.get(`${base}/api/bookmarks?language=en`);
  const original = await context.request.get(`${base}/api/bookmarks?language=en`);
  assert.deepEqual((await response.json()).bookmarks, (await original.json()).bookmarks);
  assert.deepEqual(errors, []);
  await browser.close();
  console.log('PASS: catalog → TOC → real Markdown reader at four widths, refresh/history, chapter anchors/reflow, search highlight, shared PostgreSQL bookmark reload/removal/cross-browser visibility, relative links, Mermaid, bilingual totals, navigation, safe 404');
})().catch(error => { console.error(error); process.exit(1); });
