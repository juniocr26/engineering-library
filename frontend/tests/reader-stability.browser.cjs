/* eslint-disable @typescript-eslint/no-require-imports */
// No database fixtures: exercise real Markdown, logical anchors and measured geometry.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const base = process.env.BROWSER_BASE_URL || 'http://localhost:3099';
const project = `${base}/projects/engineering-library`;
const ready = async page => {
  await page.locator('.reader[data-pagination="ready"] .reader-stage[aria-busy="false"]').waitFor();
  await page.evaluate(() => document.fonts.ready);
  // A genuine resize is observed on the next frame, then measured on two
  // consecutive frames. Begin the idle assertion after that layout commit.
  await page.evaluate(() => new Promise(resolve => {
    let frames = 4;
    const next = () => --frames ? requestAnimationFrame(next) : resolve();
    requestAnimationFrame(next);
  }));
  await page.locator('.reader[data-pagination="ready"] .reader-stage[aria-busy="false"]').waitFor();
};
const anchorOf = locator => locator.evaluate(node => node.closest('.book-unit').querySelector('[data-highlight-block]').dataset.highlightBlock);
async function stable(page, reason, duration = 1200) {
  await ready(page);
  const result = await page.evaluate(duration => new Promise(resolve => {
    const reader = document.querySelector('.reader');
    const states = new Set(); const capacities = new Set();
    let turns = 0; let missing = 0; let remounted = false;
    const start = performance.now();
    function sample() {
      remounted ||= reader !== document.querySelector('.reader');
      states.add(document.querySelector('.reader-pages .reader-controls span')?.textContent);
      capacities.add(Array.from(document.querySelectorAll('.reader-measure .reader-body')).map(node => node.clientHeight).join('/'));
      turns += document.querySelector('.turn-sheet') ? 1 : 0;
      missing += document.querySelector('.reader')?.dataset.pagination !== 'ready' ? 1 : 0;
      if (performance.now() - start < duration) requestAnimationFrame(sample);
      else resolve({ states: [...states], capacities: [...capacities], turns, missing, remounted });
    }
    requestAnimationFrame(sample);
  }), duration);
  assert.equal(result.states.length, 1, `${reason}: spontaneous page changes: ${result.states}`);
  assert.equal(result.capacities.length, 1, `${reason}: measurement feedback: ${result.capacities}`);
  assert.equal(result.turns, 0, `${reason}: unsolicited animation`);
  assert.equal(result.missing, 0, `${reason}: ready content disappeared`);
  assert.equal(result.remounted, false, `${reason}: reader remounted`);
  return result.states[0];
}
async function jump(page, document, language, anchor) {
  await page.goto(`${project}/docs/${document}?lang=${language}#${encodeURIComponent(anchor)}`);
  await ready(page);
  await page.waitForFunction(anchor => history.state?.bookLocation?.anchor === anchor, anchor);
}
(async () => {
  const browser = await chromium.launch({ executablePath: process.env.PLAYWRIGHT_EXECUTABLE_PATH, headless: true });
  try {
    for (const width of [1720, 390]) {
      const page = await browser.newPage({ viewport: { width, height: width === 1720 ? 876 : 844 }, deviceScaleFactor: 2, locale: 'pt-BR' });
      page.setDefaultTimeout(60000);
      const errors = []; page.on('pageerror', error => errors.push(error.message));
      const document = 'guides/application-development.md';
      await page.goto(`${project}/docs/${document}?lang=pt-BR`);
      await stable(page, `${width}: initial document`, 2000);
      // Real code unit whose height straddled the old 543/548 px right-leaf capacities.
      const prose = await page.locator('.reader-pages [data-highlight-block]:not([data-highlight-unsupported])').last().getAttribute('data-highlight-block');
      await page.evaluate(anchor => {
        window.proseInvalidations = 0;
        window.proseObserver = new MutationObserver(records => {
          for (const record of records) if (record.attributeName === 'data-pagination' && record.target.dataset.pagination !== 'ready') window.proseInvalidations++;
        });
        window.proseObserver.observe(document.querySelector('.reader'), {attributes:true, attributeFilter:['data-pagination']});
        location.hash = anchor;
      }, prose);
      await page.waitForFunction(anchor => history.state?.bookLocation?.anchor === anchor, prose);
      await stable(page, `${width}: same-spread prose anchor`);
      assert.equal(await page.evaluate(() => { window.proseObserver.disconnect(); return window.proseInvalidations; }), 0);
      const boundary = await anchorOf(page.locator('.reader-measure .reader-code').first());
      await jump(page, document, 'pt-BR', boundary);
      const before = await stable(page, `${width}: application-development boundary anchor`, 5000);
      console.log(`PASS ${width}: application-development idle and boundary anchor`);
      const controls = page.locator('.reader-pages .reader-controls');
      await controls.locator('button').last().click();
      await page.waitForFunction(value => document.querySelector('.reader-pages .reader-controls span')?.textContent !== value && !document.querySelector('.turn-sheet'), before);
      const forward = await stable(page, `${width}: forward`);
      assert.notEqual(forward, before);
      await controls.locator('button').first().click();
      await page.waitForFunction(() => !document.querySelector('.turn-sheet'));
      assert.equal(await stable(page, `${width}: backward`), before);
      const anchor = await page.evaluate(() => history.state.bookLocation.anchor);
      await page.setViewportSize({ width: width === 1720 ? 1280 : 768, height: 950 });
      await stable(page, `${width}: resize`);
      assert.equal(await page.evaluate(() => history.state.bookLocation.anchor), anchor);
      await page.setViewportSize({ width, height: width === 1720 ? 876 : 844 });
      await stable(page, `${width}: restored viewport`);
      for (const label of ['Pesquisar', 'Índice de capítulos', 'Minhas marcações', 'Destaques e notas']) {
        await page.getByRole('button', { name: label, exact: true }).click();
        await stable(page, `${width}: open ${label}`, 600);
        await page.keyboard.press('Escape');
        await stable(page, `${width}: close ${label}`, 600);
      }
      // A completed resource notification with unchanged geometry must not cancel a user turn.
      const current = await page.locator('.reader-pages .reader-controls span').innerText();
      await controls.locator('button').last().click();
      await page.locator('.turn-sheet').waitFor();
      await page.evaluate(() => document.querySelector('.reader-measure .reader-body').dispatchEvent(new Event('load', { bubbles: true })));
      await page.waitForFunction(value => !document.querySelector('.turn-sheet') && document.querySelector('.reader-pages .reader-controls span')?.textContent !== value, current);
      await stable(page, `${width}: navigation during resource notification`);
      const visual = 'img/visual-components.md';
      await page.goto(`${project}/docs/${visual}?lang=pt-BR`);
      await stable(page, `${width}: image/table/Mermaid document`, 2000);
      assert.ok(await page.locator('.reader-measure table').count());
      await page.waitForFunction(() => Array.from(document.querySelectorAll('.reader-measure .reader-diagram img')).filter(image => image.complete && image.naturalWidth > 0).length >= 2);
      const tableHeading = await anchorOf(page.locator('.reader-measure h2').nth(2));
      await jump(page, visual, 'pt-BR', tableHeading);
      await stable(page, `${width}: table section`);
      await page.locator('.reader-pages a[hreflang="en"]').click();
      await page.waitForFunction(() => document.querySelector('main')?.lang === 'en');
      await stable(page, `${width}: translated table section`);
      const translated = await anchorOf(page.locator('.reader-measure h2').nth(2));
      assert.ok(await page.locator(`.reader-pages [data-unit-id="${translated}"]`).count(), 'canonical img-03 section survives language switching');
      const reference = page.locator('.reader-measure .source-reference').filter({ hasText: 'Puma' }).first();
      const sourceAnchor = await anchorOf(reference);
      await jump(page, visual, 'en', sourceAnchor);
      await page.locator('.reader-pages .source-reference').filter({hasText:'Puma'}).click();
      await ready(page);
      await stable(page, `${width}: expanded source`);
      assert.ok(await page.locator('.reader-measure [data-source-code]').count());
      await page.locator('.reader-pages .source-reference').filter({hasText:'Puma'}).click();
      await stable(page, `${width}: collapsed source`);
      assert.equal(await page.locator('.reader-measure [data-source-code]').count(), 0);
      assert.deepEqual(errors, [], 'no lifecycle errors');
      console.log(`PASS ${width}: turns, resize, panels, notifications, code, tables, Mermaid and translated anchors`);
      await page.close();
    }
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
