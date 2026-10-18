import type { Language } from './i18n.ts';

export function documentHref(project: string, document: string, language: Language, anchor?: string) {
  return `/projects/${encodeURIComponent(project)}/docs/${document.split('/').map(encodeURIComponent).join('/')}?lang=${language}${anchor ? `#${encodeURIComponent(anchor)}` : ''}`;
}

export function sourcePath(document: string, language: Language) {
  return document === 'README' ? (language === 'en' ? 'README.md' : 'README.pt-BR.md') : `docs/${language}/${document}`;
}

/** Resolve only collection Markdown/assets. Other HTTP(S)/mail links retain their meaning. */
export function resolveDocumentLink(project: string, document: string, language: Language, href: string, image = false): string | undefined {
  if (href.startsWith('#')) return href;
  if (/^(?:https?:|mailto:)/i.test(href) && !href.startsWith('https://github.com/juniocr26/engineering-library/blob/main/docs/projects/')) return href;
  if (/^[a-z][a-z\d+.-]*:|^\/\//i.test(href)) return undefined;
  try {
    const repository = 'https://github.com/juniocr26/engineering-library/blob/main/docs/projects/';
    const target = href.startsWith(repository) ? new URL(`https://reader.invalid/collection/${href.slice(repository.length)}`) : new URL(href, `https://reader.invalid/collection/${project}/${sourcePath(document, language)}`);
    const pathname = decodeURIComponent(target.pathname);
    if (!pathname.startsWith('/collection/') || /[\\\0]/.test(pathname)) return undefined;
    const parts = pathname.slice('/collection/'.length).split('/');
    const slug = parts.shift()!;
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) return undefined;
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
