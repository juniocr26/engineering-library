/* eslint-disable @typescript-eslint/no-require-imports */
// Run with Playwright installed outside the application dependency tree.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const base = process.env.BROWSER_BASE_URL || 'http://127.0.0.1:3100';
  for (const width of [1440, 1024, 768, 390, 320]) {
    await page.setViewportSize({ width, height: 1000 });
    await page.goto(base, { waitUntil: 'networkidle' });
    assert.equal(await page.locator('.project').count(), 5);
    assert.equal(await page.locator('html').getAttribute('lang'), 'pt-BR');
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    assert.equal(await page.locator('.picture').isVisible(), width > 920);
    assert.equal(await page.locator('.portrait-mobile').isVisible(), width <= 920);
    assert.ok(await page.locator('.project .ico').evaluateAll(images => images.every(img => img.complete && img.naturalWidth > 0)));
    await page.screenshot({ path: `/tmp/el-${width}.png`, fullPage: true });
  }
  await page.getByRole('link', { name: 'Próxima página' }).click();
  await page.waitForURL(/page=2/);
  assert.equal(await page.locator('.project').count(), 1);
  assert.equal(await page.locator('.pagination [aria-disabled]').getAttribute('aria-label'), 'Próxima página');
  await page.getByRole('link', { name: 'English', exact: true }).click();
  await page.waitForURL(/lang=en/);
  assert.match(page.url(), /page=2/);
  await page.waitForFunction(() => document.documentElement.lang === 'en');
  assert.equal(await page.locator('html').getAttribute('lang'), 'en');
  await page.locator('.project').click();
  await page.waitForURL(/projects\//);
  await page.locator('.toc-document a').first().waitFor();
  assert.ok(await page.locator('.toc-document a').count() > 0);
  assert.equal(await page.locator('.toc-document a').first().getAttribute('href').then(url => url.startsWith('https://github.com/')), true);
  await page.getByRole('link', { name: '← Back to projects' }).click();
  await page.waitForURL(/lang=en&page=2/);
  await page.getByRole('link', { name: 'Previous page' }).click();
  await page.waitForURL(/page=1/);
  await page.keyboard.press('Tab');
  assert.ok(await page.evaluate(() => document.activeElement.tagName === 'A'));
  assert.deepEqual(errors, []);
  console.log('PASS: five viewports, icons, page boundaries, language preservation, project categories, keyboard, no runtime errors');
  await browser.close();
})().catch(error => { console.error(error); process.exit(1); });
