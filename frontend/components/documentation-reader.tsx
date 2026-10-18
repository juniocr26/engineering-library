'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { BookReader } from './book-reader';
import { DocumentLanguage } from './document-language';
import { MarkdownUnit } from './markdown-unit';
import { ReaderPanel } from './reader-panel';
import { documentHref } from '../lib/document-links';
import type { TocEntry } from '../lib/documentation';
import type { MarkdownUnit as Unit } from '../lib/markdown';
import type { Language } from '../lib/i18n';

type Bookmark = { id: number; project: string; document: string; language: Language; anchor: string; excerpt: string };
type SearchResult = { title: string; excerpt: string; href: string; anchor: string };
type Panel = 'search' | 'chapters' | 'bookmarks';
function ReaderIcon({ name }: { name: Panel | 'page' }) {
  return <svg viewBox="0 0 24 24" width="21" height="21" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    {name === 'search' ? <><circle cx="10" cy="10" r="6.5"/><path d="m15 15 6 6"/></> : name === 'chapters' ? <><path d="M4 3h13a2 2 0 0 1 2 2v16H6a3 3 0 0 1-3-3V4a1 1 0 0 1 1-1Z"/><path d="M6 3v14M4 17h15M10 7h5M10 10h5"/></> : name === 'bookmarks' ? <><path d="M5 3h9v16l-4.5-4L5 19ZM18 5h3v16l-3-3"/></> : <path d="M6 3h12v18l-6-5-6 5Z"/>}
  </svg>;
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

export function DocumentationReader({ project, document: documentId, language, units, entries, query }: {
  project: string; document: string; language: Language; units: Unit[]; entries: TocEntry[]; query: string;
}) {
  const en = language === 'en';
  const [panel, setPanel] = useState<Panel | null>(null);
  const [location, setLocation] = useState('');
  const [locationRequest, setLocationRequest] = useState(0);
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [csrf, setCsrf] = useState('');
  const [bookmarkError, setBookmarkError] = useState(false);
  const [busy, setBusy] = useState(false);
  const title = entries.find(entry => entry.id === documentId)?.title ?? units.find(unit => unit.heading !== undefined)?.text ?? documentId;
  const labels = { search: en ? 'Search' : 'Pesquisar', chapters: en ? 'Chapter index' : 'Índice de capítulos', bookmarks: en ? 'My Bookmarks' : 'Minhas marcações' };

  useEffect(() => {
    const update = () => {
      try { setLocation(decodeURIComponent(window.location.hash.slice(1))); setLocationRequest(previous => previous + 1); } catch { setLocation(''); }
    };
    update(); window.addEventListener('hashchange', update);
    return () => window.removeEventListener('hashchange', update);
  }, [documentId, language, units]);

  useEffect(() => {
    const controller = new AbortController();
    void fetch('/api/bookmarks', { cache: 'no-store', signal: controller.signal }).then(async response => {
      if (!response.ok) throw new Error('Bookmarks unavailable');
      return response.json();
    }).then(data => { setBookmarks(data.bookmarks); setCsrf(data.csrf_token); setBookmarkError(false); }, () => { if (!controller.signal.aborted) setBookmarkError(true); });
    return () => controller.abort();
  }, []);

  async function mutate(bookmark?: Bookmark, unit?: Unit) {
    if (busy || !csrf) return;
    setBusy(true); setBookmarkError(false);
    try {
      const response = await fetch(bookmark ? `/api/bookmarks/${bookmark.id}` : '/api/bookmarks', {
        method: bookmark ? 'DELETE' : 'POST', headers: { 'Content-Type': 'application/json', 'X-Reader-CSRF': csrf },
        body: bookmark ? undefined : JSON.stringify({ project, document: documentId, language, anchor: unit!.id, excerpt: unit!.text.slice(0, 240) }),
      });
      if (!response.ok) throw new Error('Bookmark mutation failed');
      if (bookmark) setBookmarks(previous => previous.filter(item => item.id !== bookmark.id));
      else { const saved = await response.json(); setBookmarks(previous => [saved, ...previous.filter(item => item.id !== saved.id)]); }
    } catch { setBookmarkError(true); }
    finally { setBusy(false); }
  }

  const header = <header className="reader-document-header">
    <Link href={`/projects/${encodeURIComponent(project)}?lang=${language}`}>← {en ? 'Contents' : 'Sumário'}</Link><span>{project}</span>
    <nav className="reader-toolbar" aria-label={en ? 'Reader tools' : 'Ferramentas de leitura'}>
      {(['search', 'chapters', 'bookmarks'] as const).map(name => <button key={name} type="button" title={labels[name]} aria-label={labels[name]} onClick={() => setPanel(name)}><ReaderIcon name={name}/></button>)}
    </nav>
    <nav className="reader-document-languages" aria-label={en ? 'Language' : 'Idioma'}>{(['pt-BR', 'en'] as const).map(lang => <Link key={lang} href={documentHref(project, documentId, lang, location)} aria-current={lang === language ? 'true' : undefined} hrefLang={lang}>{lang === 'en' ? '🇺🇸 English' : '🇧🇷 Português'}</Link>)}</nav>
  </header>;

  return <main className="scene toc-scene" lang={language} onClick={event => {
    const link = (event.target as HTMLElement).closest<HTMLAnchorElement>('a[href]');
    if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const target = new URL(link.href);
    if (target.pathname === window.location.pathname && target.search === window.location.search && target.hash) {
      try { setLocation(decodeURIComponent(target.hash.slice(1))); setLocationRequest(previous => previous + 1); } catch { /* Invalid anchors keep their native link behavior. */ }
    }
  }}><DocumentLanguage language={language}/><div className="toc-shell documentation-shell">
    <BookReader units={units} project={project} language={language} title={title} header={header} location={location} locationRequest={locationRequest}
      renderUnit={unit => <MarkdownUnit unit={unit} project={project} document={documentId} language={language} query={unit.id === location ? query : ''}/>}
      pageAction={page => {
        const saved = bookmarks.find(bookmark => bookmark.project === project && bookmark.document === documentId && bookmark.language === language && page.some(unit => unit.id === bookmark.anchor));
        const label = saved ? (en ? 'Remove page bookmark' : 'Remover marcação da página') : (en ? 'Bookmark this page' : 'Marcar esta página');
        return <div className="reader-page-bookmark"><span className={`bookmark-ribbon${saved ? ' bookmark-ribbon--saved' : ''}`} aria-hidden="true"/><button type="button" className="reader-bookmark-toggle" title={label} aria-label={label} aria-pressed={!!saved} disabled={busy || !csrf} onClick={() => void mutate(saved, page[0])}><ReaderIcon name="page"/></button></div>;
      }}/>
    {location && !units.some(unit => unit.id === location) && <p role="status" className="reader-notice">{en ? 'This saved location is no longer available in this language. Showing the document start.' : 'Esta posição não está mais disponível neste idioma. Exibindo o início do documento.'}</p>}
    {bookmarkError && <p role="alert" className="reader-notice">{en ? 'Bookmarks unavailable. Reload to try again.' : 'Marcações indisponíveis. Recarregue para tentar novamente.'}</p>}
    {panel && <ReaderPanel title={labels[panel]} close={() => setPanel(null)} closeLabel={en ? 'Close panel' : 'Fechar painel'}>
      {panel === 'search' && <Search project={project} language={language} close={() => setPanel(null)}/>}
      {panel === 'chapters' && <>
        <h3>{title}</h3><ul className="reader-panel-list">{units.filter(unit => unit.heading !== undefined).map(unit => <li key={unit.id}><a href={`#${encodeURIComponent(unit.id)}`} onClick={() => setPanel(null)}>{unit.text}</a></li>)}</ul>
        <h3>{en ? 'Project documents' : 'Documentos do projeto'}</h3><ul className="reader-panel-list">{entries.map(entry => <li key={entry.id}>{entry.href ? <Link href={entry.href} aria-current={entry.id === documentId ? 'page' : undefined} onClick={() => setPanel(null)}>{entry.number} {entry.title}</Link> : <strong>{entry.number} {entry.title}</strong>}</li>)}</ul>
      </>}
      {panel === 'bookmarks' && <>
        <p>{en ? 'Saved in this browser. Clearing its identity removes access; bookmarks do not sync across devices.' : 'Salvas neste navegador. Limpar sua identidade remove o acesso; marcações não sincronizam entre dispositivos.'}</p>
        {!bookmarks.length && <p>{en ? 'No bookmarks yet.' : 'Nenhuma marcação ainda.'}</p>}
        <ul className="reader-panel-list">{bookmarks.map(bookmark => <li key={bookmark.id} className="reader-saved-bookmark"><Link href={documentHref(bookmark.project, bookmark.document, bookmark.language, bookmark.anchor)} onClick={() => setPanel(null)}><strong>{bookmark.project} · {bookmark.document}</strong><span>{bookmark.excerpt}</span></Link><button type="button" aria-label={en ? 'Remove bookmark' : 'Remover marcação'} disabled={busy} onClick={() => void mutate(bookmark)}>×</button></li>)}</ul>
      </>}
    </ReaderPanel>}
  </div></main>;
}
