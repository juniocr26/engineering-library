import test from 'node:test';
import assert from 'node:assert/strict';
import { bookmarkHref, documentHref, CONTENTS_DOCUMENT } from '../lib/document-links.ts';
import { documentationEntries } from '../lib/documentation.ts';

test('contents bookmarks route to the project with an encoded logical anchor', () => {
  assert.equal(bookmarkHref('engineering-library', CONTENTS_DOCUMENT, 'en', 'category:architecture'), '/projects/engineering-library?lang=en#category%3Aarchitecture');
  assert.equal(bookmarkHref('engineering-library', 'README', 'pt-BR', 'intro'), documentHref('engineering-library', 'README', 'pt-BR', 'intro'));
});

test('canonical contents anchors survive localization', async () => {
  const en = await documentationEntries('engineering-library', 'en');
  const pt = await documentationEntries('engineering-library', 'pt-BR');
  assert.ok(en.length > 0);
  assert.deepEqual(en.map(entry => entry.id), pt.map(entry => entry.id));
});
