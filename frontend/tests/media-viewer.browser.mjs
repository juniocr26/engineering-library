/* Run against a server with MEDIA_DOCUMENT_URL pointing to a document with media.
 * PLAYWRIGHT_MODULE may point to an externally installed Playwright package.
 */
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)(process.env.PLAYWRIGHT_MODULE || 'playwright');
const browser = await chromium.launch({ headless: true });
try {
  for (const width of [390, 768, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    await page.goto(process.env.MEDIA_DOCUMENT_URL || 'http://localhost:3000/projects/go-image-optimizer/docs/architecture/overview.md?lang=en');
    await page.locator('.reader[data-pagination="ready"]').waitFor();
    const expand = page.locator('.reader-pages .media-expand').first();
    // Reach media through the reader's actual pagination.
    while (!await expand.isVisible()) {
      const next = page.locator('.reader-pages .reader-controls button').last();
      assert.equal(await next.getAttribute('aria-disabled'), 'false', 'document must contain media');
      await next.click();
      await page.locator('.reader-stage[aria-busy="false"]').waitFor();
    }
    assert.ok(await expand.evaluate(button => {
      const wrapper = button.closest('.expandable-media');
      const media = wrapper.querySelector('img, [role="img"]');
      const rect = button.getBoundingClientRect();
      return media && rect.top >= media.getBoundingClientRect().bottom && rect.width >= 44 && rect.height >= 44 && rect.right <= wrapper.getBoundingClientRect().right + 1;
    }), 'expand control must be below media with a bounded accessible target');
    const url = page.url();
    const pages = await page.locator('.reader-pages').innerText();
    await expand.focus();
    await page.keyboard.press('Enter');
    const viewer = page.getByRole('dialog');
    await viewer.waitFor();
    const image = viewer.locator('img');
    await image.evaluate(img => img.decode());
    assert.ok(await image.evaluate(img => img.naturalWidth > 0));
    const toolbar = viewer.locator('button');
    await toolbar.nth(1).click();
    assert.equal(await viewer.locator('output').innerText(), '125%');
    await toolbar.nth(0).click();
    assert.equal(await viewer.locator('output').innerText(), '100%');
    for (let i = 0; i < 6; i++) await toolbar.nth(1).click();
    const stage = viewer.locator('.media-viewer-stage');
    const rect = await stage.boundingBox();
    await page.mouse.move(rect.x + rect.width / 2, rect.y + rect.height / 2);
    await page.mouse.down();
    await page.mouse.move(rect.x + rect.width / 2 + 70, rect.y + rect.height / 2 + 70);
    await page.mouse.up();
    assert.doesNotMatch(await image.getAttribute('style'), /translate\(0px, 0px\)/);
    await toolbar.nth(2).click();
    assert.equal(await stage.getAttribute('data-zoom'), '1');
    await page.keyboard.press('Tab');
    assert.ok(await viewer.evaluate(node => node.contains(document.activeElement)));
    assert.ok(await viewer.evaluate(node => node.getBoundingClientRect().width <= innerWidth));
    await page.keyboard.press('Escape');
    await viewer.waitFor({ state: 'detached' });
    assert.equal(await expand.evaluate(node => node === document.activeElement), true);
    assert.equal(page.url(), url);
    assert.equal(await page.locator('.reader-pages').innerText(), pages);
    await expand.click();
    await page.getByRole('dialog').locator('button').last().click();
    await viewer.waitFor({ state: 'detached' });
    await page.close();
    console.log(`PASS media viewer ${width}px`);
  }
} finally { await browser.close(); }
