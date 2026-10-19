import { readdir, readFile, realpath } from 'node:fs/promises';
import path from 'node:path';
import { categoryLabels, type Language } from './i18n.ts';
import { documentHref, sourcePath } from './document-links.ts';
export type TocEntry = { id: string; number: string; title: string; href?: string; heading?: boolean; keepWithNext?: boolean };
const root = process.env.DOCUMENTATION_ROOT ?? path.resolve(process.cwd(), '../docs/projects');
const titleOf = (source: string, fallback: string) => source.match(/^#\s+(.+)$/m)?.[1]?.replace(/\s+—.*$/, '') ?? fallback;
export async function documentationEntries(slug: string, language: Language): Promise<TocEntry[]> {
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) return [];
  let directory: string;
  try { directory = await realpath(path.join(root, slug)); if (!directory.startsWith((await realpath(root)) + path.sep)) return []; } catch { return []; }
  async function files(relative: string): Promise<string[]> {
    try { const resolved = await realpath(path.join(directory, relative));
      if (!resolved.startsWith(directory + path.sep)) return [];
      const entries = await readdir(resolved, { withFileTypes: true });
      return (await Promise.all(entries.filter(e => !e.isSymbolicLink()).map(async e => e.isDirectory() ? files(`${relative}/${e.name}`) : e.name.endsWith('.md') ? [`${relative}/${e.name}`] : []))).flat();
    } catch { return []; }
  }
  const localized = await Promise.all((['en', 'pt-BR'] as const).map(async lang => {
    const sources = new Map<string, { source: string; relative: string }>();
    for (const relative of await files(`docs/${lang}`)) {
      const source = (await collectionFile(slug, relative))?.toString('utf8');
      if (source === undefined) continue;
      // Navigation-only indexes contain a title, backlink and list of links. Preserve substantive indexes.
      const substantive = source.split('\n').filter(line => line.trim() && !/^#\s|^\s*(?:[-*]\s+)?\[[^\]]+\]\([^)]+\)\s*$/.test(line));
      if (relative.endsWith('/index.md') && !substantive.length) continue;
      sources.set(relative.slice(`docs/${lang}/`.length), { source, relative });
    }
    const relative = lang === 'en' ? 'README.md' : 'README.pt-BR.md';
    const readme = (await collectionFile(slug, relative))?.toString('utf8');
    if (readme !== undefined) sources.set('README', { source: readme, relative });
    return sources;
  }));
  const selected = localized[language === 'en' ? 0 : 1];
  const alphabetical = (a: string, b: string) => a.toLowerCase() < b.toLowerCase() ? -1 : a.toLowerCase() > b.toLowerCase() ? 1 : a < b ? -1 : a > b ? 1 : 0;
  const ids = [...new Set(localized.flatMap(map => [...map.keys()]))].sort(alphabetical);
  const groups = [...new Set(ids.map(id => id.split('/')[0]))].sort(alphabetical);
  const result: TocEntry[] = [];
  const entry = (id: string, number: string, heading = false): TocEntry => {
    const doc = selected.get(id);
    return { id, number, heading, title: doc ? titleOf(doc.source, id) : `${id} (${language === 'en' ? 'unavailable' : 'indisponível'})`, href: doc ? documentHref(slug, id, language) : undefined };
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

/** Every read resolves real paths; symlinks may not escape the selected project. */
export async function collectionFile(slug: string, relative: string): Promise<Buffer | null> {
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug) || !relative || relative.split('/').some(part => !part || part === '.' || part === '..') || /[\\\0]/.test(relative)) return null;
  try {
    const base = await realpath(root);
    const project = await realpath(path.join(base, slug));
    if (!project.startsWith(base + path.sep)) return null;
    const file = await realpath(path.join(project, relative));
    if (!file.startsWith(project + path.sep)) return null;
    return await readFile(file);
  } catch { return null; }
}

export async function documentationSource(slug: string, id: string, language: Language) {
  if (id !== 'README' && (!id.endsWith('.md') || id.startsWith('/') || /[\\\0]/.test(id) || id.split('/').some(part => part === '.' || part === '..' || !part))) return null;
  const buffer = await collectionFile(slug, sourcePath(id, language));
  return buffer?.toString('utf8') ?? null;
}
