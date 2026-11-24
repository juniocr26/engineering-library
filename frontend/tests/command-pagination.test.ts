import test from 'node:test';
import assert from 'node:assert/strict';
import { markdownUnits } from '../lib/markdown.ts';
import { paginateMeasured } from '../lib/book-pagination.ts';
import { containsLocation } from '../lib/table-pagination.ts';

test('command continuations retain complete source, indentation and special characters', () => {
  const text = 'docker compose exec -T frontend env PLAYWRIGHT_BROWSERS_PATH=/tmp/browsers node tests/browser.cjs\n  echo "$HOME & <value>"\n\n  done';
  const [unit] = markdownUnits('```sh\n' + text + '\n```');
  assert.equal(unit.command?.value, text);
  const pages = paginateMeasured([unit], [140], 90, new Map([[0, { kind: 'code', rows: [20, 20, 20, 20], header: 0, overhead: 60, widths: [], safe: true }]]));
  assert.equal(pages.length, 4);
  assert.deepEqual(pages.flat().map(p => p.codePart?.start), [0, 1, 2, 3]);
  for (const [i, page] of pages.entries()) {
    assert.equal(page[0].command?.value, text);
    assert.ok(containsLocation(page[0], i ? `${unit.id}--line-${i}` : unit.id));
  }
});
