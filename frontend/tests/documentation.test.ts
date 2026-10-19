import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, rm, symlink } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { getReadingSequence, getNextDocument } from '../lib/reading-order.ts';
test('canonical bilingual discovery, README, substantive indexes and missing translations', async () => {
  const root = await mkdtemp(path.join(tmpdir(), 'el-docs-'));
  const previous = process.env.DOCUMENTATION_ROOT;
  process.env.DOCUMENTATION_ROOT = root;
  try {
    for (const lang of ['en', 'pt-BR']) {
      const dir = path.join(root, 'sample', 'docs', lang, 'architecture');
      await mkdir(dir, { recursive: true });
      await writeFile(path.join(dir, 'index.md'), '# Architecture\n\n- [Overview](overview.md)\n');
      await writeFile(path.join(dir, 'overview.md'), lang === 'en' ? '# Overview' : '# Visão geral');
    }
    await writeFile(path.join(root, 'sample', 'README.md'), '# README');
    await writeFile(path.join(root, 'sample', 'README.pt-BR.md'), '# LEIA-ME');
    for (const lang of ['en', 'pt-BR']) {
      const dir = path.join(root, 'sample', 'docs', lang);
      await writeFile(path.join(dir, 'index.md'), '# Legacy contents\n\nCatalog introduction.');
      await mkdir(path.join(dir, 'faq'));
      await writeFile(path.join(dir, 'faq/index.md'), '# Technical FAQ\n\n### Q001 — Question\n\nAnswer.');
      await writeFile(path.join(dir, 'faq/study-guide.md'), '# Retained study guide\n\nAnswer.');
    }
    await writeFile(path.join(root, 'sample', 'docs/en/architecture/alpha.md'), '# Only English');
    await mkdir(path.join(root, 'sample', 'docs/en/env'));
    await writeFile(path.join(root, 'sample', 'docs/en/env/index.md'), '# ENV\n\n## Runtime\nRequired configuration.');
    const { documentationEntries, documentationSource } = await import('../lib/documentation.ts');
    const en = await documentationEntries('sample', 'en');
    const pt = await documentationEntries('sample', 'pt-BR');
    assert.deepEqual(en.filter(e => !e.documentId).map(e => [e.id, e.number]), pt.filter(e => !e.documentId).map(e => [e.id, e.number]));
    assert.equal(en.filter(e => e.id === 'README').length, 1);
    assert.ok(en.findIndex(e => e.id === 'category:architecture') < en.findIndex(e => e.id === 'README'));
    assert.equal(en.at(-1)?.id, 'README');
    assert.ok(!en.some(e => e.id === 'architecture/index.md'));
    assert.ok(en.some(e => e.id === 'env/index.md'));
    assert.ok(!en.some(e => e.id === 'index.md'));
    assert.deepEqual(en.filter(e => e.id === 'faq/index.md'), [{
      id: 'faq/index.md', number: '3', heading: true, title: 'FAQ',
      href: '/projects/sample/docs/faq/index.md?lang=en', depth: 0,
    }]);
    assert.deepEqual(en.filter(e => !e.documentId).map(e => e.number), ['1', '1.1', '1.2', '2', '2.1', '3', '4']);
    assert.ok(await documentationSource('sample', 'faq/study-guide.md', 'en'));
    assert.equal(pt.find(e => e.id === 'architecture/alpha.md')?.href, undefined);
    const englishSequence = getReadingSequence('sample', 'en', en);
    const portugueseSequence = getReadingSequence('sample', 'pt-BR', pt);
    assert.deepEqual(portugueseSequence.map(entry => entry.id), englishSequence.filter(entry => entry.id === null || pt.some(localized => localized.id === entry.id && localized.href)).map(entry => entry.id));
    assert.ok(!englishSequence.some(entry => entry.id === 'architecture/index.md'));
    assert.ok(englishSequence.some(entry => entry.id === 'env/index.md'));
    assert.equal(getNextDocument(englishSequence, 'architecture/overview.md')?.id, 'env/index.md');
    assert.equal(pt.find(e => e.id === 'architecture/overview.md')?.title, 'Visão geral');
    assert.equal(en.find(e => e.id === 'architecture/overview.md')?.href, '/projects/sample/docs/architecture/overview.md?lang=en');
    assert.equal(await documentationSource('sample', 'architecture/overview.md', 'en'), '# Overview');
    assert.equal(await documentationSource('sample', '../../README.md', 'en'), null);
    assert.equal(await documentationSource('sample', '/etc/passwd.md', 'en'), null);
    assert.equal(await documentationSource('sample', 'architecture/missing.md', 'en'), null);
    await symlink('/etc/passwd', path.join(root, 'sample/docs/en/architecture/escape.md'));
    assert.equal(await documentationSource('sample', 'architecture/escape.md', 'en'), null);
    assert.deepEqual(await documentationEntries('../sample', 'en'), []);
  } finally { if (previous === undefined) delete process.env.DOCUMENTATION_ROOT; else process.env.DOCUMENTATION_ROOT = previous; await rm(root, { recursive: true, force: true }); }
});
