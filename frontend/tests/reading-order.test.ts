import test from 'node:test';
import assert from 'node:assert/strict';
import { getReadingSequence, getFirstDocument, getLastDocument, readingNeighbors } from '../lib/reading-order.ts';

for (const language of ['en', 'pt-BR']) {
  const contents = `/projects/example?lang=${language}`;
  const entries = [
    { id: 'category:guides', title: 'Guides', number: '1', heading: true },
    { id: 'guides/a.md', title: language === 'en' ? 'Zulu' : 'Alfa', number: '1.1', href: `/projects/example/docs/guides/a.md?lang=${language}` },
    { id: 'guides/missing.md', title: 'Unavailable', number: '1.2' },
    { id: 'guides/b.md', title: language === 'en' ? 'Alfa' : 'Zulu', number: '1.3', href: `/projects/example/docs/guides/b.md?lang=${language}` },
    { id: 'README', title: 'Project', number: '2', href: `/projects/example/docs/README?lang=${language}` },
  ];
  const sequence = getReadingSequence('example', language as 'en' | 'pt-BR', entries);
  test(`${language}: canonical TOC order, available documents and both boundaries`, () => {
    assert.equal(readingNeighbors(sequence, null).next, entries[1].href);
    assert.deepEqual(readingNeighbors(sequence, entries[1].id), { previous: `${contents}&edge=end`, next: entries[3].href, previousIsContents: true });
    assert.deepEqual(readingNeighbors(sequence, entries[3].id), { previous: `${entries[1].href}&edge=end`, next: entries[4].href, previousIsContents: false });
    assert.deepEqual(readingNeighbors(sequence, 'README'), { previous: `${entries[3].href}&edge=end`, next: undefined, previousIsContents: false });
    assert.equal(readingNeighbors(sequence, 'missing.md').next, undefined);
    assert.equal(getFirstDocument(sequence)?.id, entries[1].id);
    assert.equal(getLastDocument(sequence)?.id, 'README');
    assert.equal(sequence[0].id, null);
  });
  test(`${language}: empty and single-document books`, () => {
    assert.equal(readingNeighbors(getReadingSequence('example', language as 'en' | 'pt-BR', []), null).next, undefined);
    assert.deepEqual(readingNeighbors(getReadingSequence('example', language as 'en' | 'pt-BR', [entries[1]]), entries[1].id), { previous: `${contents}&edge=end`, next: undefined, previousIsContents: true });
  });
}
