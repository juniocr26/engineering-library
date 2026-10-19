import { documentHref } from './document-links.ts';
import { sourceLocation, type SourceReference } from './source-links.ts';
import type { Language } from './i18n.ts';
export function sourceSearchResults(project: string, document: string, language: Language, title: string, ref: SourceReference, query: string) {
  if (ref.status !== 'available' || ref.project !== project || !query) return [];
  return (ref.lines ?? []).flatMap((line, index) => {
    const offset = line.toLowerCase().indexOf(query.toLowerCase());
    if (offset < 0) return [];
    const number = (ref.start ?? 1) + index;
    const anchor = sourceLocation(ref, number);
    const href = documentHref(project, document, language, anchor).replace('?lang=', `?q=${encodeURIComponent(query)}&lang=`);
    return [{ kind: 'source' as const, project, document, sourceKey: ref.sourceKey, sourcePath: ref.path, revision: ref.revision, fingerprint: ref.fingerprint, occurrence: ref.id, line: number,
      title: `${title} · ${ref.path}:${number}`, excerpt: line.slice(Math.max(0, offset - 65), offset + query.length + 110), href, anchor }];
  });
}
