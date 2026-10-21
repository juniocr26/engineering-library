'use client';
import { headingTitle } from '../lib/heading-numbering';
import { useEffect, useRef, useState, type ReactNode } from 'react';
import Link from '@/components/navigation-link';
import { AnnotationsPanel } from './annotations-panel';
import { ReaderPanel } from './reader-panel';
import { bookmarkHref, CONTENTS_DOCUMENT } from '../lib/document-links';
import { projectDisplayName } from '../lib/project-name';
import { containsLocation } from '../lib/table-pagination';
import type { BookUnit } from '../lib/book-pagination';
import type { TocEntry } from '../lib/documentation';
import type { Language } from '../lib/i18n';
type Bookmark = { id: number; project: string; document: string; language: Language; anchor: string; excerpt: string };
type SearchResult = { title: string; excerpt: string; href: string; anchor: string };
type Panel = 'search' | 'chapters' | 'bookmarks' | 'annotations';
function ReaderIcon({ name }: { name: Panel | 'page' }) {
  return <svg viewBox="0 0 24 24" width="21" height="21" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    {name === 'annotations' ? <><path d="M5 3h14v18H5zM3 6h4M3 11h4M3 16h4M10 7h5M10 11h5M10 15h3"/></> : name === 'search' ? <><circle cx="10" cy="10" r="6.5"/><path d="m15 15 6 6"/></> : name === 'chapters' ? <><path d="M4 3h13a2 2 0 0 1 2 2v16H6a3 3 0 0 1-3-3V4a1 1 0 0 1 1-1Z"/><path d="M6 3v14M4 17h15M10 7h5M10 10h5"/></> : name === 'bookmarks' ? <><path d="M5 3h9v16l-4.5-4L5 19ZM18 5h3v16l-3-3"/></> : <path d="M6 3h12v18l-6-5-6 5Z"/>}
  </svg>;
}

/** A keyed page control keeps animation state local to a stable reading location. */
function PageBookmark({ saved, disabled, en, toggle }: {
  saved: boolean; disabled: boolean; en: boolean; toggle: () => void;
}) {
  const [retracting, setRetracting] = useState(false);
  const [previousSaved, setPreviousSaved] = useState(saved);
  const ribbon = useRef<HTMLButtonElement>(null);
  const button = useRef<HTMLButtonElement>(null);
  const transferFocus = useRef(false);
  if (previousSaved !== saved) {
    setPreviousSaved(saved);
    setRetracting(!saved);
  }
  useEffect(() => {
    if (saved && transferFocus.current) {
      ribbon.current?.focus({ preventScroll: true });
      transferFocus.current = false;
    }
    if (!retracting) return;
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    const finish = () => setRetracting(false);
    // The fallback also completes exits when a transition is cancelled or interrupted.
    const timer = window.setTimeout(finish, reduced.matches ? 0 : 400);
    const changed = () => { if (reduced.matches) finish(); };
    reduced.addEventListener('change', changed);
    return () => { clearTimeout(timer); reduced.removeEventListener('change', changed); };
  }, [saved, retracting]);
  useEffect(() => {
    if (!saved && !retracting && transferFocus.current) {
      button.current?.focus({ preventScroll: true });
      transferFocus.current = false;
    }
  }, [saved, retracting]);
  const label = saved || retracting ? (en ? 'Remove bookmark' : 'Remover marcação') : (en ? 'Bookmark page' : 'Marcar página');
  return <div className="reader-page-bookmark">
    <button ref={ribbon} type="button" className={`bookmark-ribbon${saved ? ' bookmark-ribbon--saved' : ''}`}
      aria-label={label} title={label} aria-hidden={!saved && !retracting} tabIndex={saved ? 0 : -1}
      disabled={disabled || !saved} onClick={() => { transferFocus.current = true; toggle(); }}
      onTransitionEnd={event => { if (event.target === event.currentTarget && event.propertyName === 'transform' && !saved) setRetracting(false); }}/>
    {!saved && !retracting && <button ref={button} type="button" className="reader-bookmark-toggle" title={label} aria-label={label}
      disabled={disabled} onClick={() => { transferFocus.current = true; toggle(); }}><ReaderIcon name="page"/></button>}
  </div>;
}

