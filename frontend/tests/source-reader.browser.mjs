import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { mkdir, writeFile, rm, mkdtemp, symlink, copyFile } from 'node:fs/promises';
import { spawn } from 'node:child_process';
const { chromium } = createRequire(import.meta.url)(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root = await mkdtemp('/tmp/engineering-source-test-');
const appRoot = new URL('../', import.meta.url).pathname;
await mkdir(`${root}/app/source-stress-test`, { recursive: true });
for (const name of ['components', 'lib', 'tests', 'node_modules', 'public']) await symlink(`${appRoot}${name}`, `${root}/${name}`);
for (const name of ['package.json', 'tsconfig.json']) await copyFile(`${appRoot}${name}`, `${root}/${name}`);
for (const name of ['layout.tsx', 'globals.css']) await symlink(`${appRoot}app/${name}`, `${root}/app/${name}`);
let server, browser;
try {
  await writeFile(`${root}/app/source-stress-test/page.tsx`, "export { default } from '../../tests/fixtures/source-stress-page';\n");
  server = spawn(process.execPath, ['node_modules/next/dist/bin/next', 'dev', '--webpack', '-p', '3103'], { cwd: root, stdio: ['ignore', 'pipe', 'pipe'] });
  let log = ''; server.stdout.on('data', x => { log += x; }); server.stderr.on('data', x => { log += x; });
  for (let i = 0; i < 120; i++) { if (server.exitCode !== null) throw Error(log); try { if ((await fetch('http://localhost:3103/source-stress-test')).ok) break; } catch {} await new Promise(r => setTimeout(r, 500)); }
  browser = await chromium.launch({ headless: true });
  const ready = async page => { await page.locator('.reader[data-pagination="ready"]').waitFor(); await page.locator('.reader-stage[aria-busy="false"]').waitFor(); };
  for (const width of [390, 768, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 1000 }, reducedMotion: 'reduce' });
    const errors = []; page.on('pageerror', error => errors.push(error.message));
    let savedBookmark;
    await page.route('**/api/bookmarks**', async route => {
      if (route.request().method() === 'POST') { savedBookmark = { ...route.request().postDataJSON(), id: 1 }; await route.fulfill({ json: savedBookmark }); }
      else await route.fulfill({ json: { bookmarks: savedBookmark ? [savedBookmark] : [], csrf_token: 'test' } });
    });
    await page.goto('http://localhost:3103/source-stress-test'); await ready(page);
    const controls = page.locator('.reader-pages .reader-controls');
    const before = await controls.locator('[aria-live]').innerText();
    await page.locator('.reader-pages .source-reference').first().click(); await ready(page);
    assert.equal(await page.locator('.reader-pages .source-reference').nth(1).getAttribute('aria-expanded'), 'false');
    const after = await controls.locator('[aria-live]').innerText(); assert.notEqual(after, before);
    const seen = []; let scrolled = false;
    while (true) {
      if (await page.locator('.reader-pages [data-source-line="21"]').count()) {
        scrolled = await page.locator('.reader-pages .source-code-scroll').evaluateAll(nodes => nodes.some(n => n.scrollWidth > n.clientWidth));
      }
      seen.push(...await page.locator('.reader-pages [data-source-line]').evaluateAll(nodes => nodes.map(n => Number(n.dataset.sourceLine))));
      const overflow = await page.locator('.reader-pages .reader-body').evaluateAll(nodes => nodes.some(n => n.scrollHeight > n.clientHeight + 3));
      assert.equal(overflow, false, `${width}: source segments fit physical pages`);
      if (await controls.locator('button').last().getAttribute('aria-disabled') === 'true') break;
      await controls.locator('button').last().click(); await ready(page);
    }
    assert.equal(scrolled, true, 'long source lines scroll horizontally');
    assert.deepEqual(seen, Array.from({ length: 200 }, (_, i) => i + 1));
    await page.evaluate(() => { window.location.hash = 'source-stress--line-171'; }); await ready(page);
    await page.locator('.reader-pages [data-source-line="171"]').waitFor();
    assert.match(await page.locator('.reader-pages [data-source-line="171"] mark').allTextContents().then(x => x.join('')), /needle_171/);
    const leaf = page.locator('.reader-pages .reader-leaf').filter({ has: page.locator('[data-source-line="171"]') });
    await leaf.getByRole('button', { name: 'Bookmark page', exact: true }).click();
    await page.waitForFunction(() => !!document.querySelector('.reader-pages .bookmark-ribbon--saved'));
    assert.ok(savedBookmark.anchor.startsWith('source-stress--line-'));
    await page.goto(`http://localhost:3103/source-stress-test#${savedBookmark.anchor}`); await ready(page);
    await page.locator(`.reader-pages [data-source-location="${savedBookmark.anchor}"]`).waitFor();
    await page.evaluate(() => { window.location.hash = 'source-stress--line-171'; }); await page.locator('.reader-pages [data-source-line="171"]').waitFor();
    await page.setViewportSize({ width: width === 390 ? 768 : 390, height: 900 }); await ready(page);
    await page.locator('.reader-pages [data-source-line="171"]').waitFor();
    await page.evaluate(() => { window.location.hash = 'intro'; }); await page.locator('.reader-pages .source-reference').first().waitFor();
    assert.equal(await page.locator('.reader-pages .source-reference').first().getAttribute('aria-expanded'), 'true');
    await page.locator('.reader-pages .source-reference').first().click(); await ready(page);
    assert.equal(await page.locator('.reader-measure [data-source-line]').count(), 0);
    assert.equal(await page.locator('.reader-pages .source-reference').first().getAttribute('aria-expanded'), 'false');
    assert.deepEqual(errors, []);
    console.log(`PASS synthetic 200 lines: ${width}px, exact continuity, page bounds, line navigation, resize, persistent expansion, independent repeated disclosure, horizontal scrolling, bookmark restoration, collapse`);
    await page.close();
  }
  for (const project of ['engineering-library', 'env-auditor', 'go-image-optimizer', 'payment-reconciliation-lab', 'rust-event-relay', 'url-shortener']) {
    const response = await fetch(`http://localhost:3000/api/document-search/${project}?lang=en&q=return`);
    assert.equal(response.ok, true);
    const result = (await response.json()).results.find(r => r.anchor.includes('--line-'));
    assert.ok(result, `${project}: search indexes approved collapsed source`);
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
    await page.goto(`http://localhost:3000${result.href}`); await ready(page);
    await page.locator(`.reader-pages [data-source-location="${result.anchor}"] mark`).first().waitFor();
    await page.locator('.reader-pages .source-code').first().waitFor();
    await ready(page);
    console.log(`PASS catalog ${project}: collapsed-source search, auto expansion, exact line and red highlight`);
    await page.close();
  }
} finally { await browser?.close(); server?.kill('SIGTERM'); await rm(root, { recursive: true, force: true }); }
