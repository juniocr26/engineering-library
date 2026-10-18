import { readdir, readFile, realpath } from 'node:fs/promises';
import path from 'node:path';
import { categoryLabels, type Language } from './i18n.ts';
export type TocEntry = { id: string; number: string; title: string; href?: string; heading?: boolean; keepWithNext?: boolean };
const root = process.env.DOCUMENTATION_ROOT ?? path.resolve(process.cwd(), '../docs/projects');
const titleOf = (source: string, fallback: string) => source.match(/^#\s+(.+)$/m)?.[1]?.replace(/\s+—.*$/, '') ?? fallback;
export async function documentationEntries(slug: string, language: Language): Promise<TocEntry[]> {
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) return [];
  let directory: string;
  try { directory = await realpath(path.join(root, slug)); if (!directory.startsWith((await realpath(root)) + path.sep)) return []; } catch { return []; }
  async function files(relative: string): Promise<string[]> {
    try { const entries = await readdir(path.join(directory, relative), { withFileTypes: true });
      return (await Promise.all(entries.filter(e => !e.isSymbolicLink()).map(async e => e.isDirectory() ? files(`${relative}/${e.name}`) : e.name.endsWith('.md') ? [`${relative}/${e.name}`] : []))).flat();
    } catch { return []; }
  }
  const localized = await Promise.all((['en', 'pt-BR'] as const).map(async lang => {
    const sources = new Map<string, { source: string; relative: string }>();
    for (const relative of await files(`docs/${lang}`)) {
      const source = await readFile(path.join(directory, relative), 'utf8');
      // Navigation-only indexes contain a title, backlink and list of links. Preserve substantive indexes.
      const substantive = source.split('\n').filter(line => line.trim() && !/^#\s|^\s*(?:[-*]\s+)?\[[^\]]+\]\([^)]+\)\s*$/.test(line));
      if (relative.endsWith('/index.md') && !substantive.length) continue;
      sources.set(relative.slice(`docs/${lang}/`.length), { source, relative });
    }
    const relative = lang === 'en' ? 'README.md' : 'README.pt-BR.md';
    try { sources.set('README', { source: await readFile(path.join(directory, relative), 'utf8'), relative }); } catch { /* Explicit missing counterpart below. */ }
    return sources;
  }));
  const selected = localized[language === 'en' ? 0 : 1];
  const alphabetical = (a: string, b: string) => a.toLowerCase() < b.toLowerCase() ? -1 : a.toLowerCase() > b.toLowerCase() ? 1 : a < b ? -1 : a > b ? 1 : 0;
  const ids = [...new Set(localized.flatMap(map => [...map.keys()]))].sort(alphabetical);
  const groups = [...new Set(ids.map(id => id.split('/')[0]))].sort(alphabetical);
  const result: TocEntry[] = [];
  const entry = (id: string, number: string, heading = false): TocEntry => {
    const doc = selected.get(id);
    return { id, number, heading, title: doc ? titleOf(doc.source, id) : `${id} (${language === 'en' ? 'unavailable' : 'indisponível'})`, href: doc ? `https://github.com/juniocr26/engineering-library/blob/main/docs/projects/${slug}/${doc.relative}` : undefined };
  };
  groups.forEach((group, index) => {
    const children = ids.filter(id => id.startsWith(`${group}/`));
    if (!children.length) result.push(entry(group, `${index + 1}`, true));
    else {
      result.push({ id: `category:${group}`, number: `${index + 1}`, title: categoryLabels[language][group] ?? group, heading: true, keepWithNext: true });
      children.forEach((id, child) => result.push(entry(id, `${index + 1}.${child + 1}`)));
    }
  });
  return result;
}
