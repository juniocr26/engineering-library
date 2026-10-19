/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || '/tmp/numbering-browser/node_modules/playwright');
const assert = require('node:assert/strict');
const base = process.env.BROWSER_BASE_URL || 'http://localhost:3000';
const documentId = 'architecture/current-state.md';
const path = `/projects/engineering-library/docs/${documentId}?lang=en`;
const ready = async page => { await page.locator('.reader[data-pagination="ready"]').waitFor(); await page.waitForFunction(() => document.querySelector('.reader-stage')?.getAttribute('aria-busy') === 'false'); };
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  try {
    for (const width of [1440, 390]) {
      const context = await browser.newContext({ viewport: { width, height: 1000 }, reducedMotion: 'reduce' });
      const page = await context.newPage(); page.setDefaultTimeout(25000);
      const errors = []; page.on('pageerror', error => errors.push(error.message));
      const created = [];
      try {
        await page.goto(base + path); await ready(page);
        await page.getByRole('button', { name: 'Highlights and Notes', exact: true }).click();
        const panel = page.getByRole('dialog', { name: 'Highlights and Notes', exact: true });
        await panel.getByText('No highlights or notes in this project.', { exact: true }).waitFor();
        await page.keyboard.press('Escape'); await panel.waitFor({ state: 'detached' });
        const anchors = await page.locator('.reader-measure [data-highlight-block]:not([data-highlight-unsupported])').evaluateAll(blocks => blocks.filter(b => b.textContent.length > 15).slice(0, 10).map(b => ({ block: b.dataset.highlightBlock, start: 0, end: 12, exact: b.textContent.slice(0,12), prefix: '', suffix: b.textContent.slice(12,60) })));
        assert.ok(anchors.length >= 9);
        const mutate = async (resource, method, body, document = documentId, language = 'en') => page.evaluate(async args => {
          const query = new URLSearchParams({ project: 'engineering-library', document: args.document, language: args.language });
          const identity = await (await fetch(`/api/highlights?${query}`)).json();
          const response = await fetch(`/api/${args.resource}?${query}`, { method: args.method, headers: { 'Content-Type': 'application/json', 'X-Reader-CSRF': identity.csrf_token }, body: args.body === undefined ? undefined : JSON.stringify(args.body) });
          if (!response.ok) throw Error(`Mutation ${response.status}`);
          return response.status === 204 ? null : response.json();
        }, { resource, method, body, document, language });
        const colors = ['yellow', 'blue', 'pink', 'orange', 'purple', 'red', 'green'];
        for (let index = 0; index < 9; index++) {
          const highlight = await mutate('highlights', 'POST', { color: colors[index % 7], segments: [anchors[index]] });
          created.push({ resource: `highlights/${highlight.id}` });
          if (index < 3) {
            const note = await mutate('notes', 'POST', { highlight_id: highlight.id, body: index === 0 ? '**' + '👩🏽‍💻'.repeat(101) + '**' : index === 1 ? '**' + 'a'.repeat(100) + '**' : 'Independent note' });
            created.push({ resource: `notes/${note.id}` });
          }
          if (index === 2) await mutate(`highlights/${highlight.id}`, 'DELETE');
        }
        const invalid = await mutate('highlights', 'POST', { color: 'blue', segments: [{ ...anchors[0], block: 'missing-source-anchor' }] }); created.push({ resource: `highlights/${invalid.id}` });
        const pt = await mutate('highlights', 'POST', { color: 'red', segments: [anchors[0]] }, documentId, 'pt-BR'); created.push({ resource: `highlights/${pt.id}`, language: 'pt-BR' });
        // Reload the document's highlight session after API seeding.
        await page.reload(); await ready(page);
        const position = await page.locator('.reader-controls span').first().innerText();
        await page.getByRole('button', { name: 'Highlights and Notes', exact: true }).click();
        await panel.locator('.annotation-entry').nth(9).waitFor();
        assert.equal(await panel.locator('.annotation-entry').count(), 10);
        assert.equal(await panel.locator('.annotation-note').count(), 3);
        assert.equal(await panel.getByRole('button', { name: 'Preview complete note', exact: true }).count(), 1);
        const filterButton = panel.getByRole('button', { name: 'Filter annotations', exact: true });
        const select = async name => { await filterButton.click(); await panel.getByRole('menuitemradio', { name, exact: true }).click(); await panel.locator('.annotation-list[aria-busy="false"]').waitFor({ state: 'attached' }); };
        await filterButton.click(); await panel.getByRole('menu').waitFor(); await page.keyboard.press('Escape'); assert.equal(await panel.getByRole('menu').count(), 0); assert.ok(await panel.isVisible());
        await filterButton.click(); await panel.locator('h2').click(); assert.equal(await panel.getByRole('menu').count(), 0);
        await filterButton.click(); await page.keyboard.press('End'); assert.equal(await page.locator(':focus').getAttribute('role'), 'menuitemradio'); await page.keyboard.press('Escape');
        const counts = { Yellow: 2, Blue: 3, Pink: 0, Orange: 1, Purple: 1, Red: 1, Green: 1 };
        for (const [color, count] of Object.entries(counts)) {
          await select(`${color} (${count})`); assert.equal(await panel.locator('.annotation-entry').count(), count);
          if (!count) await panel.getByText('No highlights in this color.', { exact: true }).waitFor();
        }
        await select('Notes (3)'); assert.equal(await panel.locator('.annotation-entry').count(), 3);
        const scroll = panel.locator('.reader-panel-content'); await scroll.evaluate(node => node.scrollTop = node.scrollHeight);
        const scrollTop = await scroll.evaluate(node => node.scrollTop);
        await panel.getByRole('button', { name: 'Preview complete note', exact: true }).click();
        const preview = page.getByRole('dialog', { name: 'Note preview', exact: true }); await preview.waitFor();
        assert.equal(await preview.getByRole('button', { name: 'Return to edit', exact: true }).count(), 0);
        await preview.getByRole('button', { name: 'Close', exact: true }).click();
        assert.equal(await scroll.evaluate(node => node.scrollTop), scrollTop);
        assert.equal(await panel.locator('.annotation-entry').count(), 3);
        assert.equal(await page.locator('.reader-controls span').first().innerText(), position);
        // Long excerpts preserve whole emoji and short notes need no preview icon.
        assert.equal(await panel.locator('.annotation-note').filter({ hasText: '👩🏽‍💻' }).locator('span').innerText(), 'Note: ' + '👩🏽‍💻'.repeat(100) + '…');
        await panel.locator('.annotation-entry').filter({ hasText: 'Independent note' }).locator('.annotation-location').click();
        await page.locator('.reader-pages [data-annotation-target="true"]').waitFor();
        // Open the orphan note editor, whose preview must still return to the draft.
        await page.locator('.reader-note-indicator').first().click();
        const editor = page.getByRole('dialog', { name: 'Note editor', exact: true }); await editor.waitFor();
        await editor.locator('textarea').fill('Unsaved test draft'); await editor.getByRole('button', { name: 'Preview', exact: true }).click();
        await preview.getByRole('button', { name: 'Return to edit', exact: true }).click(); assert.equal(await editor.locator('textarea').inputValue(), 'Unsaved test draft');
        page.once('dialog', dialog => dialog.accept()); await editor.getByRole('button', { name: 'Close note', exact: true }).click();
        await page.getByRole('button', { name: 'Highlights and Notes', exact: true }).click();
        await panel.locator('.annotation-entry').first().waitFor(); await panel.locator('.annotation-location').first().click();
        await page.getByText('This annotation location could not be verified. The annotation is preserved.', { exact: true }).waitFor();
        // A project-level annotation can route back from the TOC to its source document.
        await page.goto(`${base}/projects/engineering-library?lang=en`); await ready(page);
        await page.getByRole('button', { name: 'Highlights and Notes', exact: true }).click();
        await panel.locator('.annotation-entry').filter({ hasText: 'Independent note' }).locator('.annotation-location').click();
        await page.waitForURL('**/docs/architecture/current-state.md?lang=en&annotation=note-*'); await ready(page);
        await page.locator('.reader-pages [data-annotation-target="true"]').waitFor();
        await page.getByRole('button', { name: 'Highlights and Notes', exact: true }).click();
        await panel.locator('.annotation-entry').first().waitFor();
        const bounds = await panel.boundingBox(); assert.ok(bounds.x >= 0 && bounds.x + bounds.width <= width);
        await page.screenshot({ path: `/tmp/annotations-${width}.png` });
        // A stale record whose document left the catalog must not open a 404.
        await page.keyboard.press('Escape');
        await page.route('**/api/annotations?**', async route => {
          const response = await route.fetch();
          const data = await response.json();
          data.annotations = [{ ...data.annotations[0], document: 'removed-document.md' }];
          await route.fulfill({ response, json: data });
        }, { times: 1 });
        await page.getByRole('button', { name: 'Highlights and Notes', exact: true }).click();
        await panel.locator('.annotation-location').click();
        await panel.getByText('The source document is unavailable. The annotation is preserved.', { exact: true }).waitFor();
        await page.keyboard.press('Escape');
        await page.getByRole('button', { name: 'Highlights and Notes', exact: true }).click();
        await panel.locator('.annotation-entry').nth(9).waitFor();
        // Abort an old English filter request while switching language in place.
        await page.route('**/api/annotations?**', async route => {
          const url = new URL(route.request().url());
          if (url.searchParams.get('filter') === 'yellow' && url.searchParams.get('language') === 'en') await new Promise(resolve => setTimeout(resolve, 500));
          await route.continue().catch(() => {});
        });
        await filterButton.click(); await panel.getByRole('menuitemradio', { name: 'Yellow (2)', exact: true }).click();
        await page.locator('.reader-pages .reader-document-languages a[href*="lang=pt-BR"]').evaluate(link => link.click());
        const portuguese = page.getByRole('dialog', { name: 'Destaques e notas', exact: true });
        await portuguese.locator('.annotation-entry').waitFor();
        await page.waitForTimeout(600);
        assert.equal(await portuguese.locator('.annotation-entry').count(), 1);
        assert.equal(await portuguese.locator('.annotation-note').count(), 0);
        await portuguese.getByRole('button', { name: 'Filtrar anotações', exact: true }).click();
        await portuguese.getByRole('menuitemradio', { name: 'Vermelho (1)', exact: true }).waitFor();
        await page.keyboard.press('Escape'); await page.keyboard.press('Escape');
        await page.goto(`${base}/projects/env-auditor?lang=en`); await ready(page);
        await page.getByRole('button', { name: 'Highlights and Notes', exact: true }).click();
        await panel.getByText('No highlights or notes in this project.', { exact: true }).waitFor();
        assert.deepEqual(errors, []);
        console.log(`PASS annotations ${width}px: filters/counts, orphan notes, excerpts, preview context, scroll/focus, verified navigation, unresolved anchors, TOC, keyboard`);
      } catch (error) {
        console.log(await page.locator('dialog').evaluateAll(nodes => nodes.map(node => ({ open: node.open, text: node.innerText }))));
        await page.screenshot({ path: `/tmp/annotations-failure-${width}.png` });
        throw error;
      } finally {
        // Only records created with this isolated browser identity are removed.
        for (const entry of created.reverse()) {
          await page.evaluate(async entry => {
            const query = new URLSearchParams({ project: 'engineering-library', document: 'architecture/current-state.md', language: entry.language || 'en' });
            const identity = await (await fetch(`/api/highlights?${query}`)).json();
            await fetch(`/api/${entry.resource}?${query}`, { method: 'DELETE', headers: { 'X-Reader-CSRF': identity.csrf_token } });
          }, entry).catch(() => {});
        }
        await context.close();
      }
    }
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
