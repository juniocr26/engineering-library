import test from 'node:test';
import assert from 'node:assert/strict';
import { sourceTarget, sourceUnits } from '../lib/source-links.ts';
import { paginateMeasured, type BookUnit } from '../lib/book-pagination.ts';
import { containsLocation } from '../lib/table-pagination.ts';
import { markdownUnits } from '../lib/markdown.ts';
import { integrateSources } from '../lib/source-references.ts';
import { documentationEntries, documentationSource } from '../lib/documentation.ts';
import { resolveDocumentLink } from '../lib/document-links.ts';

test('source links preserve project boundaries, line ranges and immutable revisions', () => {
  const resolve = (href: string) => sourceTarget('rust-event-relay', 'env/index.md', 'en', href);
  assert.deepEqual(resolve('../../../../../../../rust-event-relay/backend/src/main.rs#L12-L18'), { path: 'backend/src/main.rs', start: 12, end: 18 });
  assert.equal(resolve('../../../../../../../env-auditor/scripts/audit-envs.py'), null);
  for (const href of ['#code', '../guide.md', 'https://example.com/main.rs', '/etc/passwd', '../../../../../etc/test.rs', '../../../../../rust-event-relay/%2e%2e/other.rs', 'file:///tmp/a.rs']) assert.equal(resolve(href), null);
  assert.deepEqual(resolve('https://github.com/juniocr26/rust-event-relay/blob/abc/backend/src/main.rs#L2'), { path: 'backend/src/main.rs', revision: 'abc', start: 2, end: 2 });
  assert.equal(resolve('https://github.com/other/rust-event-relay/blob/main/main.rs'), null);
  assert.equal(resolve('../../../../../../../rust-event-relay/main.rs#L9-L2'), null);
});
test('shared measured pagination consumes each complete line once and resolves stable locations on resize', () => {
  const code = { id: 'source', path: 'file.rs', href: '', language: 'rust', status: 'available' as const, start: 20, lines: Array.from({ length: 150 }, (_, i) => `line ${i}`) };
  for (const size of [90, 200, 600]) {
    const pages = paginateMeasured<BookUnit>([{ id: 'before' }, { id: 'source', code }], [25, 3040], page => size + page % 2 * 20, new Map([[1, { kind: 'code' as const, rows: Array(150).fill(20), header: 24, overhead: 16, widths: [], safe: true }]]));
    const segments = pages.flat().filter(u => 'codePart' in u);
    assert.deepEqual(segments.flatMap(u => Array.from({ length: u.codePart!.end - u.codePart!.start }, (_, i) => u.codePart!.start + i)), Array.from({ length: 150 }, (_, i) => i));
    assert.equal(pages.flat().filter(u => containsLocation(u, 'source--line-101')).length, 1);
    assert.equal(pages.flat().filter(u => containsLocation(u, 'source')).length, 1);
    if (size >= 90) assert.equal(pages[0].length, 2, 'fill the remaining first-page space');
  }
  assert.equal(sourceUnits([{ id: 'before', references: [code] }], new Set(['source'])).length, 2);
  assert.equal(sourceUnits([{ id: 'before', references: [code] }], new Set()).length, 1);
});
test('ordinary navigation and reference-style links retain their semantics', () => {
  const units = markdownUnits('- [source][code]\n- [docs](../guide.md)\n\n[code]: ../../../../../../../env-auditor/scripts/audit-envs.py');
  assert.equal(units.length, 2);
  assert.deepEqual(units[0].links, ['../../../../../../../env-auditor/scripts/audit-envs.py']);
  assert.equal(resolveDocumentLink('env-auditor', 'env/index.md', 'en', '../../../../../../../env-auditor/docs/en/guide.md#setup'), '/projects/env-auditor/docs/guide.md?lang=en#setup');
  assert.equal(resolveDocumentLink('env-auditor', 'env/index.md', 'en', 'https://github.com/juniocr26/env-auditor/blob/main/docs/en/guide.md'), '/projects/env-auditor/docs/guide.md?lang=en');
});
test('every catalog project, both languages: approved references resolve and documents without code remain unchanged', async () => {
  for (const project of ['engineering-library', 'env-auditor', 'go-image-optimizer', 'payment-reconciliation-lab', 'rust-event-relay', 'url-shortener']) for (const language of ['en', 'pt-BR'] as const) {
    let approved = 0; let plain = 0;
    for (const entry of (await documentationEntries(project, language)).filter(e => e.href)) {
      const source = await documentationSource(project, entry.id, language);
      assert.notEqual(source, null);
      const units = markdownUnits(source!);
      const integrated = await integrateSources(project, entry.id, language, units);
      assert.deepEqual(integrated.map(u => u.source), units.map(u => u.source));
      if (!integrated.some(u => u.references?.length)) plain++;
      for (const ref of integrated.flatMap(u => u.references ?? [])) if (ref.status === 'available') { approved++; assert.ok(ref.lines?.length); assert.match(ref.fingerprint!, /^[a-f0-9]{64}$/); }
    }
    assert.ok(approved > 0, `${project}/${language} approved code`);
    assert.ok(plain > 0, `${project}/${language} plain documents`);
  }
});

