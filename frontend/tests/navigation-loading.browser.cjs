/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const base = process.env.BROWSER_BASE_URL || 'http://localhost:3000';
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    let delay = 0;
    let releases = [];
    const release = () => { releases.splice(0).forEach(resolve => resolve()); };
    let fail = false;
    await page.route('**/*', async route => {
      if (route.request().headers()['next-router-prefetch']) return route.abort();
      if (route.request().headers().rsc === '1') {
        if (delay) await new Promise(resolve => { releases.push(resolve); });
        if (fail) { fail = false; return route.abort('failed'); }
      }
      await route.continue();
    });
    const ready = async () => {
      await page.locator('.reader[data-pagination="ready"]').waitFor();
      await page.locator('.navigation-loading').waitFor({ state: 'detached' });
    };
    for (const [width, language, label] of [[1440, 'en', 'Loading...'], [320, 'pt-BR', 'Carregando...']]) {
      await page.setViewportSize({ width, height: 900 });
      await page.goto(`${base}/?lang=${language}`, { waitUntil: 'networkidle' });
      delay = 1;
      await page.locator('.project').first().click();
      await page.getByRole('status').filter({ hasText: label }).waitFor();
      assert.equal(await page.locator('.project').count() > 0, true, 'current book remains mounted');
      const box = await page.locator('.navigation-loading__paper').boundingBox();
      assert.ok(box.height < 220, 'compact status surface');
      assert.ok(Math.abs(box.y + box.height / 2 - 450) < 1, 'vertically centered');
      assert.ok(box.x >= 0 && box.x + box.width <= width);
      assert.ok(Math.abs(box.x + box.width / 2 - width / 2) < 1);
      await page.emulateMedia({ reducedMotion: 'reduce' });
      assert.equal(await page.locator('.navigation-loading__quill').evaluate(n => getComputedStyle(n).animationName), 'none');
      await page.screenshot({ path: `/tmp/navigation-loading-${width}.png` });
      delay = 0; release();
      await ready();
      await page.emulateMedia({ reducedMotion: 'no-preference' });
      // A physical turn must retain its existing animation without a loading status.
      const next = page.getByRole('button', { name: language === 'en' ? 'Next page' : 'Próxima página', exact: true });
      if (await next.getAttribute('aria-disabled') === 'false') {
        await next.click();
        await page.locator('.turn-sheet').waitFor();
        assert.equal(await page.locator('.navigation-loading').count(), 0);
        await page.locator('.turn-sheet').waitFor({ state: 'detached' });
        await page.getByRole('button', { name: language === 'en' ? 'Previous page' : 'Página anterior', exact: true }).click();
        await page.locator('.turn-sheet').waitFor({ state: 'detached' });
      }
      const chapter = page.locator('.reader-pages .toc-document a').first();
      const href = await chapter.getAttribute('href');
      delay = 1;
      await chapter.click();
      await page.locator('.navigation-loading').waitFor();
      delay = 0; release();
      await page.waitForURL(url => url.pathname === new URL(href, base).pathname);
      await ready();
      if (language === 'en') {
        // Measurement copies contain the full document, including links on later leaves.
        const markdownLink = page.locator('.reader-measure .reader-markdown a[href^="/projects/"]').filter({ hasNotText: /^$/ }).first();
        assert.ok(await markdownLink.count(), 'document supplies an internal Markdown link');
        delay = 1;
        await markdownLink.evaluate(link => link.click());
        await page.locator('.navigation-loading').waitFor();
        delay = 0; release();
        await ready();
      }
      // Return to contents; allow the cached/instant transition to finish without delay.
      await page.locator('.reader-pages a').filter({ hasText: language === 'en' ? '← Contents' : '← Sumário' }).first().click();
      await ready();
      assert.equal(await page.locator('.navigation-loading').count(), 0);
    }
    await page.goto(`${base}/?lang=en`, { waitUntil: 'networkidle' });
    delay = 1;
    await page.locator('.project').nth(0).click();
    await page.locator('.navigation-loading').waitFor();
    const finalHref = await page.locator('.project').nth(1).getAttribute('href');
    await page.locator('.project').nth(1).click();
    await page.waitForFunction(() => document.querySelector('.navigation-loading'));
    delay = 0; release();
    // Release any consecutive request that reached the route handler in the meantime.
    release();
    await page.waitForURL(url => url.pathname === new URL(finalHref, base).pathname);
    await ready();
    await page.goto(`${base}/?lang=en`, { waitUntil: 'networkidle' });
    await page.clock.install({ time: new Date('2030-01-01T00:00:00Z') });
    await page.clock.pauseAt(new Date('2030-01-01T00:00:01Z'));
    delay = 1;
    await page.locator('.project').first().click();
    await page.clock.fastForward(149);
    assert.equal(await page.locator('.navigation-loading').count(), 0, 'appearance threshold avoids immediate flashes');
    await page.clock.fastForward(51);
    await page.locator('.navigation-loading').waitFor();
    await page.clock.fastForward(30000);
    assert.equal(await page.locator('.navigation-loading').count(), 0, 'stalled navigation cannot trap a loading overlay');
    delay = 0; release();
    await page.clock.resume();
    await ready();
    await page.goto(`${base}/?lang=en`, { waitUntil: 'networkidle' });
    fail = true; delay = 1;
    await page.locator('.project').first().click();
    await page.locator('.navigation-loading').waitFor();
    delay = 0; release();
    await ready();
    assert.deepEqual(errors, []);
    console.log('PASS: slow project/chapter/Markdown transitions, retained book, EN/PT labels, desktop/mobile centering, reduced motion, physical turns, cached contents return, rapid consecutive navigation, stalled request escape, failed RSC recovery, no runtime errors');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
