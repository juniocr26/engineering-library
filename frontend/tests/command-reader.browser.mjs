import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { mkdir, writeFile, rm, mkdtemp, symlink, copyFile } from 'node:fs/promises';
import { spawn } from 'node:child_process';
const { chromium } = createRequire(import.meta.url)(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root = await mkdtemp('/tmp/engineering-source-test-');
const appRoot = new URL('../', import.meta.url).pathname;
await mkdir(`${root}/app/source-stress-test`, { recursive: true });
for (const name of ['components', 'lib', 'tests', 'node_modules', 'public']) await symlink(name === 'node_modules' ? new URL('..', import.meta.resolve('next/package.json')).pathname : `${appRoot}${name}`, `${root}/${name}`);
for (const name of ['package.json', 'tsconfig.json']) await copyFile(name === 'node_modules' ? new URL('..', import.meta.resolve('next/package.json')).pathname : `${appRoot}${name}`, `${root}/${name}`);
for (const name of ['layout.tsx', 'globals.css']) await symlink(`${appRoot}app/${name}`, `${root}/app/${name}`);
let server, browser;
try {
  await writeFile(`${root}/app/source-stress-test/page.tsx`, "export { default } from '../../tests/fixtures/command-stress-page';\n");
  server = spawn(process.execPath, ['node_modules/next/dist/bin/next', 'dev', '--webpack', '-p', '3103'], { cwd: root, stdio: ['ignore', 'pipe', 'pipe'] });
  let log = ''; server.stdout.on('data', x => { log += x; }); server.stderr.on('data', x => { log += x; });
  for (let i = 0; i < 120; i++) { if (server.exitCode !== null) throw Error(log); try { if ((await fetch('http://localhost:3103/source-stress-test')).ok) break; } catch {} await new Promise(r => setTimeout(r, 500)); }
  browser = await chromium.launch({ headless: true });
  const ready = async page => { await page.locator('.reader[data-pagination="ready"]').waitFor(); await page.locator('.reader-stage[aria-busy="false"]').waitFor(); };

  for (const width of [390, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 1000 }, hasTouch: width < 921, reducedMotion: 'reduce' });
    await page.addInitScript(() => {
      window.copied = '';
      Object.defineProperty(navigator, 'clipboard', { value: { writeText: async text => { window.copied = text; } } });
    });
    await page.goto('http://localhost:3103/source-stress-test'); await ready(page);
    const shells = page.locator('.reader-pages .reader-code-shell');
    const short = shells.first();
    assert.equal(await short.locator('.reader-table-hint').count(), 0);
    await short.getByRole('button').click();
    assert.equal(await page.evaluate(() => window.copied), 'echo ok');
    assert.equal(await short.getByRole('status').innerText(), 'Copied');
    const long = shells.nth(1);
    const viewport = long.locator('.reader-code');
    assert.equal(await viewport.getAttribute('data-overflow'), 'true');
    assert.equal(await long.locator('.reader-table-hint').count(), 1);
    await long.getByRole('button').click();
    const expected = await page.evaluate(() => window.copied);
    assert.ok(expected.startsWith('docker compose exec -T frontend env PLAYWRIGHT_BROWSERS_PATH=/tmp/'));
    assert.ok(expected.endsWith('  echo "$HOME & <value>"'));
    const box = await viewport.boundingBox();
    await page.mouse.move(box.x + box.width - 4, box.y + 5);
    await page.mouse.down(); await page.mouse.move(box.x + 20, box.y + 5, { steps: 10 }); await page.mouse.up();
    assert.ok(await viewport.evaluate(n => n.scrollLeft > 0));
    await viewport.evaluate(n => { n.scrollLeft = 0; });
    await viewport.focus(); await page.keyboard.press('ArrowRight');
    await page.waitForTimeout(300);
    assert.ok(await viewport.evaluate(n => n.scrollLeft > 0));
    await viewport.evaluate(n => {
      const range = document.createRange(); range.selectNodeContents(n.querySelector('[data-code-text]'));
      getSelection().removeAllRanges(); getSelection().addRange(range);
    });
    assert.ok((await page.evaluate(() => getSelection().toString())).includes('docker compose'));
    await page.evaluate(() => getSelection().removeAllRanges());
    const label = await page.locator('.reader-pages .reader-controls [aria-live]').innerText();
    await page.waitForTimeout(500);
    assert.equal(await page.locator('.reader-pages .reader-controls [aria-live]').innerText(), label);
    await page.evaluate(() => { navigator.clipboard.writeText = async () => { throw Error('denied'); }; });
    await long.getByRole('button').click();
    assert.match(await long.getByRole('status').innerText(), /Could not copy/);
    const origin = await page.locator('.reader-measure .reader-code-shell').nth(2).locator('[data-source-code]').getAttribute('data-source-code');
    await page.evaluate(origin => { window.location.hash = `${origin}--line-50`; }, origin);
    await ready(page);
    const continuation = page.locator('.reader-pages .reader-code-shell').filter({ has: page.locator('[data-source-line="50"]') });
    await page.evaluate(() => { navigator.clipboard.writeText = async text => { window.copied = text; }; });
    await continuation.getByRole('button').click();
    assert.equal((await page.evaluate(() => window.copied)).split('\n').length, 100);
    await page.close();
  }
  console.log('Command reader: desktop/mobile overflow, drag, keyboard, selection, complete copy, feedback and stable pagination passed');

} finally { await browser?.close(); server?.kill('SIGTERM'); await rm(root, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 }); }
