import test from 'node:test';
import assert from 'node:assert/strict';
import { paginateTables, containsLocation, type TableBookUnit, type TableMeasurement } from '../lib/table-pagination.ts';
import { markdownUnits } from '../lib/markdown.ts';
import { tableFixtures } from './fixtures/tables.ts';
function split(rows: number[], capacities = [180], before = 0, safe = true) {
  const units: TableBookUnit[] = [...(before ? [{ id: 'before' }] : []), { id: 'table' }];
  const measurement: TableMeasurement = { rows, header: 40, overhead: 16, widths: [150, 200], safe };
  return paginateTables(units, [...(before ? [before] : []), 56 + rows.reduce((a, b) => a + b, 0)], new Map([[units.length - 1, measurement]]), page => capacities[page % capacities.length]);
}
function indices(pages: TableBookUnit[][]) {
  return pages.flat().flatMap(unit => unit.tablePart ? Array.from({ length: unit.tablePart.end - unit.tablePart.start }, (_, i) => unit.tablePart!.start + i) : []);
}
for (const fixture of tableFixtures) test(`${fixture.rows} rows / ${fixture.columns} columns preserve content and order at variable capacities`, () => {
  const unit = markdownUnits(fixture.source)[0];
  assert.equal(unit.table?.rows.length, fixture.rows);
  assert.equal(unit.table?.header.split('\n')[0].split('|').length - 2, fixture.columns);
  const heights = Array.from({ length: fixture.rows }, (_, i) => 25 + i % 5 * 11);
  for (const capacities of [[100], [180, 260], [600]]) {
    const pages = split(heights, capacities);
    assert.deepEqual(indices(pages), heights.map((_, i) => i));
    assert.ok(pages.length <= fixture.rows);
    for (const [pageIndex, page] of pages.entries()) for (const part of page) {
      const segment = part.tablePart!;
      const height = 56 + heights.slice(segment.start, segment.end).reduce((a, b) => a + b, 0);
      assert.ok(segment.maxHeight || height <= capacities[pageIndex % capacities.length]);
      assert.ok(containsLocation(part, `table--row-${segment.end - 1}`));
    }
  }
});
test('header and exactly one row; insufficient remaining space; table starts at bottom', () => {
  assert.equal(split([44, 44], [100]).length, 2);
  const pages = split([44, 44], [100], 70);
  assert.deepEqual(pages[0], [{ id: 'before' }]);
  assert.deepEqual(indices(pages), [0, 1]);
});
test('oversized row, oversized header and complex structure terminate with accessible fallback', () => {
  for (const pages of [split([900, 20]), split([20, 20], [30]), split([20, 20], [180], 0, false)]) {
    assert.deepEqual(indices(pages), [0, 1]);
    assert.ok(pages.flat().some(unit => unit.tablePart?.maxHeight));
  }
});
test('row anchors resolve after resize changes segment boundaries', () => {
  for (const capacity of [100, 240, 700]) {
    const pages = split(Array(30).fill(30), [capacity]);
    assert.equal(pages.flat().filter(unit => containsLocation(unit, 'table--row-17')).length, 1);
    assert.equal(pages.flat().filter(unit => containsLocation(unit, 'table')).length, 1);
  }
});
