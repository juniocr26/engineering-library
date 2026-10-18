import test from 'node:test';
import assert from 'node:assert/strict';
import { documentHref, resolveDocumentLink } from '../lib/document-links.ts';
import { markdownUnits } from '../lib/markdown.ts';

test('reader URLs distinguish relative documents, languages, anchors, assets and external sources', () => {
  const resolve = (href: string) => resolveDocumentLink('env-auditor', 'architecture/overview.md', 'en', href);
  assert.equal(resolve('../testing/verification.md#evidence'), '/projects/env-auditor/docs/testing/verification.md?lang=en#evidence');
  assert.equal(resolve('../../pt-BR/architecture/overview.md'), '/projects/env-auditor/docs/architecture/overview.md?lang=pt-BR');
  assert.equal(resolve('../../../README.md'), '/projects/env-auditor/docs/README?lang=en');
  assert.equal(resolve('#decisions'), '#decisions');
  assert.equal(resolve('https://example.com/docs.md'), 'https://example.com/docs.md');
  assert.equal(resolve('javascript:alert(1)'), undefined);
  assert.equal(resolve('../../../../../../etc/passwd'), undefined);
  assert.equal(resolveDocumentLink('env-auditor', 'architecture/overview.md', 'en', '../assets/flow.svg', true), '/api/document-assets/env-auditor/docs/en/assets/flow.svg');
  assert.equal(documentHref('engineering-library', 'README', 'pt-BR', 'a b'), '/projects/engineering-library/docs/README?lang=pt-BR#a%20b');
});

test('semantic Markdown units retain code, tables and references without executing raw HTML', () => {
  const source = '# Title\n\nParagraph [reference][ref].\n\n## Same\n\n```js\nconsole.log(1);\n```\n\n|a|b|\n|-|-|\n|1|2|\n\n## Same\n\n<script>alert(1)</script>\n\n[ref]: other.md';
  const units = markdownUnits(source);
  assert.deepEqual(units.filter(unit => unit.heading !== undefined).map(unit => unit.id), ['title', 'same', 'same-1']);
  assert.ok(units.some(unit => unit.source.includes('```js')));
  assert.ok(units.some(unit => unit.source.startsWith('|a|b|')));
  assert.ok(units.some(unit => unit.source.includes('[ref]: other.md')));
  assert.ok(!units.some(unit => unit.source.startsWith('<script>')));
  const before = markdownUnits('# Title\n\nUnchanged paragraph.')[1].id;
  const after = markdownUnits('# Title\n\nInserted paragraph.\n\nUnchanged paragraph.')[2].id;
  assert.equal(before, after);
});
