'use client';
import { headingTitle } from '../lib/heading-numbering';
import { normalizeCursiveLabel } from '../lib/cursive-headings';
import { getReadingSequence, readingNeighbors } from '../lib/reading-order';
import { useEffect, useMemo, useState, type ReactNode } from 'react';
import { BookReader } from './book-reader';
import { ReaderTools } from './reader-tools';
import Link from '@/components/navigation-link';
import { CONTENTS_DOCUMENT, bookmarkHref } from '../lib/document-links';
import { projectDisplayName } from '../lib/project-name';
import { catalogHref, messages, type Language } from '../lib/i18n';
import type { TocEntry } from '../lib/documentation';
export function TableOfContents({ entries, slug, language, projectName, catalogPage = 1, initialEnd = false }: { entries: TocEntry[]; slug: string; language: Language; projectName?: string; catalogPage?: number; initialEnd?: boolean }) {
  const [location, setLocation] = useState('');
  const [expanded, setExpanded] = useState<Set<string>>(() => new Set(entries.filter(entry => entry.id.startsWith('category:')).map(entry => entry.id)));
  const parents = useMemo(() => new Set(entries.flatMap(entry => entry.parentId ? [entry.parentId] : [])), [entries]);
  const expandedIds = useMemo(() => {
    const byId = new Map(entries.map(entry => [entry.id, entry]));
    const next = new Set(expanded);
    let target = byId.get(location);
    while (target?.parentId) { next.add(target.parentId); target = byId.get(target.parentId); }
    return next;
  }, [entries, expanded, location]);
  const visibleEntries = useMemo(() => {
    const byId = new Map(entries.map(entry => [entry.id, entry]));
    return entries.filter(entry => {
      let parent = entry.parentId;
      while (parent) {
        if (!expandedIds.has(parent)) return false;
        parent = byId.get(parent)?.parentId;
      }
      return true;
    }).map(entry => ({ ...entry, keepWithNext: parents.has(entry.id) && expandedIds.has(entry.id) }));
  }, [entries, expandedIds, parents]);
  const [locationRequest, setLocationRequest] = useState(0);
  const [visibleAnchor, setVisibleAnchor] = useState('');
  const title = language === 'en' ? 'Table of Contents' : 'Sumário';
  useEffect(() => {
    const update = () => {
      try { setLocation(decodeURIComponent(window.location.hash.slice(1))); setLocationRequest(value => value + 1); } catch { setLocation(''); }
    };
    update(); window.addEventListener('hashchange', update);
    return () => window.removeEventListener('hashchange', update);
  }, [slug, language]);
  return <div onClick={event => {
      const link = (event.target as HTMLElement).closest<HTMLAnchorElement>('a[href]');
      if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      const target = new URL(link.href);
      if (target.pathname === window.location.pathname && target.search === window.location.search && target.hash) {
        try { setLocation(decodeURIComponent(target.hash.slice(1))); setLocationRequest(value => value + 1); } catch { /* Preserve native navigation for malformed hashes. */ }
      }
    }}><ReaderTools key={slug} project={slug} projectName={projectName} document={CONTENTS_DOCUMENT} language={language} entries={entries} title={title}>{({ toolbar, pageAction }) => {
    const header = (action: ReactNode) => <header className="toc-header reader-tools-header">
      <Link className="back" href={catalogHref(catalogPage, language)}>{messages[language].back}</Link><span>{projectDisplayName(slug, projectName)}</span>
      <details className="toc-mobile-menu"><summary aria-label={language === 'en' ? 'Navigation menu' : 'Menu de navegação'}>☰</summary><Link href={catalogHref(catalogPage, language)}>{messages[language].back}</Link></details>
      {toolbar(action)}
      <nav className="langs" aria-label={messages[language].language}>{(['pt-BR', 'en'] as const).map(lang => <Link key={lang} className="lang" href={bookmarkHref(slug, CONTENTS_DOCUMENT, lang, visibleAnchor).replace('?', `?page=${catalogPage}&`)} hrefLang={lang} aria-current={lang === language ? 'true' : undefined}><span className="flag" aria-hidden="true">{lang === 'en' ? '🇺🇸' : '🇧🇷'}</span>{lang === 'en' ? 'English' : 'Português'}</Link>)}</nav>
      <h1>{normalizeCursiveLabel(title)}<span className="toc-quill" aria-hidden="true"/></h1>
    </header>;
    return <BookReader key={slug} initialEnd={initialEnd} location={location} locationRequest={locationRequest} onLocationChange={setVisibleAnchor} pageAction={pageAction} nextChapter={readingNeighbors(getReadingSequence(slug, language, entries), null).next} units={visibleEntries} header={header} project={slug} language={language} title={title} renderUnit={entry => {
      const text = <><span className="chapter-number">{entry.number}</span><span>{entry.heading ? normalizeCursiveLabel(headingTitle(entry.title, entry.number)) : headingTitle(entry.title, entry.number)}</span></>;
      const content = entry.href ? <Link href={entry.href}>{text}<span className="toc-leader" aria-hidden="true"/>↗</Link> : <span aria-disabled={!entry.heading || undefined}>{text}</span>;
      const toggle = parents.has(entry.id) ? <button type="button" className="toc-toggle" aria-expanded={expandedIds.has(entry.id)} aria-label={`${expandedIds.has(entry.id) ? (language === 'en' ? 'Collapse' : 'Recolher') : (language === 'en' ? 'Expand' : 'Expandir')}: ${entry.title}`} onClick={() => {
        const next = new Set(expandedIds);
        if (next.has(entry.id)) { next.delete(entry.id); setLocation(''); } else next.add(entry.id);
        setExpanded(next);
      }}>{expandedIds.has(entry.id) ? '−' : '+'}</button> : null;
      return <div className="toc-row" style={{ paddingInlineStart: `${Math.min(entry.depth ?? (entry.heading ? 0 : 1), 5) * 10}px` }}>
        {toggle}{entry.heading ? <h2 className="toc-chapter chapter-title" data-chapter-depth={entry.depth}>{content}</h2> : <div className="toc-document chapter-title" data-chapter-depth={entry.depth}>{content}</div>}
      </div>;
    }}/>;
  }}</ReaderTools></div>;
}
