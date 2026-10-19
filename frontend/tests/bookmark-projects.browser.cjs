/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const base = process.env.BROWSER_BASE_URL || 'http://localhost:3000';
  try {
    const context = await browser.newContext();
    const page = await context.newPage();
    let saved = [
      { id: 1, project: 'engineering-library', document: 'README', language: 'en', anchor: 'engineering-library', excerpt: 'Library saved' },
      { id: 2, project: 'env-auditor', document: 'README', language: 'en', anchor: 'env-auditor', excerpt: 'ENV saved' },
    ];
    const requested = [];
    await page.route('**/api/bookmarks{,?*,/**}', async route => {
      const request = route.request();
      if (request.method() === 'GET') {
        const project = new URL(request.url()).searchParams.get('project_slug');
        requested.push(project);
        assert.ok(project);
        return route.fulfill({ json: { bookmarks: saved.filter(item => item.project === project), csrf_token: 'fixture' } });
      }
      assert.equal(request.method(), 'DELETE');
      saved = saved.filter(item => item.id !== Number(new URL(request.url()).pathname.split('/').pop()));
      return route.fulfill({ status: 204 });
    });
    async function open(project, language = 'en') {
      await page.goto(`${base}/projects/${project}/docs/README?lang=${language}`);
      await page.locator('.reader[data-pagination="ready"]').waitFor();
      await page.locator('.reader-toolbar').first().getByRole('button', { name: language === 'en' ? 'My Bookmarks' : 'Minhas marcações', exact: true }).click();
      await page.waitForFunction(() => !!document.querySelector('.reader-bookmark-toggle:not(:disabled), .bookmark-ribbon:not(:disabled)'));
    }
    await open('engineering-library');
    assert.equal(await page.locator('.reader-saved-bookmark').count(), 1);
    assert.match(await page.locator('.reader-saved-bookmark').innerText(), /Library saved/);
    await open('env-auditor');
    assert.equal(await page.locator('.reader-saved-bookmark').count(), 1);
    assert.match(await page.locator('.reader-saved-bookmark').innerText(), /ENV saved/);
    await page.reload();
    await page.locator('.reader-toolbar').first().getByRole('button', { name: 'My Bookmarks', exact: true }).click();
    await page.locator('.reader-saved-bookmark').waitFor();
    assert.match(await page.locator('.reader-saved-bookmark').innerText(), /ENV saved/);
    await page.locator('.reader-saved-bookmark').getByRole('button', { name: 'Remove bookmark', exact: true }).click();
    await page.getByText('No bookmarks saved for this project.', { exact: true }).waitFor();
    assert.deepEqual(saved.map(item => item.project), ['engineering-library']);
    await open('engineering-library');
    assert.equal(await page.locator('.reader-saved-bookmark').count(), 1);
    for (const language of ['en', 'pt-BR']) {
      await open('go-image-optimizer', language);
      await page.getByText(language === 'en' ? 'No bookmarks saved for this project.' : 'Nenhuma marcação salva neste projeto.', { exact: true }).waitFor();
      assert.equal(await page.locator('.reader-saved-bookmark').count(), 0);
    }
    assert.ok(requested.includes('env-auditor') && requested.includes('engineering-library') && requested.includes('go-image-optimizer'));
    // Exercise the real same-origin proxy and Rails validation, without mocking fetch.
    const response = await context.request.get(`${base}/api/bookmarks?project_slug=missing-project`);
    assert.equal(response.status(), 422);
    assert.equal((await response.json()).error, 'Invalid project');
    console.log('PASS: project-scoped requests, switching, reload, removal, preservation, bilingual empty states, real proxy validation');
    await context.close();
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
