import test from 'node:test';
import assert from 'node:assert/strict';
import { translatedLocation } from '../lib/reading-position.ts';
const pt = [
  { id: 'inicio', readingAnchor: 'section-1/block-0' },
  { id: 'consequencias', readingAnchor: 'section-2/block-0' },
  { id: 'texto', readingAnchor: 'section-2/block-1' },
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
