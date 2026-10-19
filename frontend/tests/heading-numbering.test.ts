import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import type { Root } from 'hast';
import { headingTitle, numberedHeading, numberHeadingUnits } from '../lib/heading-numbering.ts';

 test('structural edits update canonical TOC, panel and rendered AST while preserving anchors', async () => {
  const root = await mkdtemp(path.join(tmpdir(), 'heading-numbering-'));
  process.env.DOCUMENTATION_ROOT = root;
  try {
    const { documentationEntries } = await import('../lib/documentation.ts');
    const { markdownUnits } = await import('../lib/markdown.ts');
    for (const inserted of [false, true]) for (const language of ['en', 'pt-BR'] as const) {
      const directory = path.join(root, 'sample/docs', language, 'architecture');
      await mkdir(directory, { recursive: true });
      const source = `# Architecture\n\n${inserted ? '## Earlier\n\n' : ''}<!-- reading-section:flow -->\n## Q005 — ADR 001 v2 2026\n\n` + Array.from({length: 12}, (_, i) => `### Detail ${i}\n`).join('\n');
      await writeFile(path.join(directory, 'overview.md'), source);
      const entries = await documentationEntries('sample', language);
      const units = numberHeadingUnits(markdownUnits(source), entries, 'architecture/overview.md');
      for (const unit of units.filter(u => u.heading !== undefined)) {
        const entry = entries.find(e => e.id === unit.navigationId)!;
        assert.ok(entry);
        assert.equal(unit.navigationNumber, entry.number);
        const tree: Root = { type: 'root', children: [{type: 'element', tagName: `h${unit.headingDepth}`, properties: {}, children: [{type: 'text', value: unit.text}]}] };
        numberedHeading(unit.navigationNumber)()(tree);
        const element = tree.children[0];
        assert.equal(element.type, 'element');
        if (element.type !== 'element') throw new Error('missing heading');
        const rendered = element.children.map(n => n.type === 'text' ? n.value : '').join('');
        assert.equal(rendered, `${entry.number} ${headingTitle(entry.title, entry.number)}`);
        if (entry.anchor) assert.equal(new URL(entry.href!, 'http://reader').hash, `#${encodeURIComponent(unit.id)}`);
      }
      const question = units.find(u => u.text.startsWith('Q005'))!;
      assert.equal(question.navigationNumber, inserted ? '1.1.2' : '1.1.1');
      assert.equal(question.id, 'q005--adr-001-v2-2026');
      assert.ok(units.some(u => u.navigationNumber?.endsWith('.10')));
    }
  } finally { delete process.env.DOCUMENTATION_ROOT; await rm(root, {recursive: true, force: true}); }
});

test('only exact structural prefixes are deduplicated', () => {
  for (const title of ['ADR 001', 'Q005', '2026-10-19', 'v1.2', '2.3 Other']) assert.equal(headingTitle(title, '1.2'), title);
  assert.equal(headingTitle('1.2 Existing', '1.2'), 'Existing');
  const tree: Root = {type: 'root', children: [{type: 'element', tagName: 'h2', properties: {}, children: [{type: 'text', value: '1.2 '}, {type: 'element', tagName: 'em', properties: {}, children: [{type: 'text', value: 'Existing'}]}]}]};
  numberedHeading('1.2')()(tree);
  assert.equal(JSON.stringify(tree).match(/1\.2 /g)?.length, 1);
});
