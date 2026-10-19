import { sourcePath } from './document-links.ts';
import type { Language } from './i18n.ts';
export type SourceTarget = { path: string; start?: number; end?: number; revision?: string };
export const sourceLanguages: Record<string, string> = { rs: 'rust', go: 'go', py: 'python', rb: 'ruby', js: 'javascript', jsx: 'javascript', ts: 'typescript', tsx: 'typescript', java: 'java', cs: 'csharp', php: 'php', sh: 'bash', sql: 'sql', json: 'json', yml: 'yaml', yaml: 'yaml', toml: 'ini' };
/** Lexical classification only. Approval and realpath validation happen on the server. */
export function sourceTarget(project: string, document: string, language: Language, href: string): SourceTarget | null {
  try {
    if (/[\\\0]/.test(href) || href.startsWith('#') || href.startsWith('//')) return null;
    let file: string; let hash: string; let revision: string | undefined;
    if (/^https?:/i.test(href)) {
      const url = new URL(href);
      if (url.origin !== 'https://github.com') return null;
      const match = decodeURIComponent(url.pathname).match(/^\/juniocr26\/([^/]+)\/blob\/([^/]+)\/(.+)$/);
      if (!match || match[1] !== project) return null;
      file = match[3]; revision = match[2]; hash = url.hash;
    } else {
      if (/^[a-z][\w+.-]*:|^\//i.test(href)) return null;
      const url = new URL(href, `https://reader.invalid/workspace/engineering-library/docs/projects/${project}/${sourcePath(document, language)}`);
      const decoded = decodeURIComponent(url.pathname);
      const collection = `/workspace/engineering-library/docs/projects/${project}/`;
      const repository = `/workspace/${project}/`;
      if (decoded.startsWith(collection)) file = decoded.slice(collection.length);
      else if (decoded.startsWith(repository)) file = decoded.slice(repository.length);
      else return null;
      hash = url.hash;
    }
    if (!file || file.split('/').some(part => !part || part === '.' || part === '..') || /[\\\0]/.test(file) || !sourceLanguages[file.split('.').pop()!.toLowerCase()]) return null;
    const lines = hash.match(/^#L(\d+)(?:-L?(\d+))?$/i);
    if (hash && !lines) return null;
    const start = lines ? Number(lines[1]) : undefined; const end = lines ? Number(lines[2] ?? lines[1]) : undefined;
    if (start !== undefined && (start < 1 || end! < start || !Number.isSafeInteger(end))) return null;
    return { path: file, ...(start ? { start, end } : {}), ...(revision ? { revision } : {}) };
  } catch { return null; }
}
export function canonicalSourceKey(project: string, relative: string, revision?: string) {
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(project) || !relative || relative.startsWith('/') || /[\\\0]/.test(relative) || relative.split('/').some(part => !part || part === '.' || part === '..')) throw new Error('Invalid canonical source identity');
  return JSON.stringify([project, relative, revision ?? null]);
}
export type SourceReference = SourceTarget & { sourceKey?: string; project?: string; id: string; href: string; language: string; status: 'available' | 'unapproved' | 'missing' | 'excluded' | 'revision-mismatch'; lines?: string[]; fingerprint?: string };
export type SourcePart = { start: number; end: number; maxHeight?: number };

export function sourceUnits<T extends { id: string; references?: SourceReference[] }>(units: T[], expanded: ReadonlySet<string>) {
  return units.flatMap(unit => [unit, ...(unit.references ?? []).filter(ref => expanded.has(ref.id)).map(ref => ({ id: ref.id, source: '', text: ref.path, code: ref }))]);
}

export function sourceLocation(ref: SourceReference, line: number) {
  return `${ref.id}${ref.fingerprint ? `--rev-${ref.fingerprint.slice(0, 16)}` : ''}--line-${line}`;
}
export function referenceContainsLocation(ref: SourceReference, location: string) {
  return location === ref.id || location.startsWith(sourceLocation(ref, 0).replace(/0$/, ''));
}
