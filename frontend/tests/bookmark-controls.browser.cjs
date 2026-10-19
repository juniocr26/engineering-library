/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  try {
    for (const width of [1440, 768, 390, 320]) {
      const context = await browser.newContext({ viewport: { width, height: 900 } });
      const page = await context.newPage();
      let bookmarks = [], nextId = 1, fail = false, requests = 0;
      await page.route('**/api/bookmarks{,?*,/**}', async route => {
        const request = route.request();
        if (request.method() === 'GET') {
          assert.equal(new URL(request.url()).searchParams.get('project_slug'), 'engineering-library');
          return route.fulfill({ json: { bookmarks, csrf_token: 'fixture' } });
        }
        requests++;
        await new Promise(resolve => setTimeout(resolve, 120));
        if (fail) return route.fulfill({ status: 503, json: { error: 'unavailable' } });
        if (request.method() === 'POST') {
          const saved = { ...request.postDataJSON(), id: nextId++ }; bookmarks.push(saved);
          return route.fulfill({ status: 201, json: saved });
        }
        bookmarks = bookmarks.filter(item => item.id !== Number(new URL(request.url()).pathname.split('/').pop()));
        return route.fulfill({ status: 204 });
      });
      await page.goto(`${process.env.BROWSER_BASE_URL || 'http://localhost:3000'}/projects/engineering-library/docs/architecture/current-state.md?lang=en`);
      const ready = () => page.locator('.reader[data-pagination="ready"] .reader-pages').waitFor();
      await ready();
      const leaves = page.locator('.reader-pages .reader-leaf');
      const left = leaves.first();
      const assertContentClearance = async () => {
        await leaves.locator('.bookmark-ribbon--saved').evaluateAll(nodes => nodes.forEach(node => node.getAnimations().forEach(animation => animation.finish())));
        const geometry = await leaves.evaluateAll(nodes => nodes.map((leaf, index) => {
          const body = leaf.querySelector('.reader-body');
          const control = leaf.querySelector('.reader-page-bookmark');
          const ribbon = control?.querySelector('.bookmark-ribbon--saved');
          const occupied = ribbon || control;
          const probe = document.querySelector(index === 0 ? '.reader-probe--left .reader-body' : '.reader-probe--right .reader-body');
          return {
            clear: !occupied || body.getBoundingClientRect().top >= occupied.getBoundingClientRect().bottom + 12 - 1,
            capacity: body.clientHeight,
            measured: probe.clientHeight,
          };
        }));
        for (const leaf of geometry) {
          assert.ok(leaf.clear, 'content starts below the bookmark control or active ribbon');
          assert.equal(leaf.capacity, leaf.measured, 'pagination measures the visible content capacity');
        }
      };
      await assertContentClearance();
      const save = left.getByRole('button', { name: 'Bookmark page', exact: true });
      await save.waitFor();
      const boxes = await left.locator('.reader-toolbar button:not(.bookmark-ribbon)').evaluateAll(nodes => nodes.map(node => { const r = node.getBoundingClientRect(); return [r.y, r.width, r.height]; }));
      assert.equal(boxes.length, 4);
      assert.ok(boxes.every(box => box.every((value, i) => Math.abs(value - boxes[0][i]) < 1)), 'four controls share axis and dimensions');
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      fail = true; await save.click(); await page.locator('.reader-notice[role=alert]').waitFor();
      assert.equal(await left.locator('.bookmark-ribbon--saved').count(), 0);
      fail = false; await save.focus(); await page.keyboard.press('Enter');
      await left.locator('.bookmark-ribbon--saved').waitFor();
      assert.equal(await save.count(), 0);
      const ribbon = left.getByRole('button', { name: 'Remove bookmark', exact: true });
      await ribbon.evaluate(node => node.getAnimations().forEach(animation => animation.finish()));
      assert.ok(await ribbon.evaluate(node => node === document.activeElement));
      if (width === 1440) {
        await leaves.nth(1).getByRole('button', { name: 'Bookmark page', exact: true }).click();
        await leaves.nth(1).locator('.bookmark-ribbon--saved').waitFor();
        assert.equal(bookmarks.length, 2);
      }
      await assertContentClearance();
      await page.reload(); await ready(); await left.locator('.bookmark-ribbon--saved').waitFor();
      fail = true; await ribbon.click(); await page.locator('.reader-notice[role=alert]').waitFor();
      await page.waitForFunction(() => !document.querySelector('.reader-pages .bookmark-ribbon--saved')?.disabled);
      assert.equal(await left.locator('.bookmark-ribbon--saved').count(), 1);
      fail = false; await ribbon.click();
      await page.waitForFunction(() => { const n = document.querySelector('.reader-pages .reader-leaf .bookmark-ribbon'); return n && !n.classList.contains('bookmark-ribbon--saved'); });
      assert.equal(await save.count(), 0, 'toggle waits for retraction');
      await save.waitFor();
      if (width === 1440) assert.equal(await leaves.nth(1).locator('.bookmark-ribbon--saved').count(), 1);
      await page.emulateMedia({ reducedMotion: 'reduce' });
      await save.click(); await ribbon.waitFor(); await ribbon.click(); await save.waitFor();
      assert.equal(requests, width === 1440 ? 7 : 6);
      console.log(`PASS ${width}px: alignment, overflow, persistence reload, API failures, ribbon insertion/removal, reduced motion${width === 1440 ? ', independent leaves' : ''}`);
      await page.screenshot({ path: `/tmp/bookmark-controls-${width}.png`, fullPage: true });
      await context.close();
    }
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
