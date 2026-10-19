/* eslint-disable @typescript-eslint/no-require-imports */
// Dedicated local demonstration browser. The UI opt-in seeds the human's cookie instead.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || '/tmp/numbering-browser/node_modules/playwright');
const fs = require('node:fs');
(async () => {
  const base = process.env.BROWSER_BASE_URL || 'http://localhost:3000';
  if (!['localhost', '127.0.0.1'].includes(new URL(base).hostname)) throw Error('Local development only');
  const browser = await chromium.launchPersistentContext('/tmp/engineering-note-demo-browser', { headless: true, args: ['--no-sandbox'], viewport: { width: 1440, height: 1000 } });
  const page = await browser.newPage();
  const cases = [];
  try {
    for (const language of ['en', 'pt-BR']) {
      await page.goto(`${base}/projects/engineering-library/docs/architecture/current-state.md?lang=${language}&noteDemos=1`);
      await page.locator('.reader[data-pagination="ready"]').waitFor();
      await page.locator('.note-demo-tools summary').click();
      const cleanup = process.argv.includes('--cleanup');
      const button = page.getByRole('button', { name: cleanup ? 'Remove demonstration records' : 'Seed current reader', exact: true });
      await button.click();
      await page.locator('.note-demo-tools [role=status]').filter({ hasText: cleanup ? 'removed' : 'cases saved' }).waitFor({ timeout: 20000 });
      if (cleanup) break;
      cases.push(...await page.locator('.note-demo-tools li a').evaluateAll(links => links.map(link => ({ label: link.textContent, url: link.href, language: new URL(link.href).searchParams.get('lang'), logical_anchor: decodeURIComponent(new URL(link.href).hash.slice(1)), expected_rendering: link.textContent }))));
    }
    if (!process.argv.includes('--cleanup')) {
      fs.writeFileSync('/tmp/engineering-note-demo-manifest.json', JSON.stringify({ project: 'engineering-library', document: 'architecture/current-state.md', navigation: 'Open a case URL, then click the passage note indicator. For your browser cookie, use Seed current reader in both languages.', owner: 'dedicated local demonstration browser; use Seed current reader for your own cookie', cases }, null, 2));
      console.log(`${cases.length} persisted cases; /tmp/engineering-note-demo-manifest.json`);
      // Re-running is intentionally part of the idempotence check.
    } else console.log('Only this demonstration reader’s tagged examples removed.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
