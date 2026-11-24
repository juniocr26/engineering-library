/* eslint-disable @typescript-eslint/no-require-imports */
// One shared dataset. An ephemeral browser measures canonical DOM anchors, never owns data.
const fs = require('node:fs');
async function runDemos({ base = process.env.BROWSER_BASE_URL || 'http://localhost:3099', cleanup = false, manifestOnly = false } = {}) {
  if (!['localhost', '127.0.0.1'].includes(new URL(base).hostname)) throw Error('Local development only');
  const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
  const inspectAnchors = require('./demo-anchors.cjs');
  const { noteDemos, localizedDemoBody } = await import('../lib/note-demos.ts');
  const { textAnchor } = await import('../lib/text-anchors.ts');
  const browser = await chromium.launch({ executablePath: process.env.PLAYWRIGHT_EXECUTABLE_PATH, headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.setDefaultTimeout(90000);
  const project = 'engineering-library';
  const documents = ['architecture/current-state.md', 'img/visual-components.md'];
  const anchors = [];
  const cases = [];
  try {
    for (const language of ['en', 'pt-BR']) for (const document of documents) {
      const query = new URLSearchParams({ project, document, language });
      const identity = await page.request.get(`${base}/api/highlights?${query}`);
      if (!identity.ok()) throw Error(`Read failed: ${identity.status()}`);
      const { csrf_token } = await identity.json();
      const headers = { Origin: new URL(base).origin, 'X-Annotation-CSRF': csrf_token };
      if (cleanup) {
        const response = await page.request.delete(`${base}/api/note-demos?${query}`, { headers });
        if (!response.ok()) throw Error(`Cleanup failed: ${response.status()}`);
        console.log('Shared demonstration records removed; manual annotations preserved.');
        return;
      }
      await page.goto(`${base}/projects/${project}/docs/${document}?lang=${language}`);
      await page.locator('.reader[data-pagination="ready"]').waitFor();
      if (!manifestOnly) {
        const blocks = await page.locator('.reader-measure [data-highlight-block]').evaluateAll(nodes => [...new Map(nodes.filter(n => !n.dataset.highlightUnsupported && n.textContent.length > 8).map(n => [n.dataset.highlightBlock, { id: n.dataset.highlightBlock, text: n.textContent }])).values()]);
        if (blocks.length < noteDemos.length) throw Error(`Insufficient canonical blocks: ${document}`);
        const save = async (key, block, data) => {
          const segment = textAnchor(block.id, block.text, 0, Math.min(block.text.length, 40));
          const response = await page.request.post(`${base}/api/note-demos?${query}`, { headers, data: { demo_key: `visual-${language}-${document.replace(/[^a-z0-9]/g, '-')}-${key}`, segments: [segment], body: '', ...data } });
          if (!response.ok()) throw Error(`Seed ${language}/${document}/${key}: ${response.status()} ${await response.text()}`);
          cases.push({ document, language, case: key, anchor: segment.block, href: `${base}/projects/${project}/docs/${document}?lang=${language}#${encodeURIComponent(segment.block)}` });
        };
        for (let i = 0; i < noteDemos.length; i++) await save(String(i + 1).padStart(2, '0'), blocks[i], { body: localizedDemoBody(noteDemos[i][1], language), color: ['yellow', 'blue', 'pink', 'orange', 'purple', 'red', 'green'][i % 7], remove_color: i === 14 });
        for (const [index, kind] of ['bookmark', 'bookmark', 'bookmark', 'highlight'].entries()) {
          await save(`${kind}-${index}`, blocks[[0, Math.floor(blocks.length / 2), blocks.length - 1, Math.min(16, blocks.length - 1)][index]], { kind, color: 'yellow' });
        }
      }
      anchors.push(...await inspectAnchors(page, document, language));
    }
    const report = { project, documents, dataset: 'shared local PostgreSQL annotations', anchors, valid_anchors: anchors.filter(item => item.valid).length, invalid_anchors: anchors.filter(item => !item.valid).length, cases };
    fs.writeFileSync('/tmp/engineering-note-demo-manifest.json', JSON.stringify(report, null, 2));
    console.log(`${manifestOnly ? 'Read-only manifest' : `${cases.length} shared cases reconciled`}; ${report.valid_anchors} valid anchors, ${report.invalid_anchors} invalid anchors; /tmp/engineering-note-demo-manifest.json`);
    return report;
  } finally { await browser.close(); }
}
module.exports = { runDemos };
if (require.main === module) runDemos({ cleanup: process.argv.includes('--cleanup'), manifestOnly: process.argv.includes('--manifest') }).catch(error => { console.error(error); process.exit(1); });
