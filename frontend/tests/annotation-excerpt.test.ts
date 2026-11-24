import assert from 'node:assert/strict';
import { test } from 'node:test';
import { noteExcerpt } from '../lib/annotation-excerpt.ts';

test('note excerpts use readable Markdown and an exact 100 grapheme threshold', () => {
  assert.deepEqual(noteExcerpt(`**${'a'.repeat(100)}**`), { text: 'a'.repeat(100), truncated: false });
  assert.deepEqual(noteExcerpt(`**${'a'.repeat(101)}**`), { text: `${'a'.repeat(100)}…`, truncated: true });
  assert.deepEqual(noteExcerpt('# Title\n\n[Read me](https://example.com) and ![diagram](image.svg)'), { text: 'Title Read me and diagram', truncated: false });
});
test('Unicode emoji sequences and combining marks are never split', () => {
  for (const grapheme of ['👩🏽‍💻', 'e\u0301', '🇧🇷', '👨‍👩‍👧‍👦']) {
    assert.deepEqual(noteExcerpt(grapheme.repeat(101)), { text: grapheme.repeat(100) + '…', truncated: true });
  }
});
test('raw HTML is inert readable text, entities decode, definitions are omitted', () => {
  assert.deepEqual(noteExcerpt('<div>Olá &amp; &#128218;</div>'), { text: 'Olá & 📚', truncated: false });
  assert.equal(noteExcerpt('[Read][ref]\n\n[ref]: https://example.com').text, 'Read');
  assert.equal(noteExcerpt('<script>alert("private")</script>\n\nSafe').text, 'Safe');
});
