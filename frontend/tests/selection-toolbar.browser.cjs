/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const trackRecords = require('./annotation-test-records.cjs');
const base = process.env.BROWSER_BASE_URL || 'http://localhost:3000';
const path = '/projects/env-auditor/docs/architecture/overview.md';
const scope = 'project=env-auditor&document=architecture%2Foverview.md&language=pt-BR';
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const cleanups = [];
  try {
    for (const width of [1728, 390]) {
      const context = await browser.newContext({ viewport: { width, height: 1000 }, permissions: ['clipboard-read', 'clipboard-write'] });
      cleanups.push(trackRecords(context, process.env.BROWSER_BASE_URL || 'http://localhost:3000'));
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      const ready = async () => {
        await page.locator('.reader[data-pagination=ready]').waitFor();
        await page.evaluate(() => document.fonts.ready);
        await page.waitForFunction(() => document.querySelector('.reader-stage')?.getAttribute('aria-busy') === 'false');
        await page.evaluate(() => new Promise(resolve => {
          let previous = '', stable = 0;
          const frame = () => {
            const stage = document.querySelector('.reader-stage');
            const geometry = JSON.stringify([...document.querySelectorAll('.reader-pages [data-highlight-block]')].map(node => [node.dataset.highlightBlock, node.getBoundingClientRect().toJSON()]));
            stable = geometry === previous && stage?.getAttribute('aria-busy') === 'false' ? stable + 1 : 0;
            previous = geometry; if (stable >= 8) resolve(); else requestAnimationFrame(frame);
          }; requestAnimationFrame(frame);
        }));
      };
      const toolbar = page.getByRole('toolbar', { name: 'Destaques de texto' });
      // Range is used only to measure endpoints. Actual selection is a mouse drag.
      const drag = async (locator, start, end) => {
        await locator.scrollIntoViewIfNeeded();
        const points = await locator.evaluate((el, { start, end }) => {
          const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); const texts = [];
          while (walker.nextNode()) texts.push(walker.currentNode);
          const point = position => {
            let offset = 0;
            for (const node of texts) {
              if (offset + node.length >= position) {
                const range = document.createRange(); range.setStart(node, position - offset); range.collapse(true);
                const rect = range.getBoundingClientRect(); return { x: rect.x, y: rect.y + rect.height / 2 };
              } offset += node.length;
            } throw Error('Offset outside text');
          };
          return { from: point(start), to: point(end) };
        }, { start, end });
        await page.mouse.move(points.from.x + 1, points.from.y);
        await page.mouse.down();
        await page.mouse.move(points.to.x, points.to.y, { steps: 16 });
        await page.mouse.up();
        assert.ok((await page.evaluate(() => getSelection().toString())).trim());
      };
      const checkToolbar = async () => {
        await toolbar.waitFor();
        assert.equal(await toolbar.locator('button[aria-pressed]').count(), 7);
        assert.equal(await toolbar.getByRole('button', { name: 'Adicionar nota (disponível na fase 2)' }).isDisabled(), true);
        assert.equal(await toolbar.evaluate(node => node.parentElement === document.body), true);
        const rect = await toolbar.boundingBox();
        assert.ok(rect.x >= 0 && rect.y >= 0 && rect.x + rect.width <= width && rect.y + rect.height <= 1000);
        assert.equal(await toolbar.evaluate(node => { const rect = node.getBoundingClientRect(); return node.contains(document.elementFromPoint(rect.x + 10, rect.y + 10)); }), true);
      };
      await page.goto(`${base}${path}?lang=pt-BR`); await ready();
      const intro = page.locator('.reader-pages p').filter({ hasText: 'O README mantém' }).first();
      assert.equal(await intro.locator('.source-reference').count(), 1);
      // Real sentence crossing the interactive label, including its hidden arrow gap.
      const sentence = 'O README mantém o contrato da CLI e todas as exclusões. A implementação é um script da biblioteca padrão, organizado em descoberta, parsing literal, planejamento e persistência por alvo.';
      await intro.evaluate(node => {
        const range = document.createRange(); range.selectNodeContents(node);
        getSelection().removeAllRanges(); getSelection().addRange(range);
      });
      await checkToolbar();
      assert.equal(await toolbar.locator('button').count(), 9);
      for (const name of ['Copiar', 'Adicionar nota (disponível na fase 2)']) {
        assert.equal(await toolbar.getByRole('button', { name, exact: true }).evaluate(node => getComputedStyle(node).backgroundColor), 'rgba(0, 0, 0, 0)');
      }
      await page.keyboard.press('Control+c');
      assert.equal(await page.evaluate(() => navigator.clipboard.readText()), sentence);
      await toolbar.getByRole('button', { name: 'Copiar', exact: true }).click();
      assert.equal(await page.evaluate(() => navigator.clipboard.readText()), sentence);
      await drag(intro, 0, 62); await checkToolbar();
      const selected = await page.evaluate(() => getSelection().toString());
      await toolbar.getByRole('button', { name: 'Copiar', exact: true }).click();
      assert.equal(await page.evaluate(() => navigator.clipboard.readText()), selected);
      await toolbar.waitFor({ state: 'hidden' });
      await intro.evaluate(node => { const range = document.createRange(); range.selectNodeContents(node); getSelection().removeAllRanges(); getSelection().addRange(range); }); await checkToolbar();
      await page.screenshot({ path: `/tmp/selection-toolbar-${width}.png` });
      await toolbar.getByRole('button', { name: 'Amarelo', exact: true }).click();
      await page.waitForFunction(() => CSS.highlights.get('reader-yellow')?.size > 0);
      const list = async () => (await page.request.get(`${base}/api/highlights?${scope}`)).json();
      assert.equal((await list()).highlights.length, 1);
      const originalId = (await list()).highlights[0].id;
      await intro.evaluate(node => { const range = document.createRange(); range.selectNodeContents(node); getSelection().removeAllRanges(); getSelection().addRange(range); }); await checkToolbar();
      await toolbar.getByRole('button', { name: 'Azul', exact: true }).click();
      await page.waitForFunction(() => CSS.highlights.get('reader-blue')?.size > 0);
      assert.equal((await list()).highlights.length, 1);
      assert.equal((await list()).highlights[0].id, originalId);
      await intro.evaluate(node => { const range = document.createRange(); range.selectNodeContents(node); getSelection().removeAllRanges(); getSelection().addRange(range); }); await checkToolbar();
      await toolbar.getByRole('button', { name: 'Amarelo', exact: true }).click();
      await page.waitForFunction(() => CSS.highlights.get('reader-yellow')?.size > 0);

      await page.reload(); await ready();
      await page.waitForFunction(() => CSS.highlights.get('reader-yellow')?.size > 0);
      const savedPoint = async color => page.evaluate(color => { const rect = [...CSS.highlights.get(`reader-${color}`)][0].getClientRects()[0]; return { x: rect.x + 4, y: rect.y + rect.height / 2 }; }, color);
      const yellow = await savedPoint('yellow'); await page.mouse.click(yellow.x, yellow.y); await checkToolbar();
      await toolbar.getByRole('button', { name: 'Azul', exact: true }).click();
      await page.waitForFunction(() => CSS.highlights.get('reader-blue')?.size > 0);
      await page.locator('.reader-pages .reader-document-languages a[hreflang=en]').click(); await page.waitForURL(/lang=en/); await ready();
      await page.waitForFunction(() => (CSS.highlights.get('reader-blue')?.size ?? 0) === 0);
      await page.locator('.reader-pages .reader-document-languages a[hreflang="pt-BR"]').click(); await page.waitForURL(/lang=pt-BR/); await ready();
      await page.waitForFunction(() => CSS.highlights.get('reader-blue')?.size > 0);
      const blue = await savedPoint('blue'); await page.mouse.click(blue.x, blue.y); await checkToolbar();
      await page.keyboard.press('Escape'); await toolbar.waitFor({ state: 'hidden' });
      assert.equal((await list()).highlights.length, 1);
      await page.mouse.click(blue.x, blue.y); await checkToolbar();
      await page.mouse.click(2, 2); await toolbar.waitFor({ state: 'hidden' });
      assert.equal((await list()).highlights.length, 1);
      await page.mouse.click(blue.x, blue.y); await checkToolbar();
      await toolbar.getByRole('button', { name: 'Azul', exact: true }).click();
      await page.waitForFunction(() => CSS.highlights.get('reader-blue')?.size === 0);
      assert.equal((await list()).highlights.length, 0);
      await page.reload(); await ready();
      assert.equal((await list()).highlights.length, 0);
      await intro.locator('.source-reference').click(); await ready();
      assert.equal(await intro.locator('.source-reference').getAttribute('aria-expanded'), 'true');
      await intro.locator('.source-reference').click(); await ready();
      assert.equal(await intro.locator('.source-reference').getAttribute('aria-expanded'), 'false');
      // A heading near the top remains selectable; the entire heading is not a forbidden surface.
      await drag(page.locator('.reader-pages h1').first(), 2, 10); await checkToolbar(); await page.keyboard.press('Escape');
      // Prose AFTER inline code in the same paragraph is eligible.
      await page.evaluate(() => { const block = [...document.querySelectorAll('.reader-measure [data-highlight-block]')].find(node => node.textContent.includes('interpreta flags')); window.location.hash = block.dataset.highlightBlock; });
      const prose = page.locator('.reader-pages p').filter({ hasText: 'interpreta flags' }).first();
      const start = await prose.evaluate(node => node.textContent.indexOf('interpreta'));
      await drag(prose, start, start + 35); await checkToolbar(); await page.keyboard.press('Escape');
      // Inline code is selectable prose; block code remains excluded.
      await drag(prose.locator('code').first(), 0, 3);
      await checkToolbar(); await page.keyboard.press('Escape');
      if (width === 1728) {
        // Resolve the logical paragraph onto its physical page, then choose the right leaf.
        const target = await page.evaluate(() => [...document.querySelectorAll('.reader-measure [data-highlight-block]')].find(node => node.textContent.includes('verifica arquivo regular')).dataset.highlightBlock);
        await page.evaluate(target => { window.location.hash = target; }, target); await ready();
        const lower = page.locator('.reader-pages p').filter({ hasText: 'verifica arquivo regular' }).first();
        const lowerOffset = await lower.evaluate(node => node.textContent.indexOf('verifica'));
        await drag(lower, lowerOffset, lowerOffset + 20); await checkToolbar(); await page.keyboard.press('Escape');
        const right = page.locator('.reader-pages > .reader-leaf').nth(1).locator('.reader-markdown > p').first();
        await right.waitFor();
        const offset = await right.evaluate(el => { const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); while (walker.nextNode()) { const n = walker.currentNode; if (!n.parentElement.closest('button,code') && n.textContent.trim().length > 10) { const r = document.createRange(); r.selectNodeContents(el); r.setEnd(n,0); return r.toString().length; } } return -1; });
        assert.ok(offset >= 0);
        await drag(right, offset, offset + 8); await checkToolbar(); await page.keyboard.press('Escape');
      }
      await page.locator('.reader-pages .reader-controls button').last().click(); await ready();
      const nextParagraphs = page.locator('.reader-pages .reader-markdown > p');
      const next = nextParagraphs.first();
      const eligible = await next.evaluate(el => { const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); while (walker.nextNode()) { const n = walker.currentNode; if (!n.parentElement.closest('button,code') && n.textContent.trim().length > 10) { const r = document.createRange(); r.selectNodeContents(el); r.setEnd(n,0); return r.toString().length; } } return -1; });
      assert.ok(eligible >= 0, 'next page has eligible prose');
      await drag(next, eligible, eligible + 8); await checkToolbar(); await page.keyboard.press('Escape');
      assert.deepEqual(errors, []);
      console.log(`PASS ${width}px: real mouse drag in mixed Markdown, seven colors, note disabled, visible portal, copy, PostgreSQL CRUD/reload, language isolation, headings, inline code, page navigation`);
    }
  } finally {
    for (const cleanup of cleanups) await cleanup();
    await browser.close();
  }
})().catch(error => { console.error(error); process.exit(1); });
