/* eslint-disable @typescript-eslint/no-require-imports */
// Generate /tmp/navigation-audit.json with npm run audit:navigation first.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const reports = require('/tmp/navigation-audit.json');
const base = process.env.BOOK_READER_URL || 'http://localhost:3000';
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  let targets = 0, panelEntries = 0;
  try {
    const page = await browser.newPage({ viewport: { width: 1728, height: 980 }, reducedMotion: 'reduce' });
    const ready = () => page.locator('.reader[data-pagination="ready"] .reader-stage[aria-busy="false"]').waitFor();
    async function check(locator, depth) {
      await locator.first().waitFor({ state: 'visible' });
      const expected = depth === 0 ? '700' : '400';
      const weights = await locator.first().evaluate(el => [el, ...el.querySelectorAll('*')].map(n => getComputedStyle(n).fontWeight));
      assert.ok(weights.every(w => w === expected), `${depth}: ${weights}`);
    }
    for (const report of reports.filter(r => !process.env.CHAPTER_WEIGHT_PROJECT || r.project === process.env.CHAPTER_WEIGHT_PROJECT)) for (const localized of report.languages) {
      const entries = localized.tree;
      const samples = [...new Set([
        ...['2', '3'].map(number => entries.find(e => e.number === number)),
        ...[1, 2, 3].map(depth => entries.find(e => e.depth === depth && e.href)),
      ].filter(Boolean))];
      for (const entry of samples) {
        await page.goto(`${base}/projects/${report.project}?lang=${localized.language}#${encodeURIComponent(entry.id)}`);
        await ready();
        await page.waitForFunction(target => Array.from(document.querySelectorAll('.reader-pages [data-unit-id]')).some(n => n.dataset.unitId === target), entry.id);
        // Resolve by canonical unit ID; numbers are labels, never depth inputs.
        const title = page.locator('.reader-pages [data-unit-id]').filter({ has: page.locator('.toc-row') });
        const id = await title.evaluateAll((nodes, target) => nodes.findIndex(n => n.dataset.unitId === target), entry.id);
        assert.ok(id >= 0, entry.id);
        await check(title.nth(id).locator('.chapter-title'), entry.depth);
        await page.getByRole('button', { name: localized.language === 'en' ? 'Chapter index' : 'Índice de capítulos', exact: true }).first().click();
        const projectItems = page.locator('.reader-panel-list').last().locator('li');
        assert.equal(await projectItems.count(), entries.length);
        const weights = await projectItems.evaluateAll(nodes => nodes.map(n => ({ depth: Number(n.dataset.chapterDepth), weights: [n, ...n.querySelectorAll('*')].map(el => getComputedStyle(el).fontWeight) })));
        for (const item of weights) assert.ok(item.weights.every(w => w === (item.depth === 0 ? '700' : '400')));
        panelEntries += weights.length;
        await page.keyboard.press('Escape');
        if (entry.href) {
          await page.goto(base + entry.href);
          await ready();
          const headings = page.locator('.reader-pages .reader-markdown.chapter-title');
          await headings.first().waitFor();
          const found = await headings.evaluateAll((nodes, number) => nodes.findIndex(n => n.textContent.startsWith(number + ' ')), entry.number);
          assert.ok(found >= 0, entry.href);
          await check(headings.nth(found), entry.depth);
          // Nested emphasis must inherit the canonical title weight.
          await headings.nth(found).evaluate(el => { const strong = document.createElement('strong'); strong.innerHTML = '<strong>Weight probe</strong>'; el.querySelector('h1,h2,h3,h4,h5,h6').append(strong); });
          await check(headings.nth(found), entry.depth);
          await page.getByRole('button', { name: localized.language === 'en' ? 'Chapter index' : 'Índice de capítulos', exact: true }).first().click();
          const localItems = page.locator('.reader-panel-list').first().locator('li[data-chapter-depth]');
          const local = await localItems.evaluateAll(nodes => nodes.map(n => ({ depth: Number(n.dataset.chapterDepth), weight: getComputedStyle(n.querySelector('a')).fontWeight })));
          assert.ok(local.length);
          for (const item of local) assert.equal(item.weight, item.depth === 0 ? '700' : '400');
          await page.keyboard.press('Escape');
        }
        targets++;
      }
      console.log(`PASS ${report.project} ${localized.language}: chapters 2/3, available depths 1–3, contents, panels, reader`);
    }
    console.log(`${targets} canonical targets; ${panelEntries} project panel entries checked`);
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
