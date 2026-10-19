/* eslint-disable @typescript-eslint/no-require-imports */
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || '/tmp/source-browser/node_modules/playwright');
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  try {
    const page = await browser.newPage({ reducedMotion: 'reduce' });
    for (const slug of ['go-image-optimizer', 'engineering-library', 'env-auditor']) {
      for (const language of ['pt-BR', 'en']) {
        for (const width of [390, 768, 1440]) {
          await page.setViewportSize({ width, height: 900 });
          await page.goto(`${process.env.BROWSER_BASE_URL || 'http://localhost:3000'}/projects/${slug}?lang=${language}`);
          await page.locator('.reader[data-pagination="ready"]').waitFor();
          const chapters = page.locator('.reader-probe--left .toc-chapter');
          assert.ok(await chapters.count());
          const labels = await chapters.allTextContents();
          assert.ok(labels.every(label => !/\b(API|FAQ|ADR)\b/u.test(label)), labels.join('; '));
          if (slug === 'go-image-optimizer') assert.ok(labels.some(label => /Api/u.test(label)));
          const geometry = await chapters.evaluateAll(nodes => nodes.map(node => ({
            fits: node.scrollWidth <= node.clientWidth + 1,
            cursive: getComputedStyle(node).fontFamily.includes('Great Vibes'),
          })));
          assert.ok(geometry.every(item => item.fits && item.cursive));
          assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
          console.log(`PASS ${slug} ${language} ${width}px: cursive labels, measured pagination and heading widths`);
        }
      }
    }
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
