import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { integrateSources } from '../lib/source-references.ts';
import { canonicalSourceKey, referenceContainsLocation, sourceLocation, sourceUnits } from '../lib/source-links.ts';
import { sourceSearchResults } from '../lib/source-search.ts';
import { markdownUnits } from '../lib/markdown.ts';
import { containsLocation, type TableMeasurement } from '../lib/table-pagination.ts';
import { paginateMeasured } from '../lib/book-pagination.ts';
const contents: Record<string, Record<string, string>> = {
  'env-auditor': { 'frontend/config.js': 'const frontend = "needle";\nsecond\nthird', 'backend/config.js': 'const backend = "needle";\nsecond\nthird' },
  'go-image-optimizer': { 'frontend/config.js': 'const optimizer = "needle";\nsecond\nthird' },
};
function fixtureReader(revision = 'v1', tamper = false) {
  const counts = new Map<string, number>();
  return { counts, read: async (project: string, relative: string) => {
    const files: Record<string, unknown> = {}; const snapshots = new Map<string, string>();
    for (const [path, content] of Object.entries(contents[project] ?? {})) {
      const source = revision === 'v2' ? `changed\n${content}` : content;
      const hash = createHash('sha256').update(source).digest('hex');
      files[path] = { status: 'available', sourceKey: canonicalSourceKey(project, path), sha256: hash, snapshot: `snapshots/${hash}.txt`, revision };
      snapshots.set(`links/snapshots/${hash}.txt`, tamper ? 'wrong' : source);
    }
    counts.set(`${project}/${relative}`, (counts.get(`${project}/${relative}`) ?? 0) + 1);
    return relative === 'links/catalog.json' ? Buffer.from(JSON.stringify({ project, files })) : snapshots.has(relative) ? Buffer.from(snapshots.get(relative)!) : null;
  } };
}
const link = (path: string, label = 'Config') => `[${label}](../../${path})`;
test('full path and project produce distinct source identities; same file shares identity across documents and languages', async () => {
  const { read } = fixtureReader();
  const parse = async (project: string, document: string, language: 'en' | 'pt-BR', text: string) => (await integrateSources(project, document, language, markdownUnits(text), read)).flatMap(u => u.references ?? []);
  const [front, back] = await parse('env-auditor', 'guide.md', 'en', `${link('frontend/config.js')}\n\n${link('backend/config.js')}`);
  const [other] = await parse('go-image-optimizer', 'guide.md', 'en', link('frontend/config.js'));
  assert.equal(new Set([front.sourceKey, back.sourceKey, other.sourceKey]).size, 3);
  assert.match(front.lines![0], /frontend/); assert.match(back.lines![0], /backend/); assert.match(other.lines![0], /optimizer/);
  const [translated] = await parse('env-auditor', 'guide.md', 'pt-BR', link('frontend/config.js', 'Configuração'));
  assert.equal(front.sourceKey, translated.sourceKey); assert.equal(front.id, translated.id);
  const [differentDocument] = await parse('env-auditor', 'other.md', 'en', link('frontend/config.js'));
  assert.equal(front.sourceKey, differentDocument.sourceKey); assert.notEqual(front.id, differentDocument.id);
});
test('repeated identical links within one paragraph and multiple units have independent disclosures and one cached authoritative file', async () => {
  const { read, counts } = fixtureReader();
  const units = await integrateSources('env-auditor', 'guide.md', 'en', markdownUnits(`${link('frontend/config.js')} and ${link('frontend/config.js')}\n\n${link('frontend/config.js')}`), read);
  const refs = units.flatMap(u => u.references ?? []);
  assert.equal(refs.length, 3); assert.equal(new Set(refs.map(r => r.id)).size, 3); assert.equal(new Set(refs.map(r => r.sourceKey)).size, 1);
  assert.equal([...counts].filter(([key]) => key.includes('/snapshots/')).length, 1);
  assert.ok([...counts].filter(([key]) => key.includes('/snapshots/')).every(([, count]) => count === 1));
  const flow = sourceUnits(units, new Set([refs[1].id])); assert.equal(flow.filter(u => 'code' in u).length, 1);
  assert.equal(flow.find(u => 'code' in u)!.id, refs[1].id);
});
test('ranges are locations within the same file; search and bookmarks resolve the exact occurrence after repagination', async () => {
  const { read } = fixtureReader();
  const units = await integrateSources('env-auditor', 'guide.md', 'en', markdownUnits(`${link('frontend/config.js')}\n\n${link('backend/config.js')}\n\n${link('frontend/config.js#L2-L3')}`), read);
  const refs = units.flatMap(u => u.references ?? []);
  assert.equal(refs[0].sourceKey, refs[2].sourceKey); assert.deepEqual(refs[2].lines, ['second', 'third']);
  const results = refs.flatMap(ref => sourceSearchResults('env-auditor', 'guide.md', 'en', 'Guide', ref, 'needle'));
  assert.equal(results.length, 2); assert.notEqual(results[0].anchor, results[1].anchor);
  assert.equal(results[0].sourcePath, 'frontend/config.js'); assert.equal(results[1].sourcePath, 'backend/config.js');
  for (const result of results) {
    assert.equal(refs.filter(ref => referenceContainsLocation(ref, result.anchor)).length, 1);
    const flow = sourceUnits(units, new Set([result.occurrence]));
    for (const capacity of [80, 150]) {
      const measured = new Map<number, TableMeasurement>();
      flow.forEach((unit, i) => { if ('code' in unit) measured.set(i, { kind: 'code', rows: [20, 20, 20], header: 25, overhead: 10, widths: [], safe: true }); });
      const pages = paginateMeasured(flow, flow.map(u => 'code' in u ? 95 : 30), capacity, measured);
      const matched = pages.flat().filter(unit => containsLocation(unit, result.anchor));
      assert.equal(matched.length, 1); assert.equal(matched[0].code?.path, result.sourcePath);
    }
  }
});
test('ambiguous basenames, unknown paths, unavailable revisions and corrupt snapshots fail without substitutions', async () => {
  const { read } = fixtureReader();
  for (const href of ['../../config.js', '../../absent/config.js', 'https://github.com/juniocr26/env-auditor/blob/v0/frontend/config.js']) {
    const refs = (await integrateSources('env-auditor', 'guide.md', 'en', markdownUnits(`[x](${href})`), read)).flatMap(u => u.references ?? []);
    assert.equal(refs.length, 1); assert.notEqual(refs[0].status, 'available'); assert.equal(refs[0].lines, undefined);
  }
  const units = markdownUnits(link('frontend/config.js'));
  const corrupt = (await integrateSources('env-auditor', 'guide.md', 'en', units, fixtureReader('v1', true).read))[0].references![0];
  assert.equal(corrupt.status, 'missing'); assert.equal(corrupt.lines, undefined);
});
test('content changes retain file/occurrence identity and invalidate old line bookmarks; pinned revisions never substitute current text', async () => {
  const units = markdownUnits(link('frontend/config.js'));
  const old = (await integrateSources('env-auditor', 'guide.md', 'en', units, fixtureReader('v1').read))[0].references![0];
  const current = (await integrateSources('env-auditor', 'guide.md', 'en', units, fixtureReader('v2').read))[0].references![0];
  assert.equal(old.sourceKey, current.sourceKey); assert.equal(old.id, current.id); assert.notEqual(old.fingerprint, current.fingerprint);
  const bookmark = sourceLocation(old, 2);
  assert.equal(referenceContainsLocation(old, bookmark), true); assert.equal(referenceContainsLocation(current, bookmark), false);
  assert.equal(containsLocation({ id: current.id, code: current }, bookmark), false);
  assert.throws(() => canonicalSourceKey('env-auditor', '../config.js'));
  assert.throws(() => canonicalSourceKey('env-auditor', '/config.js'));
});

test('synchronized project catalogs keep one canonical record per full path without basename collisions', async () => {
  const { collectionFile } = await import('../lib/documentation.ts');
  for (const project of ['engineering-library', 'env-auditor', 'go-image-optimizer', 'payment-reconciliation-lab', 'rust-event-relay', 'url-shortener']) {
    const catalog = JSON.parse((await collectionFile(project, 'links/catalog.json'))!.toString());
    assert.equal(catalog.project, project);
    const keys = new Set<string>();
    for (const [path, value] of Object.entries(catalog.files)) {
      const record = value as { sourceKey: string };
      assert.equal(record.sourceKey, canonicalSourceKey(project, path));
      assert.equal(keys.has(record.sourceKey), false); keys.add(record.sourceKey);
    }
    assert.equal(keys.size, catalog.summary.uniqueFiles);
    for (const occurrence of catalog.occurrences) assert.ok(catalog.files[occurrence.path]);
  }
});
