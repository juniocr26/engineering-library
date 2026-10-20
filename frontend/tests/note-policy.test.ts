import { test } from 'node:test';
import assert from 'node:assert/strict';
import { noteUrl, noteRenderError, NOTE_MAX_BYTES } from '../lib/note-policy.ts';

test('external images have no provider or file format allowlist', () => {
  for (const url of ['https://unlisted.example/image.svg', 'https://img.shields.io/badge/test-ok-blue', 'https://example.com/animated.gif', '/assets/notes/persistence.svg', '//images.example/file.webp', 'relative.png', 'data:image/avif;base64,AAAA']) assert.equal(noteUrl(url, 'src'), url);
  for (const url of ['javascript:alert(1)', 'JaVaScRiPt:alert(1)', 'java\nscript:alert(1)', 'file:///etc/passwd', 'data:text/html,<script/>']) assert.equal(noteUrl(url, 'src'), '');
  assert.equal(noteUrl('mailto:reader@example.com', 'href'), 'mailto:reader@example.com');
});
test('rich notes no longer have small structural limits', () => {
  for (const source of ['# Unicode ação 📚', 'x'.repeat(131073), '>'.repeat(80) + ' deep', '```mermaid\nA-->B\n```\n'.repeat(20), '| A | B |\n|---|---|\n' + '| x | y |\n'.repeat(1500)]) assert.equal(noteRenderError(source), null);
  assert.ok(noteRenderError('x'.repeat(NOTE_MAX_BYTES + 1)));
  assert.ok(noteRenderError('📚'.repeat(NOTE_MAX_BYTES / 4 + 1)));
});

test('notes use the same global IMG URL as project documentation', () => {
  assert.equal(noteUrl('/img/diagrams/reader-storage.svg', 'src'), '/api/shared-assets/diagrams/reader-storage.svg');
});
