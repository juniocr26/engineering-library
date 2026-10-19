/* Starts a temporary fixture route, removed even on failure. No fixtures enter the catalog. */
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { mkdir, writeFile, rm, mkdtemp, symlink, copyFile } from 'node:fs/promises';
import { spawn } from 'node:child_process';
const { chromium } = createRequire(import.meta.url)(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root = await mkdtemp('/tmp/engineering-table-test-');
const appRoot = new URL('../', import.meta.url).pathname;
const route = new URL(`file://${root}/app/table-stress-test/`);
await mkdir(route, { recursive: true });
for (const name of ['components', 'lib', 'tests', 'node_modules', 'public']) await symlink(`${appRoot}${name}`, `${root}/${name}`);
for (const name of ['package.json', 'tsconfig.json']) await copyFile(`${appRoot}${name}`, `${root}/${name}`);
await symlink(`${appRoot}app/layout.tsx`, `${root}/app/layout.tsx`);
await symlink(`${appRoot}app/globals.css`, `${root}/app/globals.css`);
let server;
let browser;
try {
  await writeFile(new URL('page.tsx', route), "export { default } from '../../tests/fixtures/table-stress-page';\n");
  server = spawn(process.execPath, ['node_modules/next/dist/bin/next', 'dev', '--webpack', '-p', process.env.TABLE_READER_PORT || '3101'], { cwd: root, stdio: ['ignore', 'pipe', 'pipe'], env: { ...process.env } });
  let serverLog = ''; server.stdout.on('data', value => { serverLog += value; }); server.stderr.on('data', value => { serverLog += value; });
  // The temporary project keeps its build cache separate from the development server.
  const base = process.env.TABLE_READER_URL || `http://localhost:${process.env.TABLE_READER_PORT || '3101'}`;
  for (let i = 0; i < 180; i++) {
    if (server.exitCode !== null) throw new Error(serverLog);
    try { if ((await fetch(`${base}/table-stress-test?rows=5`)).ok) break; } catch { /* Startup pending. */ }
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  browser = await chromium.launch({ headless: true });
  for (const width of (process.env.TABLE_STRESS_FOCUSED ? [] : [390, 768, 1440])) for (const rows of [5, 30, 200, 500]) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, reducedMotion: 'reduce', hasTouch: width < 921 });
    const errors = []; page.on('pageerror', error => errors.push(error.message));
    const language = rows === 30 ? 'pt-BR' : 'en';
    await page.goto(`${base}/table-stress-test?rows=${rows}&columns=${rows === 200 ? 12 : 10}&lang=${language}`);
    await page.locator('.reader[data-pagination=ready]').waitFor();
    const controls = page.locator('.reader-pages .reader-controls');
    const initial = await controls.innerText();
    const found = []; let turns = 0;
    while (true) {
      const leaves = page.locator('.reader-pages .reader-table');
      const values = await leaves.evaluateAll(nodes => nodes.map(node => {
        const table = node.querySelector('table');
        const shell = node.closest('.book-unit');
        return { headers: table.tHead.rows.length, cols: table.tHead.rows[0].cells.length, rows: [...table.tBodies[0].rows].map(row => row.cells[0].textContent), fits: shell.getBoundingClientRect().bottom <= shell.parentElement.getBoundingClientRect().bottom + 2, overflow: node.scrollWidth > node.clientWidth, bounded: node.getBoundingClientRect().right <= shell.parentElement.getBoundingClientRect().right + 1 };
      }));
      for (const value of values) { assert.equal(value.headers, 1); assert.equal(value.cols, rows === 200 ? 12 : 10); assert.ok(value.fits, 'segment fits leaf'); assert.ok(value.bounded); assert.ok(value.overflow); found.push(...value.rows); }
      if (!turns) {
        const table = leaves.first();
        await table.focus(); await page.keyboard.press('ArrowRight');
        assert.equal(await controls.innerText(), initial, 'table keys do not turn pages');
        await page.waitForFunction(() => document.querySelector('.reader-pages .reader-table')?.scrollLeft > 0);
        if (width === 1440) {
          const box = await table.boundingBox();
          await page.mouse.move(box.x + box.width * .7, box.y + 40); await page.mouse.down();
          await page.mouse.move(box.x + box.width * .3, box.y + 40, { steps: 10 }); await page.mouse.up();
          assert.ok(await table.evaluate(node => node.scrollLeft > 80));
        }
        if (width < 921) {
          const session = await page.context().newCDPSession(page);
          const box = await table.boundingBox();
          const x = box.x + box.width * .8, y = box.y + Math.min(100, box.height / 2);
          const beforeScroll = await table.evaluate(node => node.scrollLeft);
          await session.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y }] });
          for (let step = 1; step <= 8; step++) await session.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: x - step * 12, y }] });
          await session.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
          await page.waitForFunction(before => document.querySelector('.reader-pages .reader-table')?.scrollLeft > before, beforeScroll);
          assert.equal(await controls.innerText(), initial, 'touch table scrolling does not turn book pages');
          await session.detach();
        }
        await page.locator('.reader-pages .media-expand').first().click();
        const dialog = page.getByRole('dialog'); await dialog.waitFor();
        assert.equal(await dialog.locator('tbody tr').count(), rows, 'fullscreen exposes entire original table');
        await dialog.locator('button').nth(1).click(); assert.equal(await dialog.locator('output').innerText(), '125%');
        await dialog.locator('button').nth(2).click(); assert.equal(await dialog.locator('output').innerText(), '100%');
        const scroll = dialog.locator('.table-viewer-scroll');
        await scroll.evaluate(node => { node.scrollTop = node.scrollHeight; node.scrollLeft = node.scrollWidth; });
        assert.ok(await scroll.evaluate(node => node.scrollLeft > 0));
        await page.keyboard.press('Escape'); await dialog.waitFor({ state: 'detached' });
        assert.equal(await controls.innerText(), initial);
        await page.waitForFunction(() => document.querySelector('.reader-pages .media-expand') === document.activeElement);
      }
      if (await controls.locator('button').last().getAttribute('aria-disabled') === 'true') break;
      assert.ok(++turns < rows + 2, 'pagination terminates');
      const before = await controls.innerText(); await controls.locator('button').last().click();
      await page.waitForFunction(text => document.querySelector('.reader-pages .reader-controls')?.textContent !== text, before);
    }
    assert.deepEqual(found, Array.from({ length: rows }, (_, i) => `FICTIONAL_ENVIRONMENT_VARIABLE_FOR_PAGINATION_${String(i).padStart(4, '0')}`));
    await page.setViewportSize({ width: width === 1440 ? 390 : 1440, height: 760 });
    await page.locator('.reader[data-pagination=ready]').waitFor();
    await page.waitForTimeout(300);
    assert.ok(await page.locator('.reader-pages tbody tr').count() > 0);
    assert.deepEqual(errors, []);
    console.log(`PASS ${width}px, ${rows} rows: preserved rows/columns, repeated headers, bounded leaves, keyboard, drag (desktop), full table dialog, zoom, resize, termination`);
    await page.close();
  }
  const page = await browser.newPage({ viewport: { width: 390, height: 700 } });
  await page.goto(`${base}/table-stress-test?rows=5&oversized=1`);
  await page.locator('.reader[data-pagination=ready]').waitFor();
  assert.ok(await page.locator('.reader-pages .reader-table').first().evaluate(node => node.scrollHeight > node.clientHeight));
  console.log('PASS oversized row: bounded vertical scrolling fallback');
  for (const edge of ['one-row', 'insufficient-space', 'oversized-header']) {
    await page.goto(`${base}/table-stress-test?rows=5${edge === 'insufficient-space' ? '&before=1' : ''}`);
    await page.locator('.reader[data-pagination=ready]').waitFor();
    const height = await page.locator('.reader-probe--left table').evaluate(table => table.tHead.getBoundingClientRect().height + table.tBodies[0].rows[0].getBoundingClientRect().height + 17);
    await page.addStyleTag({ content: `.reader-body{flex:0 0 ${height}px!important;height:${height}px!important}` + (edge === 'insufficient-space' ? `.book-unit:has(> .reader-markdown > p){height:${height - 10}px;box-sizing:border-box}` : '') + (edge === 'oversized-header' ? '.reader-table th{height:900px}' : '') });
    await page.waitForTimeout(400);
    await page.locator('.reader[data-pagination=ready]').waitFor();
    if (edge === 'one-row') assert.equal(await page.locator('.reader-pages tbody tr').count(), 1);
    if (edge === 'insufficient-space') {
      assert.equal(await page.locator('.reader-pages table').count(), 0, 'move table when header plus first row cannot fit remaining space');
      await page.locator('.reader-pages .reader-controls button').last().click();
      await page.locator('.reader-pages table').waitFor();
    }
    if (edge === 'oversized-header') assert.ok(await page.locator('.reader-pages .reader-table').evaluate(node => node.scrollHeight > node.clientHeight));
    console.log(`PASS rendered edge: ${edge}`);
  }
  for (const width of [390, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto(`${base}/table-stress-test?rows=200&row=117`);
    await page.locator('.reader[data-pagination=ready]').waitFor();
    await page.locator('.reader-pages td').filter({ hasText: 'FICTIONAL_ENVIRONMENT_VARIABLE_FOR_PAGINATION_0117' }).waitFor();
    console.log(`PASS content row anchor ${width}px: row 117 resolves to its continuation`);
  }
  await page.setViewportSize({ width: 390, height: 900 });
  await page.goto(`${base}/table-stress-test?rows=500`);
  await page.locator('.reader[data-pagination=ready]').waitFor();
  await page.evaluate(() => {
    window.tableRowReads = 0;
    const original = Element.prototype.getBoundingClientRect;
    Element.prototype.getBoundingClientRect = function (...args) { if (this.tagName === 'TR') window.tableRowReads++; return original.apply(this, args); };
  });
  for (let i = 0; i < 5; i++) {
    const controls = page.locator('.reader-pages .reader-controls');
    const text = await controls.innerText(); await controls.locator('button').last().click();
    await page.waitForFunction(text => document.querySelector('.reader-pages .reader-controls')?.textContent !== text, text);
  }
  await page.setViewportSize({ width: 390, height: 800 });
  await page.waitForTimeout(400);
  assert.equal(await page.evaluate(() => window.tableRowReads), 0, 'turns and height-only resize reuse 500-row measurements');
  console.log('PASS measurement cache: no row remeasurements for page turns or height-only resize');
  await page.close();

} finally {
  await browser?.close(); server?.kill('SIGTERM'); await rm(root, { recursive: true, force: true });
}
