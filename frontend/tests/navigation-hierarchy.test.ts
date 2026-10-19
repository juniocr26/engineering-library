import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

test('all six heading levels, 120 FAQ questions, explicit bilingual IDs and document-only reading order', async () => {
  const root = await mkdtemp(path.join(tmpdir(), 'navigation-tree-'));
  process.env.DOCUMENTATION_ROOT = root;
  try {
    for (const language of ['en', 'pt-BR']) {
      const directory = path.join(root, 'sample/docs', language, 'faq');
      await mkdir(directory, { recursive: true });
      await writeFile(path.join(directory, 'index.md'), `# FAQ\n\n<!-- reading-section:basics -->\n## ${language === 'en' ? 'Basics' : 'Fundamentos'}\n\n` + Array.from({ length: 120 }, (_, i) => `### Q${String(i + 1).padStart(3, '0')} — ${language} question\nAnswer\n`).join('\n') + '\n#### Detail\n##### Deeper\n###### Deepest\n\n```md\n## Not a heading\n```\n');
    }
    const { documentationEntries } = await import('../lib/documentation.ts');
    const { getReadingSequence } = await import('../lib/reading-order.ts');
    const en = await documentationEntries('sample', 'en');
    const pt = await documentationEntries('sample', 'pt-BR');
    const question = (n: number) => en.find(e => e.id === `faq/index.md#question:Q${String(n).padStart(3,'0')}`)!;
    assert.equal(question(9).number, '1.1.9');
    assert.equal(question(10).number, '1.1.10');
    assert.equal(question(99).number, '1.1.99');
    assert.equal(question(100).number, '1.1.100');
    assert.equal(question(120).number, '1.1.120');
    assert.equal(en.at(-1)?.number, '1.1.120.1.1.1');
    assert.equal(en.at(-1)?.depth, 5);
    assert.ok(!en.some(e => e.title === 'Not a heading'));
    assert.equal(new Set(en.map(e => e.id)).size, en.length);
    for (const node of en.filter(e => e.id.includes('#question:') || e.id.includes('#section:'))) {
      const translated = pt.find(e => e.id === node.id);
      assert.ok(translated?.href);
      assert.equal(translated.number, node.number);
    }
    assert.deepEqual(getReadingSequence('sample','en',en).map(e => e.id), [null, 'faq/index.md']);
  } finally { delete process.env.DOCUMENTATION_ROOT; await rm(root, { recursive: true, force: true }); }
});
