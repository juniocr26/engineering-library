import { createHash } from 'node:crypto';
import { collectionFile } from './documentation.ts';
import { canonicalSourceKey, sourceTarget, sourceLanguages, type SourceReference } from './source-links.ts';
import type { MarkdownUnit } from './markdown.ts';
import type { Language } from './i18n.ts';
type Catalog = { project?: string; files: Record<string, { status: SourceReference['status']; sha256?: string; snapshot?: string; revision?: string }> };
export async function integrateSources(project: string, document: string, language: Language, units: MarkdownUnit[], read: typeof collectionFile = collectionFile): Promise<MarkdownUnit[]> {
  let catalog: Catalog = { files: {} };
  try { catalog = JSON.parse((await read(project, 'links/catalog.json'))?.toString('utf8') ?? '{}'); } catch { /* Missing metadata denies source inclusion. */ }
  const cache = new Map<string, Promise<string[] | undefined>>();
  const occurrences = new Map<string, number>();
  const identities = units.map(unit => (unit.links ?? []).map(href => {
    const target = sourceTarget(project, document, language, href);
    if (!target) return null;
    const sourceKey = canonicalSourceKey(project, target.path, target.revision);
    const key = JSON.stringify([project, document, sourceKey, target.start ?? null, target.end ?? null]);
    const ordinal = occurrences.get(key) ?? 0; occurrences.set(key, ordinal + 1);
    return { sourceKey, id: `source-${createHash('sha256').update(`${key}/${ordinal}`).digest('hex').slice(0, 32)}` };
  }));
  return Promise.all(units.map(async (unit, unitIndex) => {
    const references: SourceReference[] = [];
    for (const [linkIndex, href] of (unit.links ?? []).entries()) {
      const target = sourceTarget(project, document, language, href);
      if (!target) continue;
      const { sourceKey, id } = identities[unitIndex][linkIndex]!;
      const record = catalog.project === project ? catalog.files?.[target.path] : undefined;
      let status: SourceReference['status'] = record?.status ?? 'unapproved';
      if (status === 'available' && record && target.revision && target.revision !== record.revision && target.revision !== record.sha256) status = 'revision-mismatch';
      let lines: string[] | undefined;
      if (status === 'available' && record) {
        const cacheKey = JSON.stringify([sourceKey, record.sha256]);
        if (!cache.has(cacheKey)) cache.set(cacheKey, (async () => {
          const content = record.snapshot?.match(/^snapshots\/[a-f0-9]{64}\.txt$/) ? await read(project, `links/${record.snapshot}`) : null;
          return content && content.length <= 512_000 && createHash('sha256').update(content).digest('hex') === record.sha256 ? content.toString('utf8').split('\n') : undefined;
        })());
        const all = await cache.get(cacheKey);
        if (!all || (target.end && target.end > all.length)) status = 'missing';
        else lines = target.start ? all.slice(target.start - 1, target.end) : all;
      }
      references.push({ ...target, project, sourceKey, id, href, status, language: sourceLanguages[target.path.split('.').pop()!.toLowerCase()], ...(lines ? { lines, fingerprint: record?.sha256 } : {}) });
    }
    return { ...unit, references };
  }));
}