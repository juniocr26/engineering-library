/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const base = process.env.BROWSER_BASE_URL || 'http://localhost:3000';
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const results = [];
  try {
    for (const slug of (process.env.FAQ_PROJECTS?.split(',') || ['engineering-library', 'env-auditor', 'go-image-optimizer', 'payment-reconciliation-lab', 'rust-event-relay', 'url-shortener'])) {
      for (const lang of ['en', 'pt-BR']) {
        const context = await browser.newContext({ viewport: { width: lang === 'en' ? 1440 : 390, height: 900 } });
        const page = await context.newPage();
        const errors = [];
        page.on('pageerror', error => errors.push(error.message));
        const ready = () => page.locator('.reader[data-pagination="ready"] .reader-stage[aria-busy="false"]').waitFor();
        const indicator = () => page.locator('.reader-pages .reader-controls [aria-live]').innerText();
        const turn = async direction => {
          const before = await indicator();
          const buttons = page.locator('.reader-pages .reader-controls button');
          await (direction === 'next' ? buttons.last() : buttons.first()).click();
          await page.waitForFunction(text => document.querySelector('.reader-pages .reader-controls [aria-live]')?.textContent !== text, before);
          await ready();
        };
        await page.goto(`${base}/projects/${slug}?lang=${lang}`); await ready();
        const probeLinks = page.locator('.reader-probe--left a[href*="/docs/faq/"]');
        assert.equal(await probeLinks.count(), 1);
        assert.match((await probeLinks.textContent()).trim(), /^\d+\.?\s*FAQ(?:↗)?$/);
        const faq = page.locator('.reader-pages a[href*="/docs/faq/index.md?"]').first();
        for (let count = 0; !(await faq.isVisible()); count++) {
          assert.ok(count < 100, 'FAQ must be reachable through normal TOC pagination');
          await turn('next');
        }
        await faq.click(); await page.waitForURL(`**/docs/faq/index.md?lang=${lang}`); await ready();
        const text = await page.locator('.reader-probe--left').textContent();
        assert.match(text, /(?:Answer|Resposta|Model answer|Resposta modelo):/);
        assert.match(await page.locator('.reader-pages').innerText(), /Q\d{3}|Question|Pergunta/, 'questions appear on the first physical FAQ page');
        if (process.env.FAQ_NAV_ONLY) {
          await page.screenshot({ path: `/tmp/faq-final-${slug}-${lang}.png`, fullPage: true });
          results.push({ project: slug, language: lang, firstPageQuestions: true, directNavigation: true });
          console.log(`PASS final navigation ${slug}/${lang}`);
          await context.close();
          continue;
        }
        const initial = await indicator();
        await turn('next'); await turn('previous'); assert.equal(await indicator(), initial);
        // Persist a real anonymous bookmark, reload, then remove this test's bookmark.
        const leaf = page.locator('.reader-pages .reader-leaf').first();
        const save = leaf.getByRole('button', { name: lang === 'en' ? 'Bookmark page' : 'Marcar página', exact: true });
        await save.click(); await leaf.locator('.bookmark-ribbon--saved').waitFor();
        await page.reload(); await ready(); await leaf.locator('.bookmark-ribbon--saved').waitFor();
        await leaf.getByRole('button', { name: lang === 'en' ? 'Remove bookmark' : 'Remover marcação', exact: true }).click();
        await save.waitFor();
        await page.locator('.reader-pages').getByRole('button', { name: lang === 'en' ? 'Search' : 'Pesquisar', exact: true }).first().click();
        await page.locator('#reader-search').fill('Q001');
        const hit = page.locator('dialog a[href*="/docs/faq/index.md"]').first();
        await hit.waitFor(); await hit.click(); await ready();
        assert.match(page.url(), /\/docs\/faq\/index\.md\?/);
        await page.screenshot({ path: `/tmp/faq-${slug}-${lang}.png`, fullPage: true });
        assert.deepEqual(errors, []);
        results.push({ project: slug, language: lang, directNavigation: true, pagination: true, bookmarkPersistence: true, search: true, viewport: lang === 'en' ? 1440 : 390 });
        console.log(`PASS ${slug}/${lang}`);
        await context.close();
      }
    }
    if (process.env.FAQ_REPORT) fs.writeFileSync(process.env.FAQ_REPORT, JSON.stringify(results, null, 2) + '\n');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
