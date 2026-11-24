import test from 'node:test';
import assert from 'node:assert/strict';
import { noteAtSelection } from '../lib/note-location.ts';
const segments = [{ block: 'logical-block', start: 0, end: 5, exact: 'Hello', prefix: '', suffix: '' }];

test('shared notes at identical ranges retain their explicit highlight association', () => {
  const first = { highlight_id: 10, segments, body: 'First distinct body' };
  const second = { highlight_id: 20, segments, body: 'Second distinct body' };
  assert.equal(noteAtSelection([first, second], segments, 20), second);
  assert.equal(noteAtSelection([first, second], segments, 30), undefined);
});

test('only an unambiguous independent note may be reopened by passage', () => {
  const first = { highlight_id: null, segments, body: 'Independent body' };
  const second = { highlight_id: null, segments, body: 'Another distinct body' };
  assert.equal(noteAtSelection([first], segments, 30), first);
  assert.equal(noteAtSelection([first, second], segments, 30), undefined);
  assert.equal(noteAtSelection([first], [{ ...segments[0], block: 'other-block' }]), undefined);
});
