import { test } from 'node:test';
import assert from 'node:assert/strict';
import { noteUrl, noteRenderError, diagramAllowed, noteTreeLimits } from '../lib/note-policy.ts';

test('note links and assets use an explicit allowlist', () => {
  for (const url of ['javascript:alert(1)', 'JaVaScRiPt:alert(1)', 'data:image/svg+xml,<svg/>', 'file:///etc/passwd', '//tracker.example/x', '/api/document-assets/private.svg', '/assets/notes/../evil.svg', 'http://127.0.0.1/x']) assert.equal(noteUrl(url, 'src'), '');
  for (const url of ['javascript:alert(1)', 'vbscript:evil', 'data:text/html,x', 'file:///etc/passwd', '//evil.example', '/projects/../api']) assert.equal(noteUrl(url, 'href'), '');
  assert.equal(noteUrl('/assets/notes/persistence.svg', 'src'), '/assets/notes/persistence.svg');
  assert.equal(noteUrl('https://www.postgresql.org/docs/', 'href'), 'https://www.postgresql.org/docs/');
});
test('Mermaid cannot weaken configuration or navigate', () => {
  assert.ok(diagramAllowed('flowchart LR\n A --> B'));
  for (const value of ['%%{init:{"securityLevel":"loose"}}%%\nflowchart LR\n A-->B', '---\nconfig: {}\n---\nflowchart LR\n A-->B', 'flowchart LR\n click A "https://evil.example"', 'flowchart LR\n A[<img onerror=evil>]', 'flowchart LR\n A["url(http://127.0.0.1)"]', 'a'.repeat(12001)]) assert.equal(diagramAllowed(value), false);
});
test('resource limits preserve source and refuse pathological previews', () => {
  assert.equal(noteRenderError('# Unicode ação 📚\n\nplain'), null);
  assert.ok(noteRenderError('x'.repeat(131073)));
  assert.ok(noteRenderError('>'.repeat(33) + ' deep'));
  assert.ok(noteRenderError('```mermaid\nA-->B\n```\n'.repeat(9)));
  const deep: { type: string; children?: unknown[] } = { type: 'root' }; let current = deep;
  for (let i = 0; i < 40; i++) { const child = { type: 'blockquote' }; current.children = [child]; current = child; }
  assert.throws(() => noteTreeLimits()(deep));
});
