/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const base = process.env.BROWSER_BASE_URL || 'http://localhost:3000';
const path = '/projects/engineering-library/docs/architecture/current-state.md';
const query = 'project=engineering-library&document=architecture%2Fcurrent-state.md&language=en';
const svg = '<svg xmlns="http://www.w3.org/2000/svg" width="80" height="24"><rect width="80" height="24" fill="navy"/></svg>';
const animatedSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="80" height="24"><rect width="80" height="24" fill="navy"><animate attributeName="opacity" values="1;.3;1" dur="1s" repeatCount="indefinite"/></rect></svg>';
const formats = {
  'image.png': ['image/png', fs.readFileSync('public/assets/icon-512.png')],
  'image.jpg': ['image/jpeg', fs.readFileSync('public/assets/writer-library.jpg')],
  'image.webp': ['image/webp', fs.readFileSync('public/assets/manuscript/parchment/aged-fibers.webp')],
};
const gif = Buffer.from('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7', 'base64');
const source = '# Rich content 📚 ação\n\n**Markdown** <em>mixed HTML</em>\n\n<span style="color:navy">Styled presentation</span>\n\n<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 24"><text y="18">Inline SVG</text></svg>\n\n![Remote SVG](https://unlisted.test/badge.svg)\n\n![Animated SVG](https://unlisted.test/animated.svg)\n\n![GIF](https://unlisted.test/image.gif)\n\n![PNG](https://unlisted.test/image.png)\n\n![JPEG](https://unlisted.test/image.jpg)\n\n![WebP](https://unlisted.test/image.webp)\n\n![Broken URL](https://unlisted.test/missing.png)\n\n![Missing host](https://absent.test/image.webp)\n\n<img src="https://unlisted.test/html.svg" alt="HTML image">\n\n| Index | Value |\n|---|---|\n' + Array.from({ length: 1100 }, (_, i) => `| ${i} | retained |`).join('\n') + '\n\n```typescript\nconst answer = 42;\n```\n\n```mermaid\nflowchart LR\n A["<b>HTML label</b>"] --> B\n```\n\n```mermaid\ninvalid diagram\n```\n\n<script>parent.pwned=1</script>\n\nEnd of rich note.\n\n' + 'Long-form notes retain Unicode ação 📚 and original source. '.repeat(2500) + '\n\n' + fs.readFileSync(`${process.env.DOCUMENTATION_ROOT || '../docs/projects'}/engineering-library/docs/en/architecture/current-state.md`, 'utf8');
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  try {
    for (const width of [1440, 390]) {
      const context = await browser.newContext({ viewport: { width, height: 1000 } });
      const page = await context.newPage(); page.setDefaultTimeout(30000);
      const errors = []; page.on('pageerror', error => errors.push(error.message));
      await page.route('https://unlisted.test/**', route => {
        const url = route.request().url();
        if (url.endsWith('missing.png')) return route.fulfill({ status: 404, body: '' });
        const format = formats[url.split('/').at(-1)];
        if (format) return route.fulfill({ contentType: format[0], body: format[1] });
        return route.fulfill({ contentType: url.endsWith('.gif') ? 'image/gif' : 'image/svg+xml', body: url.endsWith('.gif') ? gif : url.endsWith('animated.svg') ? animatedSvg : svg });
      });
      await page.route('https://absent.test/**', route => route.abort('namenotresolved'));
      await page.goto(`${base}${path}?lang=en`);
      await page.locator('.reader[data-pagination="ready"]').waitFor();
      await page.locator('.reader-pages [data-highlight-block]:not([data-highlight-unsupported]) p').first().waitFor();
      const ids = await page.evaluate(async ({ query, source }) => {
        const { csrf_token } = await (await fetch(`/api/highlights?${query}`)).json();
        const p = document.querySelector('.reader-pages [data-highlight-block]:not([data-highlight-unsupported]) p');
        const block = p.closest('[data-highlight-block]'); const text = block.textContent;
        const headers = { 'Content-Type': 'application/json', 'X-Annotation-CSRF': csrf_token };
        const highlightResponse = await fetch(`/api/highlights?${query}`, { method: 'POST', headers, body: JSON.stringify({ color: 'green', segments: [{ block: block.dataset.highlightBlock, start: 0, end: 20, exact: text.slice(0, 20), prefix: '', suffix: text.slice(20, 68) }] }) });
        if (!highlightResponse.ok) throw Error(`highlight ${highlightResponse.status}`);
        const highlight = await highlightResponse.json();
        const noteResponse = await fetch(`/api/notes?${query}`, { method: 'POST', headers, body: JSON.stringify({ highlight_id: highlight.id, body: source }) });
        if (!noteResponse.ok) throw Error(`note ${noteResponse.status}`);
        return { highlight: highlight.id, note: (await noteResponse.json()).id, token: csrf_token };
      }, { query, source });
      try {
        await page.reload();
        await page.getByRole('button', { name: 'Open saved note', exact: true }).click();
        assert.equal(await page.locator('#note-draft').inputValue(), source);
        let resumeWorker;
        const heldWorker = new Promise(resolve => { resumeWorker = resolve; });
        const workerPattern = '**/*note-worker*';
        await page.route(workerPattern, async route => { await heldWorker; await route.continue().catch(() => {}); });
        await page.getByRole('button', { name: 'Preview', exact: true }).click();
        await page.getByRole('button', { name: 'Cancel rendering', exact: true }).click();
        await page.getByRole('status').filter({ hasText: 'Preview stopped.' }).waitFor();
        resumeWorker();
        await page.unroute(workerPattern);
        await page.getByRole('button', { name: 'Retry', exact: true }).click();
        const preview = page.getByRole('dialog', { name: 'Note preview', exact: true });
        await preview.locator('h1').first().waitFor().catch(async error => { console.log(await preview.innerText()); throw error; });
        assert.ok((await preview.innerText()).includes('End of rich note.'));
        assert.ok(await preview.locator('tbody tr').count() >= 1100);
        await preview.locator('img.missing-image').nth(1).waitFor();
        assert.equal(await preview.locator('img.missing-image').count(), 2);
        for (const alt of ['Remote SVG', 'Animated SVG', 'GIF', 'PNG', 'JPEG', 'WebP', 'HTML image']) {
          assert.ok(await preview.getByAltText(alt, { exact: true }).evaluate(img => img.complete && img.naturalWidth > 0));
        }
        assert.equal(await preview.locator('script,[onload],[onerror]').count(), 0);
        assert.equal(await page.evaluate(() => window.pwned), undefined);
        assert.ok(await preview.locator('.note-html-frame').count() >= 3);
        const isolated = await preview.locator('.note-html-frame').first().elementHandle();
        const isolatedFrame = await isolated.contentFrame();
        assert.equal(await isolatedFrame.evaluate(() => { try { return !!parent.document; } catch { return false; } }), false);
        assert.equal(await isolatedFrame.evaluate(async url => { try { await fetch(url); return 'unexpected access'; } catch { return 'blocked'; } }, `${base}/api/notes?${query}`), 'blocked');
        await preview.locator('.reader-diagram img').waitFor();
        await preview.locator('.reader-diagram [role=alert]').waitFor();
        assert.equal(await preview.locator('.expandable-media > .media-controls').count(), 0);
        const image = preview.getByRole('button', { name: 'Expand image: Remote SVG', exact: true });
        assert.equal(await image.evaluate(node => getComputedStyle(node).cursor), 'pointer');
        await image.click();
        await page.getByRole('dialog', { name: 'Remote SVG', exact: true }).waitFor();
        const viewer = page.getByRole('dialog', { name: 'Remote SVG', exact: true });
        await viewer.getByRole('button', { name: 'Zoom in', exact: true }).click();
        assert.equal(await viewer.locator('output').innerText(), '125%');
        await viewer.getByRole('button', { name: 'Reset zoom', exact: true }).click();
        assert.equal(await viewer.locator('output').innerText(), '100%');
        await page.keyboard.press('Escape');
        await image.focus();
        await page.keyboard.press('Enter');
        await viewer.waitFor();
        await page.keyboard.press('Escape');
        await image.focus();
        await page.keyboard.press('Space');
        await viewer.waitFor();
        await page.keyboard.press('Escape');
        await preview.getByRole('button', { name: 'Expand diagram: Documentation diagram', exact: true }).click();
        await page.getByRole('dialog', { name: 'Documentation diagram', exact: true }).waitFor();
        await page.keyboard.press('Escape');
        assert.ok(await preview.getByRole('button', { name: 'Expand table', exact: true }).count());
        for (let i = 0; i < 8; i++) { const button = preview.getByRole('button', { name: 'Zoom in', exact: true }); if (await button.isEnabled()) await button.click(); }
        assert.equal(await preview.locator('output').innerText(), '500%');
        await preview.getByRole('button', { name: 'Pan mode', exact: true }).click();
        assert.equal(await preview.locator('.note-preview-scroll').getAttribute('data-pan'), 'true');
        await preview.getByRole('button', { name: 'Reset zoom', exact: true }).click();
        await preview.locator('.note-preview-scroll').evaluate(node => node.scrollTo(0, 0));
        await page.screenshot({ path: `/tmp/note-rich-${width}.png` });
        await preview.getByRole('button', { name: 'Return to edit', exact: true }).click();
        await page.locator('#note-draft').fill(source + '\nSaved from editor.');
        await page.getByRole('button', { name: 'Save', exact: true }).click();
        await page.getByRole('status').filter({ hasText: 'Note updated successfully.' }).waitFor();
        await page.getByRole('button', { name: 'Close note', exact: true }).click();
        await page.reload(); await page.getByRole('button', { name: 'Open saved note', exact: true }).click();
        assert.equal(await page.locator('#note-draft').inputValue(), source + '\nSaved from editor.');
        await page.getByRole('button', { name: 'Close note', exact: true }).click();
        await page.goto(`${base}${path}?lang=pt-BR`);
        await page.locator('.reader[data-pagination="ready"]').waitFor();
        assert.equal(await page.getByRole('button', { name: 'Abrir nota salva', exact: true }).count(), 0);
        assert.deepEqual(errors, []);
        console.log(`PASS rich note ${width}: mixed HTML, isolated SVG/scripts, arbitrary image hosts, GIF, 1100 rows, Mermaid success/failure, local fallback, expansion, zoom, save/reload, language isolation`);
      } finally {
        await page.evaluate(async ({ ids, query }) => {
          const headers = { 'X-Annotation-CSRF': ids.token };
          await fetch(`/api/notes/${ids.note}?${query}`, { method: 'DELETE', headers });
          await fetch(`/api/highlights/${ids.highlight}?${query}`, { method: 'DELETE', headers });
        }, { ids, query });
        await context.close();
      }
    }
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
