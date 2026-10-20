/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
(async () => {
  const base = process.env.BROWSER_BASE_URL || 'http://localhost:3099';
  const browser = await chromium.launch({ executablePath: process.env.PLAYWRIGHT_EXECUTABLE_PATH, headless: true });
  try {
    for (const language of ['en', 'pt-BR']) {
      const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
      page.setDefaultTimeout(90000);
      await page.goto(`${base}/projects/engineering-library?lang=${language}`);
      await page.locator('.reader[data-pagination="ready"]').waitFor();
      assert.ok(await page.locator('a[href*="img/visual-components.md"]').count());
      await page.goto(`${base}/projects/engineering-library/docs/img/visual-components.md?lang=${language}`);
      await page.locator('.reader[data-pagination="ready"]').waitFor();
      // Measurement contains every logical unit, including media on later leaves.
      for (const src of ['/assets/writer-library.jpg', '/api/shared-assets/diagrams/reader-storage.svg', '/assets/icon-512.png', 'https://www.w3.org/Icons/w3c_home.svg', 'https://www.w3.org/Icons/valid-xhtml10.gif', '/assets/image-missing.svg']) {
        const img = page.locator(`img[src="${src}"]`).first();
        await img.waitFor({state: 'attached'});
        await page.waitForFunction(element => element.complete && element.naturalWidth > 0, await img.elementHandle());
      }
      await page.waitForFunction(() => Array.from(document.querySelectorAll('.reader-diagram img')).filter(img => img.complete && img.naturalWidth > 0).length >= 2);
      const notes = await page.evaluate(async language => (await (await fetch(`/api/notes?project=engineering-library&document=img%2Fvisual-components.md&language=${language}`)).json()).notes, language);
      assert.equal(notes.length, 0, 'static guide must work without seeded identity');
      await page.getByRole('button', {name: language === 'en' ? 'Expand image' : 'Ampliar imagem', exact:true}).filter({visible:true}).first().click();
      const viewer = page.locator('dialog.media-viewer');
      await viewer.waitFor();
      const picture = viewer.locator('img');
      const before = await picture.getAttribute('style');
      for (let i = 0; i < 3; i++) await viewer.getByRole('button', {name: language === 'en' ? 'Zoom in' : 'Ampliar', exact:true}).click();
      assert.notEqual(await picture.getAttribute('style'), before);
      const zoomed = await picture.getAttribute('style');
      const bounds = await picture.boundingBox();
      await page.mouse.move(bounds.x + bounds.width / 2, bounds.y + bounds.height / 2);
      await page.mouse.down(); await page.mouse.move(bounds.x + bounds.width / 2 + 40, bounds.y + bounds.height / 2 + 40, {steps: 5}); await page.mouse.up();
      assert.notEqual(await picture.getAttribute('style'), zoomed, 'drag must pan the zoomed image');
      await page.keyboard.press('Escape');
      await viewer.waitFor({state:'detached'});
      assert.equal((await page.request.get(`${base}/api/shared-assets/README.md`)).status(), 404);
      console.log(`PASS ${language}: canonical TOC, seed-free media, SVG, HTTPS, GIF, fallback, Mermaid, fullscreen and zoom`);
      await page.close();
    }
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
