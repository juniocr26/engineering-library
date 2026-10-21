/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const base = process.env.BROWSER_BASE_URL || 'http://localhost:3000';
const colors = ['yellow', 'blue', 'pink', 'orange', 'purple', 'red', 'green'];
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  try {
    for (const viewport of [{ width: 1440, height: 1000 }, { width: 1440, height: 420 }, { width: 1440, height: 280 }, { width: 768, height: 1024 }, { width: 320, height: 640 }]) {
      const context = await browser.newContext({ viewport, reducedMotion: 'reduce' });
      const page = await context.newPage(); page.setDefaultTimeout(20000);
      const errors = []; page.on('pageerror', error => errors.push(error.message));
      const requested = [];
      // UI regression fixtures only: no Rails mutations or persistent records.
      await page.route('**/api/bookmarks?**', route => route.fulfill({ json: { bookmarks: [], csrf_token: 'fixture' } }));
      await page.route('**/api/highlights?**', route => route.fulfill({ json: { highlights: [], csrf_token: 'fixture' } }));
      await page.route('**/api/notes?**', route => route.fulfill({ json: { notes: [], csrf_token: 'fixture' } }));
      await page.route('**/api/annotations?**', route => {
        requested.push(new URL(route.request().url()).searchParams.get('filter'));
        return route.fulfill({ json: { annotations: [], counts: { all: 0, notes: 0, ...Object.fromEntries(colors.map(color => [color, 0])) }, next_page: null } });
      });
      try {
        await page.goto(`${base}/projects/engineering-library/docs/architecture/current-state.md?lang=pt-BR`);
        await page.locator('.reader[data-pagination="ready"]').waitFor();
        await page.getByRole('button', { name: 'Destaques e notas', exact: true }).click();
        const panel = page.getByRole('dialog', { name: 'Destaques e notas', exact: true });
        await panel.getByText('Nenhum destaque ou nota neste projeto.', { exact: true }).waitFor();
        const trigger = panel.getByRole('button', { name: 'Filtrar anotações', exact: true });
        const menu = panel.getByRole('menu');
        const inspect = async () => menu.evaluate(node => {
          const rect = node.getBoundingClientRect();
          return { topLayer: node.matches(':popover-open'), rect: rect.toJSON(), height: node.clientHeight, scrollHeight: node.scrollHeight,
            content: node.closest('.reader-panel-content').getBoundingClientRect().toJSON(),
            options: [...node.querySelectorAll('button')].map(button => { const r = button.getBoundingClientRect(); const x = Math.min(r.right - 2, r.left + 20), y = r.top + r.height / 2; return { rect: r.toJSON(), hit: button.contains(document.elementFromPoint(x, y)) }; }) };
        });
        await trigger.click(); await menu.waitFor();
        const initial = await inspect();
        assert.ok(initial.topLayer, 'popover escapes the modal scroll container through the top layer');
        assert.equal(initial.options.length, 9);
        assert.ok(initial.rect.x >= 7 && initial.rect.right <= viewport.width - 7);
        assert.ok(initial.rect.top >= 7 && initial.rect.bottom <= viewport.height - 7);
        if (viewport.height >= 420) {
          assert.ok(initial.scrollHeight <= initial.height + 1, 'no unnecessary menu scrollbar');
          assert.ok(initial.options.every(option => option.hit), 'every option is hit-testable above the empty panel content');
        } else {
          await menu.getByRole('menuitemradio', { name: 'Notas (0)', exact: true }).scrollIntoViewIfNeeded();
          assert.ok((await inspect()).options.at(-1).hit, 'last choice reachable on short screens');
        }
        await page.screenshot({ path: `/tmp/annotation-popover-empty-${viewport.width}x${viewport.height}.png` });
        await page.keyboard.press('Home'); await page.keyboard.press('End');
        assert.equal((await page.locator(':focus').innerText()).replace(/\s+/g, ' '), 'Notas (0)');
        await page.keyboard.press('ArrowDown'); assert.equal((await page.locator(':focus').innerText()).replace(/\s+/g, ' '), 'Todas as anotações (0)');
        await page.keyboard.press('Escape'); await menu.waitFor({ state: 'detached' });
        assert.equal(await trigger.evaluate(node => node === document.activeElement), true);
        assert.ok(await panel.isVisible());
        await trigger.click(); await page.mouse.click(viewport.width - 4, viewport.height / 2); await menu.waitFor({ state: 'detached' });
        for (const [name, filter] of [['Amarelo', 'yellow'], ['Azul', 'blue'], ['Rosa', 'pink'], ['Laranja', 'orange'], ['Roxo', 'purple'], ['Vermelho', 'red'], ['Verde', 'green'], ['Notas', 'notes'], ['Todas as anotações', 'all']]) {
          await trigger.click(); await menu.getByRole('menuitemradio', { name: `${name} (0)`, exact: true }).click();
          await menu.waitFor({ state: 'detached' });
          await page.waitForFunction(() => document.querySelector('.annotation-list')?.getAttribute('aria-busy') === 'false');
          assert.equal(requested.at(-1), filter);
        }
        // Repeat with list content underneath the menu, still without persistence.
        await page.route('**/api/annotations?**', route => route.fulfill({ json: {
          annotations: Array.from({ length: 12 }, (_, index) => ({ id: `fixture-${index}`, document: 'architecture/current-state.md', color: 'yellow',
            segments: [{ block: 'fixture', start: 0, end: 7, exact: 'Excerpt', prefix: '', suffix: '' }], note_id: null, body: null, created_at: '2026-10-19T12:00:00Z' })),
          counts: { all: 12, notes: 0, ...Object.fromEntries(colors.map(color => [color, color === 'yellow' ? 12 : 0])) }, next_page: null
        } }), { times: 1 });
        await panel.getByRole('button', { name: 'Fechar painel', exact: true }).click();
        await page.getByRole('button', { name: 'Destaques e notas', exact: true }).click();
        await panel.locator('.annotation-entry').nth(11).waitFor();
        await trigger.click(); await menu.waitFor();
        await menu.getByRole('menuitemradio', { name: 'Amarelo (12)', exact: true }).waitFor();
        const populated = await inspect();
        if (viewport.height >= 420) assert.ok(populated.options.every(option => option.hit), 'menu overlays populated list');
        if (viewport.height >= 640) {
          await panel.locator('.reader-panel-content').evaluate(node => node.scrollTop = 20);
          await page.waitForTimeout(100);
          const scrolled = await inspect(); const triggerAfterScroll = await trigger.boundingBox();
          assert.ok(Math.abs(scrolled.rect.top - triggerAfterScroll.y - triggerAfterScroll.height - 6) < 2, 'follows trigger on panel scroll');
          await panel.locator('.reader-panel-content').evaluate(node => node.scrollTop = 0);
        }
        await page.keyboard.press('Escape');
        // Move the trigger down inside its panel to verify flipping rather than clipping.
        await panel.locator('.annotation-filter').evaluate(node => { node.style.position = 'fixed'; node.style.top = `${innerHeight - 50}px`; });
        await trigger.evaluate(node => node.click()); await menu.waitFor();
        const buttonRect = await trigger.boundingBox(); const moved = await inspect();
        if (viewport.height === 420) assert.ok(moved.rect.bottom <= buttonRect.y, 'flips above when more space is available there');
        await page.setViewportSize({ width: Math.max(320, viewport.width - 60), height: viewport.height + 70 });
        await page.waitForTimeout(100);
        const resized = await inspect();
        assert.ok(resized.rect.x >= 7 && resized.rect.right <= page.viewportSize().width - 7);
        assert.ok(resized.rect.top >= 7 && resized.rect.bottom <= page.viewportSize().height - 7);
        await page.keyboard.press('Escape');
        await panel.locator('.annotation-filter').evaluate(node => { node.style.position = ''; node.style.top = ''; });
        await trigger.click(); await page.screenshot({ path: `/tmp/annotation-popover-${viewport.width}x${viewport.height}.png` });
        assert.deepEqual(errors, []);
        console.log(`PASS popover ${viewport.width}x${viewport.height}: layering, viewport, filters, keyboard, dismissal, resize/flip`);
      } finally { await context.close(); }
    }
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
