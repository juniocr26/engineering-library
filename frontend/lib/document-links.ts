import { collectionPath, languageDirectory } from './catalog-paths.ts';
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
  return `${languageDirectory(language)}/${document === 'README' ? 'README.md' : document}`;
}

/** Resolve only collection Markdown/assets. Other HTTP(S)/mail links retain their meaning. */
export function resolveDocumentLink(project: string, document: string, language: Language, href: string, image = false): string | undefined {
  if (image && /^\/(?:assets\/|api\/shared-assets\/)/.test(href)) return href;
  if (href.startsWith('#')) return href;
  const repository = 'https://github.com/juniocr26/engineering-library/blob/main/docs/';
  const github = href.match(/^https:\/\/github\.com\/juniocr26\/([a-z0-9-]+)\/blob\/(?:main|master)\/(.+\.md(?:#.*)?)$/);
  if (/^(?:https?:|mailto:)/i.test(href) && !href.startsWith(repository) && !github) return href;
  if (/^[a-z][a-z\d+.-]*:|^\/\//i.test(href) && !/^https?:/i.test(href)) return undefined;
  try {
    const target = href.startsWith(repository)
      ? new URL(`https://reader.invalid/workspace/engineering-library/docs/${href.slice(repository.length)}`)
      : github ? new URL(`https://reader.invalid/workspace/${github[1]}/${github[2]}`)
      : new URL(href, `https://reader.invalid/workspace/engineering-library/docs/${collectionPath(project, sourcePath(document, language))}`);
    const pathname = decodeURIComponent(target.pathname);
    if (/[\\\0]/.test(pathname)) return undefined;
    const prefix = '/workspace/engineering-library/docs/';
    const physical = pathname.startsWith(prefix) ? pathname.slice(prefix.length) : '';
    if (/^[a-z0-9-]+\/(?:img|(?:en|pt-br)\/img)\/.+\.(png|jpe?g|gif|webp|svg)$/i.test(physical)) return `/api/shared-assets/${physical.split('/').map(encodeURIComponent).join('/')}`;
    const local = physical.match(/^([a-z0-9-]+)\/(en|pt-br)\/(.+)$/);
    const peer = !physical ? pathname.match(/^\/workspace\/([a-z0-9-]+)\/(.+)$/) : null;
    const slug = local?.[1] ?? peer?.[1];
    const relative = local ? `${local[2]}/${local[3]}` : peer?.[2];
    if (!slug || !relative || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) return undefined;
    if (image) return /\.(png|jpe?g|gif|webp|svg)$/i.test(relative) ? `/api/document-assets/${[slug, ...relative.split('/')].map(encodeURIComponent).join('/')}` : undefined;
    let id: string; let lang = language;
    if (peer && (relative === 'README.md' || relative === 'README.pt-BR.md')) {
      id = 'README'; lang = relative === 'README.md' ? 'en' : 'pt-BR';
    } else {
      const match = relative.match(peer ? /^docs\/(en|pt-br)\/(.+\.md)$/ : /^(en|pt-br)\/(.+\.md)$/);
      if (!match) return undefined;
      lang = match[1] === 'en' ? 'en' : 'pt-BR'; id = match[2] === 'README.md' ? 'README' : match[2];
    }
    return documentHref(slug, id, lang, target.hash ? decodeURIComponent(target.hash.slice(1)) : undefined);
  } catch { return undefined; }
}
