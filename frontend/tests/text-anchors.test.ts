import test from 'node:test';
import assert from 'node:assert/strict';
import { textAnchor, resolveTextAnchor, toolbarPosition, highlightColors } from '../lib/text-anchors.ts';
test('seven colors and viewport bounds', () => {
  assert.equal(highlightColors.length, 7);
  assert.deepEqual(toolbarPosition({ left: -10, top: 3, bottom: 40 }, 320, 500), { left: 8, top: 48 });
  assert.deepEqual(toolbarPosition({ left: 999, top: 900, bottom: 940 }, 1000, 600), { left: 670, top: 540 });
});
test('anchors verify offsets, quotes and context and fail safely after edits', () => {
  const source = 'Intro: The selected passage. End.';
  const anchor = textAnchor('logical-block', source, 11, 27);
  assert.deepEqual(resolveTextAnchor(anchor, source), [11, 27]);
  assert.equal(resolveTextAnchor(anchor, source.replace('selected', 'different')), null);
  const middle = 'x'.repeat(60) + 'unique' + 'y'.repeat(60);
  const movable = textAnchor('block', middle, 60, 66);
  assert.deepEqual(resolveTextAnchor(movable, 'new introduction' + middle), [76, 82]);
  assert.equal(resolveTextAnchor(movable, 'intro' + middle + middle), null);
});
