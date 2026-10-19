/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const base = process.env.BOOK_READER_URL || 'http://localhost:3000';
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  try {
    for (const width of [1728, 390]) {
      const page = await browser.newPage({ viewport: { width, height: 980 }, reducedMotion: 'reduce' });
      page.setDefaultTimeout(30000);
      const ready = () => page.locator('.reader[data-pagination="ready"] .reader-stage[aria-busy="false"]').waitFor();
      const current = () => page.evaluate(() => window.history.state?.bookLocation?.anchor);
      const folio = () => page.locator('.reader-pages .reader-controls span[aria-live]').innerText();
      const switchTo = async lang => {
        await page.locator(`.reader-pages a[hreflang="${lang}"]`).click();
        await page.waitForURL(url => url.searchParams.get('lang') === lang);
        await ready();
        await page.waitForFunction(() => /^q005\b/i.test(window.history.state?.bookLocation?.anchor || ''));
      };
      let releaseFont;
      let fontRequested;
      const fontGate = new Promise(resolve => { releaseFont = resolve; });
      const fontSeen = new Promise(resolve => { fontRequested = resolve; });
      await page.route('**/*.ttf', async route => { fontRequested(); await fontGate; await route.continue(); });
      await page.goto(`${base}/projects/go-image-optimizer/docs/faq/index.md?lang=pt-BR`, { waitUntil: 'domcontentloaded' });
      await fontSeen;
      assert.equal(await page.locator('.reader').getAttribute('data-pagination'), 'measuring');
      releaseFont();
      await ready();
      // Ordinary page turns capture the first content on the left leaf.
      let found = false;
      for (let turn = 0; turn < 220; turn++) {
        const first = await page.locator('.reader-pages .book-unit').first().getAttribute('data-unit-id');
        if (/^q005\b/i.test(first)) { found = true; break; }
        if (/^q006\b/i.test(first)) break;
        await page.locator('.reader-pages .reader-controls button').last().click();
        await ready();
      }
      assert.ok(found, 'ordinary reading must reach Q005');
      const pt = await folio();
      await switchTo('en');
      const en = await folio();
      assert.notEqual(pt.match(/\d+$/)[0], en.match(/\d+$/)[0], 'translations have different physical totals');
      await switchTo('pt-BR');
      assert.match(await current(), /^q005\b/i);
      let releaseImage;
      let imageRequested;
      const imageGate = new Promise(resolve => { releaseImage = resolve; });
      const imageSeen = new Promise(resolve => { imageRequested = resolve; });
      await page.route('**/__reader_delayed_image.svg', async route => {
        imageRequested(); await imageGate;
        await route.fulfill({ contentType: 'image/svg+xml', body: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"/>' });
      });
      await page.evaluate(() => {
        const image = document.createElement('img');
        image.src = '/__reader_delayed_image.svg';
        document.querySelector('.reader-measure .book-unit').append(image);
      });
      await imageSeen;
      await page.locator('.reader[data-pagination="measuring"]').waitFor();
      releaseImage(); await ready();
      assert.match(await current(), /^q005\b/i);
      // Issue the reverse switch as soon as the target header becomes available.
      await page.locator('.reader-pages a[hreflang="en"]').click();
      await page.waitForURL(url => url.searchParams.get('lang') === 'en');
      await page.locator('.reader-pages a[hreflang="pt-BR"]').click();
      await page.waitForURL(url => url.searchParams.get('lang') === 'pt-BR');
      await ready();
      assert.match(await current(), /^q005\b/i);
      await page.setViewportSize({ width: width === 390 ? 430 : 1000, height: 850 });
      await ready();
      await switchTo('en');
      console.log(`PASS FAQ Q005 ${width}px: ${pt} -> ${en}; round trip, rapid toggle, resize, delayed font/image`);
      await page.close();
    }
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