function Search({ project, language, close }: { project: string; language: Language; close: () => void }) {
  const en = language === 'en';
  const [query, setQuery] = useState('');
  const [state, setState] = useState<{ query: string; results: SearchResult[]; truncated?: boolean; error?: boolean } | null>(null);
  useEffect(() => {
    const controller = new AbortController();
    if (query.trim().length < 2) return () => controller.abort();
    const timer = setTimeout(() => {
      void fetch(`/api/document-search/${encodeURIComponent(project)}?lang=${language}&q=${encodeURIComponent(query.trim())}`, { signal: controller.signal }).then(async response => {
        if (!response.ok) throw new Error('Search failed');
        return response.json();
      }).then(data => setState({ ...data, query }), () => { if (!controller.signal.aborted) setState({ query, results: [], error: true }); });
    }, 250);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [query, language, project]);
  return <>
    <label htmlFor="reader-search">{en ? 'Search project documentation' : 'Pesquisar documentação do projeto'}</label>
    <input id="reader-search" type="search" maxLength={100} value={query} onChange={event => setQuery(event.target.value)} placeholder={en ? 'At least 2 characters' : 'Pelo menos 2 caracteres'}/>
    <p role="status">{query.trim().length < 2 ? '' : state?.query !== query ? (en ? 'Searching…' : 'Pesquisando…') : state.error ? (en ? 'Search unavailable. Try again.' : 'Pesquisa indisponível. Tente novamente.') : `${state.results.length}${state.truncated ? '+' : ''} ${en ? 'results found' : 'resultados encontrados'}`}</p>
    {state?.query === query && <ul className="reader-panel-list">{state.results.map(result => <li key={`${result.href}`}><Link href={result.href} onClick={close}><strong>{result.title}</strong><span>{result.excerpt}</span></Link></li>)}</ul>}
  </>;
}

export function ReaderTools({ project, projectName, document: documentId, language, entries, title, headings = [], children }: {
  project: string; projectName?: string; document: string; language: Language; entries: TocEntry[]; title: string;
  headings?: { id: string; text: string; navigationNumber?: string }[];
  children: (tools: { toolbar: (action: ReactNode) => ReactNode; pageAction: (page: BookUnit[]) => ReactNode }) => ReactNode;
}) {
  const en = language === 'en';
  const [panel, setPanel] = useState<Panel | null>(null);
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [csrf, setCsrf] = useState('');
  const [bookmarkError, setBookmarkError] = useState(false);
  const [busy, setBusy] = useState(false);
  const mutationPending = useRef(false);
  const labels = { annotations: en ? 'Highlights and Notes' : 'Destaques e notas', search: en ? 'Search' : 'Pesquisar', chapters: en ? 'Chapter index' : 'Índice de capítulos', bookmarks: en ? 'My Bookmarks' : 'Minhas marcações' };

  useEffect(() => {
    const controller = new AbortController();
    void fetch(`/api/bookmarks?project_slug=${encodeURIComponent(project)}&language=${language}`, { cache: 'no-store', signal: controller.signal }).then(async response => {
      if (!response.ok) throw new Error('Bookmarks unavailable');
      return response.json();
    }).then(data => { if (controller.signal.aborted) return; setBookmarks(data.bookmarks.filter((item: Bookmark) => item.project === project && item.language === language)); setCsrf(data.csrf_token); setBookmarkError(false); }, () => { if (!controller.signal.aborted) setBookmarkError(true); });
    return () => controller.abort();
  }, [project, language]);

  async function mutate(bookmark?: Bookmark, unit?: { id: string; text: string }) {
    if (mutationPending.current || !csrf) return;
    mutationPending.current = true;
    setBusy(true); setBookmarkError(false);
    try {
      const response = await fetch(bookmark ? `/api/bookmarks/${bookmark.id}?language=${language}` : '/api/bookmarks', {
        method: bookmark ? 'DELETE' : 'POST', headers: { 'Content-Type': 'application/json', 'X-Annotation-CSRF': csrf },
        body: bookmark ? undefined : JSON.stringify({ project, document: documentId, language, anchor: unit!.id, excerpt: unit!.text.slice(0, 240) }),
      });
      if (!response.ok) throw new Error('Bookmark mutation failed');
      if (bookmark) setBookmarks(previous => previous.filter(item => item.id !== bookmark.id));
      else { const saved = await response.json(); setBookmarks(previous => [saved, ...previous.filter(item => item.id !== saved.id)]); }
    } catch { setBookmarkError(true); }
    finally { mutationPending.current = false; setBusy(false); }
  }

  const toolbar = (action: ReactNode) => <>
    <nav className="reader-toolbar" aria-label={en ? 'Reader tools' : 'Ferramentas de leitura'}>
      {(['search', 'chapters', 'bookmarks', 'annotations'] as const).map(name => <button key={name} type="button" title={labels[name]} aria-label={labels[name]} onClick={() => setPanel(name)}><ReaderIcon name={name}/></button>)}
      <div className="reader-bookmark-slot">{action}</div>
    </nav>
  </>;
  const pageAction = (page: BookUnit[]) => {
    const saved = bookmarks.find(bookmark => bookmark.project === project && bookmark.document === documentId && bookmark.language === language && page.some(unit => containsLocation(unit, bookmark.anchor)));
    const first = page[0] as BookUnit & { text?: string; title?: string };
    return <PageBookmark key={`${project}/${documentId}/${language}/${page.map(unit => unit.id).join('/')}`} saved={!!saved} disabled={busy || !csrf} en={en} toggle={() => void mutate(saved, { id: first.id, text: first.text ?? first.title ?? title })}/>;
  };
  return <>{children({ toolbar, pageAction })}
    {bookmarkError && <p role="alert" className="reader-notice">{en ? 'Bookmarks unavailable. Reload to try again.' : 'Marcações indisponíveis. Recarregue para tentar novamente.'}</p>}
    {panel && <ReaderPanel title={labels[panel]} close={() => setPanel(null)} closeLabel={en ? 'Close panel' : 'Fechar painel'}>
      {panel === 'annotations' && <AnnotationsPanel key={`${project}/${language}`} project={project} language={language} entries={entries} documentId={documentId} headings={headings} close={() => setPanel(null)}/>}
      {panel === 'search' && <Search project={project} language={language} close={() => setPanel(null)}/>}
      {panel === 'chapters' && <>
        {headings.length > 0 && <h3>{title}</h3>}<ul className="reader-panel-list">{headings.map(unit => <li key={unit.id}><a href={`#${encodeURIComponent(unit.id)}`} onClick={() => setPanel(null)}>{unit.navigationNumber ? `${unit.navigationNumber} ${headingTitle(unit.text, unit.navigationNumber)}` : unit.text}</a></li>)}</ul>
        <h3>{en ? 'Project documents' : 'Documentos do projeto'}</h3><ul className="reader-panel-list">{entries.map(entry => <li key={entry.id}>{entry.href ? <Link href={entry.href} aria-current={entry.id === documentId ? 'page' : undefined} onClick={() => setPanel(null)}>{entry.number} {headingTitle(entry.title, entry.number)}</Link> : <strong>{entry.number} {headingTitle(entry.title, entry.number)}</strong>}</li>)}</ul>
      </>}
      {panel === 'bookmarks' && <>
        <p>{en ? 'Shared in this local installation, organized by project and language.' : 'Compartilhadas nesta instalação local, organizadas por projeto e idioma.'}</p>
        {!bookmarks.filter(item => item.language === language).length && <p>{en ? 'No bookmarks saved for this project.' : 'Nenhuma marcação salva neste projeto.'}</p>}
        <ul className="reader-panel-list">{bookmarks.filter(item => item.language === language).map(bookmark => <li key={bookmark.id} className="reader-saved-bookmark"><Link href={bookmarkHref(bookmark.project, bookmark.document, bookmark.language, bookmark.anchor)} onClick={() => setPanel(null)}><strong>{projectDisplayName(bookmark.project, bookmark.project === project ? projectName : undefined)} · {bookmark.document === CONTENTS_DOCUMENT ? (bookmark.language === 'en' ? 'Table of Contents' : 'Sumário') : bookmark.document}</strong><span>{bookmark.excerpt}</span></Link><button type="button" aria-label={en ? 'Remove bookmark' : 'Remover marcação'} disabled={busy} onClick={() => void mutate(bookmark)}>×</button></li>)}</ul>
      </>}
    </ReaderPanel>}
  </>;
}
