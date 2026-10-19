import type { Language } from './i18n.ts';

export function documentHref(project: string, document: string, language: Language, anchor?: string) {
  return `/projects/${encodeURIComponent(project)}/docs/${document.split('/').map(encodeURIComponent).join('/')}?lang=${language}${anchor ? `#${encodeURIComponent(anchor)}` : ''}`;
}

/** Reserved virtual document; anchors are canonical TocEntry IDs, never page numbers. */
export const CONTENTS_DOCUMENT = '@contents';
export function bookmarkHref(project: string, document: string, language: Language, anchor?: string) {
  return document === CONTENTS_DOCUMENT
    ? `/projects/${encodeURIComponent(project)}?lang=${language}${anchor ? `#${encodeURIComponent(anchor)}` : ''}`
    : documentHref(project, document, language, anchor);
}

export function sourcePath(document: string, language: Language) {
  return document === 'README' ? (language === 'en' ? 'README.md' : 'README.pt-BR.md') : `docs/${language}/${document}`;
}

/** Resolve only collection Markdown/assets. Other HTTP(S)/mail links retain their meaning. */
export function resolveDocumentLink(project: string, document: string, language: Language, href: string, image = false): string | undefined {
  if (href.startsWith('#')) return href;
  const repository = 'https://github.com/juniocr26/engineering-library/blob/main/docs/projects/';
  const github = href.match(/^https:\/\/github\.com\/juniocr26\/([a-z0-9-]+)\/blob\/(?:main|master)\/(.+\.md(?:#.*)?)$/);
  if (/^(?:https?:|mailto:)/i.test(href) && !href.startsWith(repository) && !github) return href;
  if (/^[a-z][a-z\d+.-]*:|^\/\//i.test(href) && !/^https?:/i.test(href)) return undefined;
  try {
    const target = href.startsWith(repository)
      ? new URL(`https://reader.invalid/workspace/engineering-library/docs/projects/${href.slice(repository.length)}`)
      : github ? new URL(`https://reader.invalid/workspace/${github[1]}/${github[2]}`)
      : new URL(href, `https://reader.invalid/workspace/engineering-library/docs/projects/${project}/${sourcePath(document, language)}`);
    const pathname = decodeURIComponent(target.pathname);
    if (/[\\\0]/.test(pathname)) return undefined;
    const prefix = '/workspace/engineering-library/docs/projects/';
    const parts = pathname.startsWith(prefix) ? pathname.slice(prefix.length).split('/') : pathname.startsWith('/workspace/') ? pathname.slice('/workspace/'.length).split('/') : [];
    const slug = parts.shift()!;
    if (!slug || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) return undefined;
    const relative = parts.join('/');
    if (image) return /\.(png|jpe?g|gif|webp|svg)$/i.test(relative) ? `/api/document-assets/${[slug, ...parts].map(encodeURIComponent).join('/')}` : undefined;
    let id: string; let lang = language;
    if (relative === 'README.md' || relative === 'README.pt-BR.md') {
      id = 'README'; lang = relative === 'README.md' ? 'en' : 'pt-BR';
    } else {
      const match = relative.match(/^docs\/(en|pt-BR)\/(.+\.md)$/);
      if (!match) return undefined;
      lang = match[1] as Language; id = match[2];
    }
    return documentHref(slug, id, lang, target.hash ? decodeURIComponent(target.hash.slice(1)) : undefined);
  } catch { return undefined; }
}
