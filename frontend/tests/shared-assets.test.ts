import test from 'node:test';
import assert from 'node:assert/strict';
import { resolveDocumentLink } from '../lib/document-links.ts';
import { mkdtemp, mkdir, writeFile, symlink, rm } from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { GET } from '../app/api/shared-assets/[...path]/route.ts';

for (const language of ['en', 'pt-BR'] as const) {
  test(`${language}: shared image URLs are independent of project and document depth`, () => {
    for (const project of ['engineering-library', 'url-shortener']) {
      assert.equal(resolveDocumentLink(project, 'guides/nested/example.md', language, '/api/shared-assets/engineering-library/img/diagrams/reader-storage.webp', true), '/api/shared-assets/engineering-library/img/diagrams/reader-storage.webp');
      assert.equal(resolveDocumentLink(project, 'README', language, '/assets/writer-library.webp', true), '/assets/writer-library.webp');
    }
  });
}
test('shared assets serve images and reject non-images and traversal', async () => {
  const request = new Request('http://localhost/api/shared-assets/example');
  const get = (parts: string[]) => GET(request, { params: Promise.resolve({path: parts}) });
  const image = await get(['engineering-library', 'img', 'diagrams', 'reader-storage.webp']);
  assert.equal(image.status, 200);
  assert.equal(image.headers.get('content-type'), 'image/webp');
  assert.match(image.headers.get('content-security-policy')!, /sandbox/);
  const bytes = Buffer.from(await image.arrayBuffer());
  assert.equal(bytes.subarray(0, 4).toString(), 'RIFF');
  assert.equal(bytes.subarray(8, 12).toString(), 'WEBP');
  for (const parts of [['README.md'], ['..', 'secret.svg'], ['diagrams/reader-storage.webp'], ['missing.svg'], ['diagrams', '..', 'reader-storage.webp']]) {
    assert.equal((await get(parts)).status, 404);
  }
});

test('shared image symlinks cannot expose files outside IMG', async () => {
  const temporary = await mkdtemp(path.join(os.tmpdir(), 'library-img-'));
  const previous = process.env.DOCUMENTATION_ROOT;
  try {
    await mkdir(path.join(temporary, 'sample/img'), { recursive: true });
    await writeFile(path.join(temporary, 'outside.svg'), '<svg/>');
    await symlink(path.join(temporary, 'outside.svg'), path.join(temporary, 'sample/img', 'escape.svg'));
    process.env.DOCUMENTATION_ROOT = temporary;
    const result = await GET(new Request('http://localhost/api/shared-assets/escape.svg'), { params: Promise.resolve({path: ['sample', 'img', 'escape.svg']}) });
    assert.equal(result.status, 404);
  } finally {
    if (previous === undefined) delete process.env.DOCUMENTATION_ROOT;
    else process.env.DOCUMENTATION_ROOT = previous;
    await rm(temporary, {recursive: true, force: true});
  }
});
