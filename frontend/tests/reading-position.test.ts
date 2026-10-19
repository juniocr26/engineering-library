import test from 'node:test';
import assert from 'node:assert/strict';
import { translatedLocation } from '../lib/reading-position.ts';
const pt = [
  { id: 'inicio', readingSection: 'section:introduction', readingAnchor: 'intro-heading' },
  { id: 'consequencias', readingSection: 'section:consequences', readingAnchor: 'consequences-heading' },
  { id: 'texto', readingSection: 'section:consequences', readingAnchor: 'verified-block' },
];
const en = pt.map((unit, i) => ({ ...unit, id: ['start', 'consequences', 'text'][i] }));
test('translations preserve first, section and last blocks in both directions', () => {
  for (let i = 0; i < pt.length; i++) {
    assert.equal(translatedLocation(pt, en, pt[i].id), en[i].id);
    assert.equal(translatedLocation(en, pt, en[i].id), pt[i].id);
  }
});
test('missing blocks use nearest section, missing sections use relative progress', () => {
  assert.equal(translatedLocation(pt, en.slice(0, 2), 'texto'), 'consequences');
  assert.equal(translatedLocation(pt, [{ id: 'a' }, { id: 'b' }], 'texto'), 'b');
});
test('canonical contents and source anchors survive unchanged', () => {
  assert.equal(translatedLocation([{ id: 'adr/example.md' }], [{ id: 'adr/example.md' }], 'adr/example.md'), 'adr/example.md');
  assert.equal(translatedLocation(pt, [], 'texto'), undefined);
});
test('table row offsets translate without changing bookmark identities', () => {
  assert.equal(translatedLocation(pt, en, 'texto--row-4'), 'text--row-4');
  assert.deepEqual(pt.map(unit => unit.id), ['inicio', 'consequencias', 'texto']);
});

test('canonical Q005 survives extra translated headings, long answers and unequal page counts', async () => {
  const { markdownUnits } = await import('../lib/markdown.ts');
  const { readFileSync } = await import('node:fs');
  const { paginateMeasured } = await import('../lib/book-pagination.ts');
  const pt = markdownUnits(readFileSync(new URL('../../docs/projects/go-image-optimizer/docs/pt-BR/faq/index.md', import.meta.url), 'utf8'));
  const en = markdownUnits(readFileSync(new URL('../../docs/projects/go-image-optimizer/docs/en/faq/index.md', import.meta.url), 'utf8'));
  for (const [from, to] of [[pt, en], [en, pt]]) {
    const heading = to.find(unit => unit.readingSection === 'question:Q005')!;
    assert.ok(heading.text.startsWith('Q005'));
    for (const unit of from.filter(unit => unit.readingSection === 'question:Q005')) {
      const target = translatedLocation(from, to, unit.id);
      assert.equal(to.find(unit => unit.id === target)?.readingSection, 'question:Q005');
      for (const capacity of [120, 240]) {
        const pages = paginateMeasured(to, to.map(() => 100), capacity);
        const index = pages.findIndex(page => page.some(unit => unit.id === target));
        assert.ok(index >= 0);
        for (const count of [1, 2]) {
          const start = index - index % count;
          assert.ok(pages.slice(start, start + count).flat().some(unit => unit.id === target));
        }
      }
    }
    const lastQuestion = from.filter(unit => unit.readingSection === 'question:Q007').at(-1)!;
    assert.equal(to.find(unit => unit.id === translatedLocation(from, to, lastQuestion.id))?.readingSection, 'question:Q007');
  }
});

test('missing and duplicate question IDs report ambiguity instead of guessing another question', async () => {
  const { markdownUnits } = await import('../lib/markdown.ts');
  const { resolveTranslatedLocation } = await import('../lib/reading-position.ts');
  const from = markdownUnits('# FAQ\n\n## Q005 — Pergunta\n\nResposta');
  for (const source of ['# FAQ\n\n## Q006 — Other', '# FAQ\n\n## Q005 — One\n\n## Q005 — Two']) {
    const result = resolveTranslatedLocation(from, markdownUnits(source), from[1].id);
    assert.ok(result.limitation);
    assert.equal(result.anchor, 'faq');
  }
});

test('unverified paragraph ordinals fall back to same question; identical content preserves exact block', async () => {
  const { markdownUnits } = await import('../lib/markdown.ts');
  const from = markdownUnits('# FAQ\n\n## Q005 — Pergunta\n\nPrimeiro\n\n```js\nconst x = 1;\n```\n\nÚltimo');
  const to = markdownUnits('# FAQ\n\n## Q005 — Question\n\nExtra\n\nFirst\n\n```js\nconst x = 1;\n```\n\nLast');
  assert.equal(translatedLocation(from, to, from.at(-1)!.id), to[1].id);
  assert.equal(translatedLocation(from, to, from[3].id), to[4].id);
  const back = translatedLocation(to, from, translatedLocation(from, to, from.at(-1)!.id));
  assert.equal(back, from[1].id);
});

test('ordinary translated headings are not assumed equivalent by ordinal', async () => {
  const { markdownUnits } = await import('../lib/markdown.ts');
  const { resolveTranslatedLocation } = await import('../lib/reading-position.ts');
  const from = markdownUnits('# Visão\n\nTexto\n\n## Fim\n\nFinal');
  const to = markdownUnits('# Overview\n\nText\n\n## End\n\nFinal text');
  assert.equal(resolveTranslatedLocation(from, to, from[2].id).limitation, 'document-progress');
});

test('invisible canonical metadata maps ordinary translated sections without changing rendered headings', async () => {
  const { markdownUnits } = await import('../lib/markdown.ts');
  const from = markdownUnits('<!-- reading-section: architecture -->\n\n## Arquitetura\n\nTexto');
  const to = markdownUnits('# Introduction\n\n<!-- reading-section: architecture -->\n\n## Architecture\n\nText');
  assert.equal(from[0].id, 'arquitetura');
  assert.equal(from[1].readingSection, 'section:architecture');
  assert.equal(translatedLocation(from, to, from[1].id), 'architecture');
});

test('missing sections use the nearest verified canonical parent', async () => {
  const { markdownUnits } = await import('../lib/markdown.ts');
  const { resolveTranslatedLocation } = await import('../lib/reading-position.ts');
  const from = markdownUnits('<!-- reading-section: guide -->\n\n# Guia\n\n## Q005 — Pergunta\n\nResposta');
  const to = markdownUnits('<!-- reading-section: guide -->\n\n# Guide\n\n## Q006 — Different');
  assert.deepEqual(resolveTranslatedLocation(from, to, from.at(-1)!.id), { anchor: 'guide', limitation: 'missing-section' });
  const duplicateSource = markdownUnits('# FAQ\n\n## Q005 — A\n\n## Q005 — B');
  assert.equal(resolveTranslatedLocation(duplicateSource, to, duplicateSource.at(-1)!.id).limitation, 'ambiguous-section');
});
