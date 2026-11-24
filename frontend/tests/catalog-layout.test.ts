import test from 'node:test';
import assert from 'node:assert/strict';
import { readdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import { documentationEntries, documentationSource, collectionFile } from '../lib/documentation.ts';
import { resolveDocumentLink } from '../lib/document-links.ts';
import { GET } from '../app/api/shared-assets/[...path]/route.ts';

const root = process.env.DOCUMENTATION_ROOT ?? path.resolve(process.cwd(), '../docs');
test('real bilingual collections expose readable chapters, matching icons and resolvable image bytes', async () => {
  const slugs = (await readdir(root, { withFileTypes: true })).filter(entry => entry.isDirectory()).map(entry => entry.name);
  assert.ok(slugs.length > 0);
  let images = 0;
  for (const slug of slugs) {
    const icon = await collectionFile(slug, 'img/icon.webp');
    if (icon) { assert.equal(icon.subarray(0, 4).toString(), 'RIFF'); assert.equal(icon.subarray(8, 12).toString(), 'WEBP'); }
    for (const language of ['en', 'pt-BR'] as const) {
      const entries = await documentationEntries(slug, language);
      assert.ok(entries.some(entry => entry.id === 'README' && entry.href), `${slug}/${language}: README`);
      for (const entry of entries.filter(entry => entry.href && !entry.documentId)) {
        const source = await documentationSource(slug, entry.id, language);
        assert.notEqual(source, null, `${slug}/${language}/${entry.id}`);
        for (const match of source!.matchAll(/!\[[^\]]*\]\(([^\s)]+)\)/g)) {
          const href = match[1];
          if (/^https?:/.test(href)) continue;
          const resolved = resolveDocumentLink(slug, entry.id, language, href, true);
          assert.ok(resolved, `${slug}/${language}/${entry.id}: ${href}`);
          if (resolved.startsWith('/api/shared-assets/')) {
            const parts = resolved.slice('/api/shared-assets/'.length).split('/').map(decodeURIComponent);
            const response = await GET(new Request(`http://reader${resolved}`), { params: Promise.resolve({ path: parts }) });
            assert.equal(response.status, 200, resolved);
            assert.ok((await response.arrayBuffer()).byteLength > 0);
          } else if (resolved.startsWith('/api/document-assets/')) {
            const [, project, ...parts] = resolved.slice('/api/'.length).split('/').map(decodeURIComponent);
            assert.ok((await collectionFile(project, parts.join('/')))?.length, resolved);
          } else if (resolved.startsWith('/assets/')) {
            assert.ok((await readFile(path.join(process.cwd(), 'public', resolved.slice(1)))).length);
          } else assert.fail(`Unexpected image destination: ${resolved}`);
          images++;
        }
      }
    }
  }
  assert.ok(images > 0);
});
