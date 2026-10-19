/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
(async () => {
 const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
 try {
  for (const width of [1440, 390]) {
   const page = await browser.newPage({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
   page.setDefaultTimeout(20000);
   const ready = () => page.locator('.reader[data-pagination="ready"] .reader-stage[aria-busy="false"]').waitFor();
   const position = () => page.locator('.reader-pages .reader-controls span[aria-live]').innerText();
   async function switchTo(lang) {
    await page.locator(`.reader-pages a[hreflang="${lang}"]`).click();
    await page.waitForURL(url => url.searchParams.get('lang') === lang);
    await ready();
   }
   for (const path of ['/projects/go-image-optimizer/docs/adr/001-native-image-codecs.md', '/projects/engineering-library']) {
    await page.goto(`http://localhost:3000${path}?lang=pt-BR`); await ready();
    await switchTo('en'); assert.match(await position(), /Page 1/);
    await switchTo('pt-BR');
    await page.locator('.reader-pages .reader-controls button').last().click(); await ready();
    assert.doesNotMatch(await position(), /Página 1(?:–| de)/);
    await switchTo('en'); assert.doesNotMatch(await position(), /Page 1(?:–| of)/);
    await switchTo('pt-BR'); assert.doesNotMatch(await position(), /Página 1(?:–| de)/);
    await page.goBack(); await ready(); assert.doesNotMatch(await position(), /Page 1(?:–| of)/);
    await page.goForward(); await ready(); assert.doesNotMatch(await position(), /Página 1(?:–| de)/);
    await page.locator('.reader-pages a[hreflang="en"]').click();
    await page.waitForURL(url => url.searchParams.get('lang') === 'en');
    await page.locator('.reader-pages a[hreflang="pt-BR"]').click();
    await page.waitForURL(url => url.searchParams.get('lang') === 'pt-BR'); await ready();
    assert.doesNotMatch(await position(), /Página 1(?:–| de)/);
    await switchTo('en');
    if (width === 1440) { await page.setViewportSize({ width: 768, height: 900 }); await ready(); assert.doesNotMatch(await position(), /Page 1(?:–| of)/); await page.setViewportSize({ width, height: 900 }); await ready(); }
    // Stop at the last physical page without crossing into another chapter.
    for (let i = 0; i < 100; i++) {
      const numbers = (await position()).match(/\d+/g).map(Number);
      if (numbers[numbers.length - 2] >= numbers[numbers.length - 1]) break;
      await page.locator('.reader-pages .reader-controls button').last().click(); await ready();
    }
    await switchTo('pt-BR'); assert.doesNotMatch(await position(), /Página 1(?:–| de)/);
    console.log(`PASS ${width} ${path}: first/intermediate/last, round trip, back/forward, rapid switch, resize`);
   }
   async function switchLanguage(lang) {
    await page.locator(`.reader-pages a[hreflang="${lang}"]`).click();
    await page.waitForURL(url => url.searchParams.get('lang') === lang); await ready();
   }
   await page.goto('http://localhost:3000/projects/go-image-optimizer/docs/faq/study-guide.md?lang=en'); await ready();
   for (let i = 0; i < 4; i++) { await page.locator('.reader-pages .reader-controls button').last().click(); await ready(); }
   await switchLanguage('pt-BR'); assert.doesNotMatch(await position(), /Página 1(?:–| de)/);
   console.log(`PASS ${width}: long document`);
   await page.goto('http://localhost:3000/projects/go-image-optimizer/docs/operations/source-review.md?lang=en#inspected-implementation-sources'); await ready();
   await page.locator('.reader-pages .source-reference').first().click(); await ready();
   await switchLanguage('pt-BR');
   assert.ok(await page.locator('.reader-measure .source-reference[aria-expanded="true"]').count());
   console.log(`PASS ${width}: expanded source`);
   await page.goto('http://localhost:3000/projects/go-image-optimizer/docs/operations/completion-checklist.md?lang=en'); await ready();
   await switchLanguage('pt-BR'); await switchLanguage('en');
   console.log(`PASS ${width}: short document round trip`);
   await page.close();
  }
 } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
