import test from 'node:test';
import assert from 'node:assert/strict';
import { documentationEntries, documentationSource } from '../lib/documentation.ts';
import { getReadingSequence, readingNeighbors } from '../lib/reading-order.ts';

for (const slug of ['engineering-library', 'env-auditor', 'go-image-optimizer', 'payment-reconciliation-lab', 'rust-event-relay', 'url-shortener']) {
  for (const language of ['en', 'pt-BR'] as const) {
    test(`${slug}/${language}: one direct FAQ with answers in continuous reading order`, async () => {
      const entries = await documentationEntries(slug, language);
      const faq = entries.filter(entry => entry.id.startsWith('faq/') || entry.id === 'category:faq');
      assert.equal(faq.length, 1);
      assert.equal(faq[0].title, 'FAQ');
      assert.equal(faq[0].heading, true);
      assert.match(faq[0].number, /^\d+$/);
      assert.equal(faq[0].href, `/projects/${slug}/docs/faq/index.md?lang=${language}`);
      const source = await documentationSource(slug, faq[0].id, language);
      assert.match(source!, /^# FAQ\n/);
      assert.match(source!, /\*\*(?:Answer|Resposta|Model answer|Resposta modelo):\*\*/);
      const sequence = getReadingSequence(slug, language, entries);
      assert.equal(sequence.filter(entry => entry.id?.startsWith('faq/')).length, 1);
      assert.ok(readingNeighbors(sequence, faq[0].id).previous);
      assert.ok(readingNeighbors(sequence, faq[0].id).next);
      assert.ok(!entries.some(entry => /study-guide|application-and-catalog/.test(entry.id)));
    });
  }
}
