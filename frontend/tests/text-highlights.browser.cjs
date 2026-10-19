/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || '/tmp/numbering-browser/node_modules/playwright');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const contexts = [];
  try {
    for (const width of [1440, 390]) {
      const context = await browser.newContext({ viewport: { width, height: 1000 } });
      contexts.push(context);
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      const base = process.env.BROWSER_BASE_URL || 'http://localhost:3000';
      const path = '/projects/engineering-library/docs/architecture/current-state.md';
      const ready = async () => {
        await page.locator('.reader[data-pagination="ready"]').waitFor();
        await page.waitForFunction(() => !!window.CSS.highlights);
        await page.evaluate(() => new Promise(resolve => {
          let previous = '', stable = 0;
          const frame = () => {
            const stage = document.querySelector('.reader-stage');
            const geometry = JSON.stringify([stage?.getBoundingClientRect().toJSON(), ...[...document.querySelectorAll('.reader-pages [data-highlight-block]')].map(node => node.getBoundingClientRect().toJSON())]);
            stable = geometry === previous && stage?.getAttribute('aria-busy') === 'false' ? stable + 1 : 0;
            previous = geometry;
            if (stable >= 8) resolve(); else requestAnimationFrame(frame);
          }; requestAnimationFrame(frame);
        }));
      };
      const select = async () => {
        await page.evaluate(() => document.fonts.ready);
        await page.waitForFunction(() => document.querySelector('.reader-stage')?.getAttribute('aria-busy') === 'false');
        await page.locator('.reader-pages [data-highlight-block] p').first().evaluate(p => {
          const walker = document.createTreeWalker(p, NodeFilter.SHOW_TEXT);
          const text = walker.nextNode();
          const range = document.createRange(); range.setStart(text, 0); range.setEnd(text, Math.min(text.length, 18));
          const selection = getSelection(); selection.removeAllRanges(); selection.addRange(range);
        });
        await page.getByRole('toolbar', { name: 'Text highlights' }).waitFor({ timeout: 5000 }).catch(async error => { console.log(await page.evaluate(() => ({ selection: getSelection().toString(), notices: [...document.querySelectorAll('[role=status]')].map(n => n.textContent), html: document.querySelector('.reader-pages [data-highlight-block] p')?.outerHTML, mode: document.querySelector('.reader')?.dataset.mode, inert: document.querySelector('.reader-pages [data-highlight-block] p')?.closest('[inert]')?.outerHTML.slice(0,200), css: getComputedStyle(document.querySelector('.reader-pages [data-highlight-block] p')).userSelect }))); throw error; });
      };
      await page.goto(`${base}${path}?lang=en`); await ready();
      // Synthetic DOM fixture in the real reader: inline formatting, controls,
      // collapsed disclosure, code and media boundaries share one saved record.
      await page.locator('.reader-pages [data-highlight-block]').first().evaluate(block => {
        block.innerHTML = '<p>Before <a href="#fixture">link</a> <strong>bold</strong> <em>italic</em> <code>inline</code><button class="source-reference">CONTROL</button> after</p><pre>EXCLUDED CODE</pre><p>across code</p><details><summary>Disclosure</summary><p>COLLAPSED</p></details><table><tbody><tr><td>EXCLUDED TABLE</td></tr></tbody></table><p>end</p>';
        const range = document.createRange(); range.selectNodeContents(block);
        getSelection().removeAllRanges(); getSelection().addRange(range);
      });
      await page.getByRole('button', { name: 'Purple', exact: true }).click();
      await page.waitForFunction(() => CSS.highlights.get('reader-purple')?.size > 0);
      const fixture = await page.evaluate(async () => (await fetch('/api/highlights?project=engineering-library&document=architecture%2Fcurrent-state.md&language=en')).json());
      assert.equal(fixture.highlights.length, 1);
      const captured = fixture.highlights[0].segments.map(part => part.exact).join(' ');
      for (const text of ['Before', 'link', 'bold', 'italic', 'inline', 'after', 'across code', 'end']) assert.ok(captured.includes(text), captured);
      for (const text of ['CONTROL', 'EXCLUDED', 'COLLAPSED', 'Disclosure']) assert.ok(!captured.includes(text), captured);
      assert.equal(await page.locator('.reader-pages details[open]').count(), 0);
      const painted = await page.evaluate(() => [...CSS.highlights.get('reader-purple')].map(range => range.toString()).join(' '));
      for (const text of ['CONTROL', 'EXCLUDED', 'COLLAPSED', 'Disclosure']) assert.ok(!painted.includes(text), painted);
      await page.request.delete(`${base}/api/highlights/${fixture.highlights[0].id}?project=engineering-library&document=architecture%2Fcurrent-state.md&language=en`, { headers: { Origin: base, 'X-Reader-CSRF': fixture.csrf_token } });
      await page.reload(); await ready();
      await select();
      assert.equal(await page.locator('.reader-selection-toolbar button[aria-pressed]').count(), 7);
      await page.keyboard.press('Escape');
      await page.getByRole('toolbar', { name: 'Text highlights' }).waitFor({ state: 'hidden' });
      await select();
      const beforeKeyboard = await page.locator('.reader-controls').first().innerText();
      await page.keyboard.press('Shift+ArrowRight');
      await page.getByRole('toolbar', { name: 'Text highlights' }).waitFor();
      assert.equal(await page.locator('.reader-controls').first().innerText(), beforeKeyboard);
      await page.getByRole('button', { name: 'Yellow', exact: true }).click();
      await page.waitForFunction(() => CSS.highlights.get('reader-yellow')?.size > 0);
      const list = () => page.evaluate(async () => (await fetch('/api/highlights?project=engineering-library&document=architecture%2Fcurrent-state.md&language=en')).json());
      const saved = (await list()).highlights;
      assert.equal(saved.length, 1);
      // Independent overlapping records survive together; deleting one preserves the other.
      await page.locator('.reader-pages [data-highlight-block] p').first().evaluate(p => {
        const walker = document.createTreeWalker(p, NodeFilter.SHOW_TEXT); const node = walker.nextNode();
        const range = document.createRange(); range.setStart(node, 7); range.setEnd(node, 25);
        getSelection().removeAllRanges(); getSelection().addRange(range);
      });
      await page.getByRole('button', { name: 'Green', exact: true }).click();
      await page.waitForFunction(() => CSS.highlights.get('reader-green')?.size > 0 && CSS.highlights.get('reader-yellow')?.size > 0);
      const overlapping = await list();
      assert.equal(overlapping.highlights.length, 2);
      const green = overlapping.highlights.find(item => item.color === 'green');
      const deleted = await page.request.delete(`${base}/api/highlights/${green.id}?project=engineering-library&document=architecture%2Fcurrent-state.md&language=en`, { headers: { Origin: base, 'X-Reader-CSRF': overlapping.csrf_token } });
      assert.equal(deleted.status(), 204);
      await page.reload(); await ready();
      await page.waitForFunction(() => CSS.highlights.get('reader-yellow')?.size > 0);
      const firstPage = await page.locator('.reader-controls').first().innerText();
      await page.locator('.reader-pages .reader-controls button').last().click(); await ready();
      assert.notEqual(await page.locator('.reader-controls').first().innerText(), firstPage);
      await page.locator('.reader-pages .reader-controls button').first().click(); await ready();
      await page.waitForFunction(() => CSS.highlights.get('reader-yellow')?.size > 0);
      await page.goto(`${base}${path}?lang=en&q=Static#${encodeURIComponent(saved[0].segments[0].block)}`); await ready();
      assert.ok(await page.locator('.reader-pages mark').count() > 0);
      await page.waitForFunction(() => CSS.highlights.get('reader-yellow')?.size > 0);
      // Repagination retains the range and does not change logical identity.
      await page.setViewportSize({ width: width === 390 ? 500 : 1200, height: 900 }); await ready();
      await page.waitForFunction(() => CSS.highlights.get('reader-yellow')?.size > 0);
      const point = await page.evaluate(() => {
        const range = [...CSS.highlights.get('reader-yellow')][0];
        const rect = range.getClientRects()[0]; return { x: rect.x + 2, y: rect.y + rect.height / 2 };
      });
      await page.mouse.click(point.x, point.y);
      await page.getByRole('button', { name: 'Blue', exact: true }).click();
      await page.waitForFunction(() => CSS.highlights.get('reader-blue')?.size > 0);
      await page.locator('.reader-pages .reader-document-languages a[hreflang="pt-BR"]').click(); await page.waitForURL(/lang=pt-BR/); await ready();
      assert.equal(await page.evaluate(() => CSS.highlights.get('reader-blue')?.size ?? 0), 0);
      await page.locator('.reader-pages .reader-document-languages a[hreflang="en"]').click(); await page.waitForURL(/lang=en/); await ready();
      await page.waitForFunction(() => CSS.highlights.get('reader-blue')?.size > 0);
      const removePoint = await page.evaluate(() => {
        const rect = [...CSS.highlights.get('reader-blue')][0].getClientRects()[0]; return { x: rect.x + 2, y: rect.y + rect.height / 2 };
      });
      await page.mouse.click(removePoint.x, removePoint.y);
      await page.getByRole('button', { name: 'Remove highlight', exact: true }).click();
      await page.waitForFunction(() => CSS.highlights.get('reader-blue')?.size === 0);
      assert.equal((await list()).highlights.length, 0);
      assert.deepEqual(errors, []);
      await page.screenshot({ path: `/tmp/highlights-${width}.png` });
      await context.close();
    }
    console.log('PASS: desktop/mobile selection, seven colors, Escape, keyboard selection, search compatibility, overlaps, PostgreSQL persistence, reload, resize, language scope, recolor and delete');
  } finally {
    for (const context of contexts) {
      try {
        const base = process.env.BROWSER_BASE_URL || 'http://localhost:3000';
        const scope = 'project=engineering-library&document=architecture%2Fcurrent-state.md&language=en';
        const response = await context.request.get(`${base}/api/highlights?${scope}`);
        if (response.ok()) {
          const data = await response.json();
          for (const item of data.highlights) await context.request.delete(`${base}/api/highlights/${item.id}?${scope}`, { headers: { Origin: base, 'X-Reader-CSRF': data.csrf_token } });
        }
      } catch { /* Completed contexts are already closed and cleaned. */ }
    }
    await browser.close();
  }
})().catch(error => { console.error(error); process.exit(1); });
