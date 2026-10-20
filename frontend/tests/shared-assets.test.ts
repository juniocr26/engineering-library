import test from 'node:test';
import assert from 'node:assert/strict';
import { resolveDocumentLink } from '../lib/document-links.ts';
import { mkdtemp, mkdir, writeFile, symlink, rm } from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { GET } from '../app/api/shared-assets/[...path]/route.ts';

for (const language of ['en', 'pt-BR'] as const) {
  test(`${language}: shared image URLs are independent of project and document depth`, () => {
    for (const project of ['engineering-library', 'env-auditor']) {
      assert.equal(resolveDocumentLink(project, 'guides/nested/example.md', language, '/img/diagrams/reader-storage.svg', true), '/api/shared-assets/diagrams/reader-storage.svg');
      assert.equal(resolveDocumentLink(project, 'README', language, '/assets/writer-library.jpg', true), '/assets/writer-library.jpg');
    }
  });
}
test('shared assets serve images and reject non-images and traversal', async () => {
  const request = new Request('http://localhost/api/shared-assets/example');
  const get = (parts: string[]) => GET(request, { params: Promise.resolve({path: parts}) });
  const svg = await get(['diagrams', 'reader-storage.svg']);
  assert.equal(svg.status, 200);
  assert.equal(svg.headers.get('content-type'), 'image/svg+xml');
  assert.match(svg.headers.get('content-security-policy')!, /sandbox/);
  assert.match(await svg.text(), /Next.js reader/);
  for (const parts of [['README.md'], ['..', 'secret.svg'], ['diagrams/reader-storage.svg'], ['missing.svg'], ['diagrams', '..', 'reader-storage.svg']]) {
    assert.equal((await get(parts)).status, 404);
  }
});

test('shared image symlinks cannot expose files outside IMG', async () => {
  const temporary = await mkdtemp(path.join(os.tmpdir(), 'library-img-'));
  const previous = process.env.DOCUMENTATION_ROOT;
  try {
    await mkdir(path.join(temporary, 'img'));
    await writeFile(path.join(temporary, 'outside.svg'), '<svg/>');
    await symlink(path.join(temporary, 'outside.svg'), path.join(temporary, 'img', 'escape.svg'));
    process.env.DOCUMENTATION_ROOT = path.join(temporary, 'projects');
    const result = await GET(new Request('http://localhost/api/shared-assets/escape.svg'), { params: Promise.resolve({path: ['escape.svg']}) });
    assert.equal(result.status, 404);
  } finally {
    if (previous === undefined) delete process.env.DOCUMENTATION_ROOT;
    else process.env.DOCUMENTATION_ROOT = previous;
    await rm(temporary, {recursive: true, force: true});
  }
});
