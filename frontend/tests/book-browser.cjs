/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage({ hasTouch: true });
  const errors = []; page.on('pageerror', e => errors.push(e.message));
  page.on('console', message => { if (message.type() === 'error' && /hydrat/i.test(message.text())) errors.push(message.text()); });
  const base = process.env.BROWSER_BASE_URL || 'http://localhost:3000';
  const ids = () => page.locator('.reader-pages .reader-leaf').evaluateAll(nodes => nodes.map(n => n.dataset.pageId));
  // Independently pack browser geometry and compare it with the published total.
  async function verifyTotal() {
    await page.waitForFunction(() => document.querySelector('.reader[data-pagination="ready"]'));
    const expected = await page.evaluate(() => {
      const spread = document.querySelector('.reader').dataset.mode === 'spread';
      const left = document.querySelector('.reader-probe--left .reader-body');
      const right = document.querySelector('.reader-probe--right .reader-body');
      const units = [...left.children];
      let pages = 1, used = 0, entries = 0;
      units.forEach((unit, index) => {
        const height = unit.getBoundingClientRect().height;
        const following = unit.querySelector('.toc-chapter > span') ? units[index + 1]?.getBoundingClientRect().height || 0 : 0;
        const capacity = spread && pages % 2 === 0 ? right.clientHeight : left.clientHeight;
        if (entries && used + height + following > capacity) { pages++; used = 0; entries = 0; }
        used += height; entries++;
      });
      return pages;
    });
    const label = await page.locator('.reader-pages .reader-controls span').innerText();
    assert.equal(Number(label.match(/(\d+)$/)[1]), expected, label);
    return expected;
  }
  for (const width of [1440, 768, 390, 320]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto(`${base}/projects/engineering-library?lang=en`, { waitUntil: 'networkidle' });
    await page.waitForFunction(() => document.querySelector('.reader[data-pagination="ready"]'));
    assert.match(await page.locator('.reader-pages .reader-controls span').innerText(), /^Page 1(?:–2)? of [1-9]\d*$/);
    await verifyTotal();
    assert.equal(await page.locator('.reader').getAttribute('data-mode'), width > 920 ? 'spread' : 'single-page');
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    const original = await ids();
    const marks = await page.locator('.reader-pages .manuscript-decorations').first().innerHTML();
    const next = page.getByRole('button', { name: 'Next page', exact: true });
    const previous = page.getByRole('button', { name: 'Previous page', exact: true });
    await next.click();
    await page.locator('.turn-sheet--forward').waitFor();
    assert.equal(await page.locator('.turn-sheet').evaluate(n => getComputedStyle(n).animationName), 'book-forward');
    await next.click({ force: true });
    assert.equal(await page.locator('.turn-sheet').count(), 1);
    await page.locator('.turn-sheet').waitFor({ state: 'detached' });
    assert.notDeepEqual(await ids(), original);
    await previous.click();
    await page.locator('.turn-sheet--backward').waitFor();
    assert.equal(await page.locator('.turn-sheet').evaluate(n => getComputedStyle(n).animationName), 'book-backward');
    await page.locator('.turn-sheet').waitFor({ state: 'detached' });
    assert.deepEqual(await ids(), original);
    assert.equal(await page.locator('.reader-pages .manuscript-decorations').first().innerHTML(), marks);
    await page.reload({ waitUntil: 'networkidle' });
    assert.deepEqual(await ids(), original);
    assert.equal(await page.locator('.reader-pages .manuscript-decorations').first().innerHTML(), marks);
    await page.screenshot({ path: `/tmp/book-${width}.png`, fullPage: true });
    if (width <= 768) {
      const cdp = await page.context().newCDPSession(page);
      const box = await page.locator('.reader-stage').boundingBox();
      const y = box.y + 12;
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: width - 35, y }] });
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: 35, y }] });
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
      await page.locator('.turn-sheet').waitFor({ state: 'detached' });
      assert.notDeepEqual(await ids(), original);
      await page.emulateMedia({ reducedMotion: 'reduce' });
      await previous.click();
      assert.deepEqual(await ids(), original);
      await page.locator('.reader-pages .toc-mobile-menu summary').click();
      assert.ok(await page.locator('.reader-pages .toc-mobile-menu a').isVisible());
      await page.locator('.reader-pages .toc-mobile-menu summary').click();
    }
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await next.focus(); await page.keyboard.press('ArrowRight');
    assert.equal(await page.locator('.turn-sheet').count(), 0);
    assert.notDeepEqual(await ids(), original);
    const anchor = JSON.parse((await ids())[0])[0];
    await page.setViewportSize({ width: width === 1440 ? 390 : 1440, height: 900 });
    await page.waitForTimeout(250);
    assert.ok((await ids()).some(id => JSON.parse(id).includes(anchor)));
    await verifyTotal();
    const numbers = await page.locator('.reader-measure .chapter-number').allTextContents();
    await page.getByRole('link', { name: 'Português', exact: true }).click();
    await page.waitForURL(/lang=pt-BR/); await page.waitForLoadState('networkidle');
    await page.waitForFunction(() => document.querySelector('.reader[data-pagination="ready"]'));
    assert.match(await page.locator('.reader-pages .reader-controls span').innerText(), /^Página \d+(?:–\d+)? de [1-9]\d*$/);
    await verifyTotal();
    assert.deepEqual(await page.locator('.reader-measure .chapter-number').allTextContents(), numbers);
    await page.emulateMedia({ reducedMotion: 'no-preference' });
  }
  // Traverse every spread through the final odd/even leaf; no phantom blank page is counted.
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto(`${base}/projects/engineering-library?lang=en`, { waitUntil: 'networkidle' });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  const total = await verifyTotal();
  const next = page.getByRole('button', { name: 'Next page', exact: true });
  let start = 1;
  while (await next.getAttribute('aria-disabled') === 'false') {
    await next.click(); start += 2;
    assert.equal(await page.locator('.reader-pages .reader-controls span').innerText(), `Page ${start}${start < total ? `–${start + 1}` : ''} of ${total}`);
  }
  assert.equal(start + (start < total ? 1 : 0), total);
  // Actual font metrics change without a viewport event.
  const fontOverride = await page.addStyleTag({ content: '.reader .toc-document{font-size:28px!important;line-height:2!important}' });
  await page.waitForTimeout(250);
  assert.ok(await verifyTotal() > total);
  await fontOverride.evaluate(node => node.remove());
  await page.waitForTimeout(250);
  assert.equal(await verifyTotal(), total);
  assert.deepEqual(errors, []);
  console.log('PASS: desktop/tablet/mobile, forward/backward geometry, rapid navigation lock, content continuity, stable reload textures, keyboard, touch swipes, mobile menu, bilingual numbering, reduced motion, resize anchor, no horizontal overflow/runtime errors');
  await browser.close();
})().catch(error => { console.error(error); process.exit(1); });
