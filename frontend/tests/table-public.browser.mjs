import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)(process.env.PLAYWRIGHT_MODULE || 'playwright');
const browser = await chromium.launch({ headless: true });
try {
  for (const width of [390, 768, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
    await page.goto(`${process.env.BOOK_READER_URL || 'http://localhost:3000'}/projects/engineering-library/docs/env/index.md?lang=pt-BR`);
    await page.locator('.reader[data-pagination=ready]').waitFor();
    const original = await page.locator('.reader-probe--left tbody tr').allTextContents();
    assert.ok(original.length);
    const found = []; let turns = 0;
    while (true) {
      found.push(...await page.locator('.reader-pages tbody tr').allTextContents());
      assert.ok(await page.locator('.reader-pages .reader-table').evaluateAll(nodes => nodes.every(node => node.getBoundingClientRect().right <= node.closest('.reader-body').getBoundingClientRect().right + 1)));
      const controls = page.locator('.reader-pages .reader-controls');
      if (await controls.locator('button').last().getAttribute('aria-disabled') === 'true') break;
      assert.ok(++turns < 200);
      const text = await controls.innerText(); await controls.locator('button').last().click();
      await page.waitForFunction(text => document.querySelector('.reader-pages .reader-controls')?.textContent !== text, text);
    }
    assert.deepEqual(found, original);
    console.log(`PASS public documentation ${width}px: all original table rows accessible in order, bounded horizontal overflow`);
    await page.close();
  }
} finally { await browser.close(); }
