/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const trackRecords = require('./annotation-test-records.cjs');
(async () => {
 const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
 const context = await browser.newContext({ baseURL: process.env.BROWSER_BASE_URL || 'http://localhost:3000', viewport: { width: 1440, height: 900 } });
 const page = await context.newPage();
 const cleanup = trackRecords(context, process.env.BROWSER_BASE_URL || 'http://localhost:3000');
 try {
  await page.goto(`${process.env.BROWSER_BASE_URL || 'http://localhost:3000'}/projects/engineering-library?lang=en`);
  await page.locator('.reader[data-pagination="ready"]').waitFor();
  const left = page.locator('.reader-pages > .reader-leaf').first();
  const right = page.locator('.reader-pages > .reader-leaf').nth(1);
  for (const leaf of [left, right]) {
   await leaf.getByRole('button', { name: 'Bookmark page', exact: true }).click();
   await leaf.locator('.bookmark-ribbon--saved').waitFor();
  }
  const response = await page.request.get('/api/bookmarks?project_slug=engineering-library&language=en');
  const { bookmarks } = await response.json();
  assert.equal(bookmarks.length, 2);
  assert.ok(bookmarks.every(b => b.document === '@contents'));
  assert.notEqual(bookmarks[0].anchor, bookmarks[1].anchor);
  await page.reload(); await page.locator('.reader[data-pagination="ready"]').waitFor();
  await left.locator('.bookmark-ribbon--saved').waitFor(); await right.locator('.bookmark-ribbon--saved').waitFor();
  for (const leaf of [left, right]) {
   await leaf.locator('.bookmark-ribbon--saved').click();
   await leaf.getByRole('button', { name: 'Bookmark page', exact: true }).waitFor();
  }
  assert.equal((await (await page.request.get('/api/bookmarks?project_slug=engineering-library&language=en')).json()).bookmarks.length, 0);
  console.log('PASS: shared Rails/PostgreSQL create, independent leaves, refresh and ribbon deletion');
 } finally {
  await cleanup();
  await browser.close();
 }
})().catch(error => { console.error(error); process.exit(1); });
