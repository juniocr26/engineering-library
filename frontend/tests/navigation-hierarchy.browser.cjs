/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const { readFileSync } = require('node:fs');
const assert = require('node:assert/strict');
const reports = JSON.parse(readFileSync('/tmp/navigation-audit.json','utf8'));
const base = process.env.BOOK_READER_URL || 'http://localhost:3000';
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  let cases = 0;
  try {
    for (const width of [1728, 390]) {
      const page = await browser.newPage({ viewport: { width, height: 980 }, reducedMotion: 'reduce' });
      page.setDefaultTimeout(30000);
      const ready = () => page.locator('.reader[data-pagination="ready"] .reader-stage[aria-busy="false"]').waitFor();
      for (const report of reports.filter(r => !process.env.NAVIGATION_PROJECT || r.project === process.env.NAVIGATION_PROJECT)) for (const localized of report.languages) {
        const faq = localized.tree.filter(e => e.documentId === 'faq/index.md');
        const target = faq.filter(e => e.id.includes('#question:')).at(-1) || faq.at(-1);
        assert.ok(target);
        await page.goto(`${base}/projects/${report.project}?lang=${localized.language}#${encodeURIComponent(target.id)}`);
        await ready();
        const link = page.locator('.reader-pages a').filter({ hasText: `${target.number}` }).filter({ hasText: target.title }).first();
        await link.waitFor({ state: 'visible' });
        assert.equal(await link.getAttribute('href'), target.href);
        // Deep links reveal their ancestors even when the default groups are collapsed.
        await link.click();
        await ready();
        await page.waitForFunction(anchor => window.history.state?.bookLocation?.anchor === anchor, target.anchor);
        assert.equal(decodeURIComponent(new URL(page.url()).hash.slice(1)), target.anchor);
        if (target.id.includes('#question:')) {
          const lang = localized.language === 'en' ? 'pt-BR' : 'en';
          const counterpart = report.languages.find(l => l.language === lang).tree.find(e => e.id === target.id);
          if (counterpart) {
            await page.locator(`.reader-pages a[hreflang="${lang}"]`).click();
            await ready();
            await page.waitForFunction(anchor => window.history.state?.bookLocation?.anchor === anchor, counterpart.anchor);
          }
        }
        // Exercise collapse/expansion and a second measured pagination on the contents.
        await page.goto(`${base}/projects/${report.project}?lang=${localized.language}#${encodeURIComponent('faq/index.md')}`);
        await ready();
        const button = page.locator('.reader-pages .toc-row').filter({ has: page.locator('a[href$="/faq/index.md?lang=' + localized.language + '"]') }).locator('.toc-toggle').first();
        await button.click(); await ready();
        assert.equal(await page.locator('.reader-pages .toc-toggle[aria-expanded="true"]').count() > 0, true);
        assert.equal(await button.getAttribute('aria-expanded'), 'true');
        await button.click(); await ready();
        assert.equal(await button.getAttribute('aria-expanded'), 'false');
        await button.click(); await ready();
        assert.equal(await button.getAttribute('aria-expanded'), 'true');
        cases++;
        console.log(`PASS ${report.project} ${localized.language} ${width}px: late FAQ destination, canonical switch when available, expansion`);
      }
      await page.close();
    }
    console.log(`${cases} navigation browser cases passed`);
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