test('offline source loader rejects traversal, escaped symlinks, configuration, large/binary files and secret patterns', async () => {
  const { mkdtemp, writeFile, mkdir, symlink, rm } = await import('node:fs/promises');
  const { approvedSource } = await import('../lib/source-snapshot.ts');
  const temp = await mkdtemp('/tmp/source-security-');
  const root = `${temp}/approved`;
  try {
    await mkdir(root); await writeFile(`${root}/safe.py`, 'print("synthetic")\n');
    await writeFile(`${temp}/outside.py`, 'outside'); await symlink(`${temp}/outside.py`, `${root}/escape.py`);
    await writeFile(`${root}/key.py`, '# -----BEGIN PRIVATE KEY-----');
    await writeFile(`${root}/binary.py`, Buffer.from([0, 1, 2]));
    await writeFile(`${root}/large.py`, 'x'.repeat(512001));
    const safe = await approvedSource(root, 'safe.py'); assert.equal(safe.status, 'available');
    if (safe.status === 'available') assert.equal(safe.content.toString(), 'print("synthetic")\n');
    for (const file of ['../outside.py', '/etc/passwd', 'escape.py', '.env', 'config.yml', 'key.py', 'binary.py', 'large.py', 'node_modules/test.py']) assert.equal((await approvedSource(root, file)).status, 'excluded', file);
    assert.equal((await approvedSource(root, 'missing.py')).status, 'missing');
  } finally { await rm(temp, { recursive: true, force: true }); }
});

test('language highlighting preserves whitespace, blank lines, multiline syntax and untrusted HTML', async () => {
  const { highlightedLines } = await import('../lib/syntax-highlight.ts');
  const examples = { rust: 'fn main() {\n    let x = 1;\n}', go: 'package main\nfunc main() {}', python: 'def main():\n    return "hello"', ruby: 'def main\n  puts "hi"\nend', javascript: 'const x = "hi";\n', typescript: 'const x: number = 1;\n' };
  for (const [language, source] of Object.entries(examples)) {
    const rendered = highlightedLines(source, language);
    assert.equal(rendered.length, source.split('\n').length);
    assert.ok(rendered.some(line => line.includes('hljs-')));
    assert.deepEqual(rendered.map(line => line.replace(/<[^>]+>/g, '').replaceAll('&quot;', '"').replaceAll('&#x27;', "'").replaceAll('&lt;', '<').replaceAll('&gt;', '>').replaceAll('&amp;', '&')), source.split('\n'));
  }
  const block = highlightedLines('/* multi\nline */\n<script>no execution</script>', 'javascript');
  for (const line of block) assert.equal((line.match(/<span/g) ?? []).length, (line.match(/<\/span>/g) ?? []).length);
  assert.ok(block[2].includes('&lt;script&gt;'));
});

test('ordinary list units and legacy source-list bookmark identities are preserved', async () => {
  const { createHash } = await import('node:crypto');
  const ordinary = '- [First](one.md)\n- [Second](two.md)';
  assert.equal(markdownUnits(ordinary).length, 1);
  assert.equal(markdownUnits(ordinary)[0].id, `start--${createHash('sha256').update(ordinary).digest('hex').slice(0, 16)}`);
  const sources = '- [First](first.py)\n- [Second](second.py)';
  assert.equal(markdownUnits(sources).length, 2);
  assert.equal(markdownUnits(sources)[0].id, `start--${createHash('sha256').update(sources).digest('hex').slice(0, 16)}`);
});
