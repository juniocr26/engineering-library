import test from 'node:test';
import assert from 'node:assert/strict';
import { paginateMeasured, samePagination } from '../lib/book-pagination.ts';

test('equivalent measured partitions preserve layout, while changed source and boundaries invalidate it', () => {
  const units = [{ id: 'a', source: 'Original' }, { id: 'b', source: 'Second' }];
  const previous = paginateMeasured(units, [40, 40], 100);
  assert.ok(samePagination(previous, paginateMeasured(units, [42, 42], 100)));
  assert.equal(samePagination(previous, paginateMeasured(units, [60, 60], 100)), false);
  assert.equal(samePagination(previous, [[{ ...units[0], source: 'Edited' }, units[1]]]), false);
  assert.equal(samePagination(previous, [[units[1], units[0]]]), false);
});

test('equal table fragments compare row ranges and widths instead of fresh object identity', () => {
  const units = [{ id: 'table' }];
  const tables = new Map([[0, { rows: [30, 30, 30], header: 10, overhead: 5, widths: [150, 200], safe: true }]]);
  const previous = paginateMeasured(units, [105], 80, tables);
  const next = paginateMeasured(units, [105], 80, tables);
  assert.notEqual(previous[0][0], next[0][0]);
  assert.ok(samePagination(previous, next));
  const resized = new Map([[0, { ...tables.get(0)!, widths: [151, 200] }]]);
  assert.equal(samePagination(previous, paginateMeasured(units, [105], 80, resized)), false);
  assert.equal(samePagination(previous, paginateMeasured(units, [105], 50, tables)), false);
});

test('code continuation ranges and oversized fragment limits remain meaningful', () => {
  const unit = { id: 'source--line-1', codeOrigin: 'source', codePart: { start: 0, end: 10, maxHeight: 120 } };
  assert.ok(samePagination([[unit]], [[{ ...unit, codePart: { ...unit.codePart } }]]));
  assert.equal(samePagination([[unit]], [[{ ...unit, codePart: { ...unit.codePart, end: 9 } }]]), false);
  assert.equal(samePagination([[unit]], [[{ ...unit, codePart: { ...unit.codePart, maxHeight: 100 } }]]), false);
});
