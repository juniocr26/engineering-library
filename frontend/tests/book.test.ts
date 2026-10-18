import test from 'node:test';
import assert from 'node:assert/strict';
import { manuscriptMarks, contentPageId } from '../lib/manuscript.ts';
import { paginateMeasured } from '../lib/book-pagination.ts';
test('decorations survive rerenders, language changes and folio renumbering', () => {
  const identity = contentPageId(['architecture/overview.md', 'architecture/api.md']);
  assert.deepEqual(manuscriptMarks('project', identity, 'reading'), manuscriptMarks('project', identity, 'reading'));
  assert.notDeepEqual(manuscriptMarks('project', identity, 'reading'), manuscriptMarks('project', contentPageId(['README']), 'reading'));
  assert.notDeepEqual(manuscriptMarks('project', identity, 'reading'), manuscriptMarks('other-project', identity, 'reading'));
});
test('measured heights keep heading with first child and reflow without renumbering', () => {
  const units = [{ id: 'intro' }, { id: 'chapter', keepWithNext: true }, { id: '1.1' }, { id: '1.2' }];
  assert.deepEqual(paginateMeasured(units, [40, 30, 40, 30], 100).map(p => p.map(u => u.id)), [['intro'], ['chapter', '1.1', '1.2']]);
  assert.deepEqual(paginateMeasured(units, [40, 30, 40, 30], 200).flat(), units);
});
test('oversized units remain accessible, empty content and unavailable measurement are safe', () => {
  const units = [{ id: 'long' }, { id: 'next' }];
  assert.deepEqual(paginateMeasured(units, [800, 20], 100), [[units[0]], [units[1]]]);
  assert.deepEqual(paginateMeasured([], [], 100), [[]]);
  assert.deepEqual(paginateMeasured(units, [], 0), [units]);
});
