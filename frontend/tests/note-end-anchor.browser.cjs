/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const base = process.env.BROWSER_BASE_URL || 'http://localhost:3000';
const query = 'project=engineering-library&document=architecture%2Fcurrent-state.md&language=en';
const ready = async page => { await page.locator('.reader[data-pagination="ready"]').waitFor(); await page.waitForFunction(() => document.querySelector('.reader-stage')?.getAttribute('aria-busy') === 'false'); };
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  try {
    const page = await browser.newPage({ viewport: { width: 390, height: 850 } });
    await page.goto(`${base}/projects/engineering-library/docs/architecture/current-state.md?lang=en`);
    await page.evaluate(() => document.fonts.ready); await ready(page);
    await page.waitForTimeout(1500);
    // One logical passage spanning distant physical pages, stored through the real API.
    const record = await page.evaluate(async query => {
      const identity = await (await fetch(`/api/highlights?${query}`)).json();
      const blocks = [...document.querySelectorAll('.reader-measure [data-highlight-block]')].filter(node => node.querySelector('p') && !node.dataset.highlightUnsupported);
      const segments = [blocks[0], blocks.at(-1)].map(node => { const text = node.textContent; return { block: node.dataset.highlightBlock, start: 0, end: 10, exact: text.slice(0,10), prefix: '', suffix: text.slice(10,58) }; });
      const headers = { 'Content-Type': 'application/json', 'X-Annotation-CSRF': identity.csrf_token };
      const highlight = await (await fetch(`/api/highlights?${query}`, { method: 'POST', headers, body: JSON.stringify({ color: 'green', segments }) })).json();
      const response = await fetch(`/api/notes?${query}`, { method: 'POST', headers, body: JSON.stringify({ highlight_id: highlight.id, body: 'Logical end fixture' }) });
      if (!response.ok) throw Error(`Note fixture: ${response.status}`);
      const note = await response.json();
      return { note, highlight, token: identity.csrf_token };
    }, query);
    await page.reload(); await ready(page);
    const marker = page.locator(`[data-note-id="${record.note.id}"]`);
    assert.equal(await marker.count(), 0, 'No marker on the first continuation page');
    let found = false;
    for (let turn = 0; turn < 60; turn++) {
      if (await marker.count()) { found = true; break; }
      const next = page.locator('.reader-pages .reader-controls button').last();
      assert.ok(await next.isEnabled(), 'Logical end must be reachable');
      await next.click(); await ready(page); await page.waitForTimeout(350);
    }
    assert.ok(found); assert.equal(await marker.count(), 1);
    const nearEnd = await marker.evaluate((node, anchor) => {
      const block = [...document.querySelectorAll('.reader-pages [data-highlight-block]')].find(block => block.dataset.highlightBlock === anchor.block && !block.closest('[inert]'));
      const text = document.createTreeWalker(block, NodeFilter.SHOW_TEXT).nextNode();
      const range = document.createRange(); range.setStart(text, 0); range.setEnd(text, 10);
      const end = [...range.getClientRects()].at(-1); const rect = node.getBoundingClientRect();
      return Math.abs(rect.left - end.right - 2) < 3 && Math.abs(rect.top - end.top + 7) < 3;
    }, record.note.segments.at(-1));
    assert.ok(nearEnd, 'Marker follows the actual text endpoint');
    await page.setViewportSize({ width: 430, height: 900 }); await ready(page); await marker.waitFor();
    assert.equal(await marker.count(), 1);
    await page.evaluate(async ({ record, query }) => {
      const response = await fetch(`/api/highlights/${record.highlight.id}?${query}`, { method: 'DELETE', headers: { 'X-Annotation-CSRF': record.token } });
      if (!response.ok) throw Error('Highlight cleanup failed');
    }, { record, query });
    await page.reload(); await ready(page); await marker.waitFor();
    await marker.focus(); await page.keyboard.press('Enter');
    assert.equal(await page.locator('#note-draft').inputValue(), 'Logical end fixture');
    await page.setViewportSize({ width: 320, height: 480 });
    const editor = page.getByRole('dialog', { name: 'Note editor', exact: true });
    const frame = await editor.boundingBox();
    assert.ok(Math.abs(frame.x + frame.width / 2 - 160) < 3 && Math.abs(frame.y + frame.height / 2 - 240) < 3);
    for (const button of await editor.locator('footer button').all()) {
      const box = await button.boundingBox(); assert.ok(box.x >= 0 && box.x + box.width <= 320 && box.y >= 0 && box.y + box.height <= 480);
    }
    await page.locator('#note-draft').fill('# Selectable heading\n\n' + 'Long note text for scrolling. '.repeat(500));
    await editor.getByRole('button', { name: 'Preview', exact: true }).click();
    const preview = page.getByRole('dialog', { name: 'Note preview', exact: true });
    const stage = preview.locator('.note-preview-scroll');
    assert.ok(await stage.evaluate(node => node.scrollHeight > node.clientHeight));
    const heading = await preview.locator('h1').boundingBox();
    await page.mouse.move(heading.x + 4, heading.y + heading.height / 2);
    await page.mouse.down(); await page.mouse.move(heading.x + 100, heading.y + heading.height / 2, { steps: 5 }); await page.mouse.up();
    assert.ok(await page.evaluate(() => getSelection().toString().length > 0), 'Mouse text selection remains available');
    await preview.getByRole('button', { name: 'Pan mode', exact: true }).click();
    const box = await stage.boundingBox();
    const session = await page.context().newCDPSession(page);
    await session.send('Emulation.setTouchEmulationEnabled', { enabled: true });
    const y = box.y + 20;
    await session.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ id: 1, x: box.x + 40, y }, { id: 2, x: box.x + 90, y }] });
    await session.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ id: 1, x: box.x + 25, y }, { id: 2, x: box.x + 120, y }] });
    await session.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
    await page.waitForFunction(() => Number(document.querySelector('.note-preview-scroll').dataset.zoom) > 1);
    await preview.getByRole('button', { name: 'Reset zoom', exact: true }).click();
    await page.mouse.move(box.x + 50, y); await page.mouse.wheel(0, -200);
    await page.waitForFunction(() => Number(document.querySelector('.note-preview-scroll').dataset.zoom) > 1);
    await page.evaluate(async ({ record, query }) => {
      const response = await fetch(`/api/notes/${record.note.id}?${query}`, { method: 'DELETE', headers: { 'X-Annotation-CSRF': record.token } });
      if (!response.ok) throw Error('Note cleanup failed');
    }, { record, query });
    console.log('PASS compact 320x480: visible actions, long-note scrolling, mouse text selection, touch pinch, wheel zoom');
    console.log('PASS note logical end: continuation pages, one superscript, endpoint geometry, resize, highlight removal, keyboard open');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
