import { test } from 'node:test';
import assert from 'node:assert/strict';
import { pageNumbers } from '../lib/pagination.ts';
import { catalogHref, languageOf, messages } from '../lib/i18n.ts';
test('compact numbered pagination at both boundaries and intermediate pages', () => {
  assert.deepEqual(pageNumbers(1, 1), [1]);
  assert.deepEqual(pageNumbers(1, 2), [1, 2]);
  assert.deepEqual(pageNumbers(1, 101), [1, 2, 3, 'ellipsis', 101]);
  assert.deepEqual(pageNumbers(50, 101), [1, 'ellipsis', 49, 50, 51, 'ellipsis', 101]);
  assert.deepEqual(pageNumbers(101, 101), [1, 'ellipsis', 99, 100, 101]);
  for (let n = 1; n <= 101; n++) {
    const values = pageNumbers(n, 101);
    assert.ok(values.length <= 9);
    assert.ok(values.includes(n));
    assert.equal(values[0], 1);
    assert.equal(values.at(-1), 101);
  }
});
test('language and catalog page persist in navigation', () => {
  assert.equal(languageOf(), 'pt-BR');
  assert.equal(languageOf('invalid'), 'pt-BR');
  assert.equal(languageOf('en'), 'en');
  assert.equal(catalogHref(2, 'en'), '/?lang=en&page=2');
  assert.equal(catalogHref(2, 'pt-BR', 'env-auditor'), '/projects/env-auditor?lang=pt-BR&page=2');
  assert.deepEqual(Object.keys(messages.en), Object.keys(messages['pt-BR']));
});
