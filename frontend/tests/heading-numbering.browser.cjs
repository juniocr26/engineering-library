/* eslint-disable @typescript-eslint/no-require-imports */
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const reports = require('/tmp/navigation-audit.json');
const base = process.env.BOOK_READER_URL || 'http://localhost:3000';
(async () => {
  const browser = await chromium.launch({headless:true, args:['--no-sandbox']});
  let cases = 0;
  try {
    const page = await browser.newPage({viewport:{width:1728,height:980}, reducedMotion:'reduce'});
    const ready = () => page.locator('.reader[data-pagination="ready"] .reader-stage[aria-busy="false"]').waitFor();
    for (const report of reports) for (const localized of report.languages) {
      const target = report.project === 'env-auditor'
        ? localized.tree.find(e => e.id.includes('#section:') && e.documentId?.startsWith('architecture/')) || localized.tree.find(e => e.documentId?.startsWith('architecture/'))
        : localized.tree.filter(e => e.documentId === 'faq/index.md').at(-1);
      assert.ok(target);
      await page.goto(base + target.href);
      await ready();
      const heading = page.locator('.reader-pages .book-unit').filter({has: page.locator('h1,h2,h3,h4,h5,h6')}).filter({hasText:target.number}).first();
      await heading.waitFor({state:'visible'});
      assert.equal(await page.locator(`.reader-pages [data-unit-id="${target.anchor}"]`).count(),1);
      const text = await page.locator(`.reader-pages [data-unit-id="${target.anchor}"]`).innerText();
      assert.ok(text.startsWith(target.number + ' '),text);
      await page.getByRole('button', {name: localized.language === 'en' ? 'Chapter index' : 'Índice de capítulos', exact:true}).first().click();
      const panelLink = page.locator('.reader-panel-list a').filter({hasText: `${target.number} ${target.title}`}).first();
      await panelLink.waitFor();
      assert.equal(await panelLink.getAttribute('href'), `#${encodeURIComponent(target.anchor)}`);
      await panelLink.click();
      await ready();
      await page.setViewportSize({width:390,height:844});
      await ready();
      assert.ok((await page.locator(`.reader-pages [data-unit-id="${target.anchor}"]`).innerText()).startsWith(target.number + ' '));
      await page.setViewportSize({width:1728,height:980});
      await ready();
      await page.goto(`${base}/projects/${report.project}?lang=${localized.language}#${encodeURIComponent(target.id)}`);
      await ready();
      const tocLink = page.locator('.reader-pages a').filter({hasText:target.number}).filter({hasText:target.title}).first();
      await tocLink.waitFor({state:'visible'});
      assert.equal(await tocLink.getAttribute('href'), target.href);
      await tocLink.click();
      await ready();
      assert.ok((await page.locator(`.reader-pages [data-unit-id="${target.anchor}"]`).innerText()).startsWith(target.number + ' '));
      cases++;
    }
    console.log(`${cases} project/language cases: numbered headings, direct anchors and resize repagination passed`);
  } finally { await browser.close(); }
})().catch(error => {console.error(error);process.exitCode=1;});
