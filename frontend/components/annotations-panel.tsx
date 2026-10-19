'use client';
import { useEffect, useMemo, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { NotePreview } from './note-editor';
import { noteExcerpt } from '../lib/annotation-excerpt';
import { documentHref } from '../lib/document-links';
import { readerIdentity } from '../lib/reader-identity';
import { highlightColors, type HighlightColor, type TextAnchor } from '../lib/text-anchors';
import type { TocEntry } from '../lib/documentation';
import type { Language } from '../lib/i18n';

type Filter = 'all' | 'notes' | HighlightColor;
type Annotation = { id: string; document: string; color: HighlightColor | null; segments: TextAnchor[]; note_id: number | null; body: string | null; created_at: string };
type Collection = { annotations: Annotation[]; counts: Record<Filter, number>; next_page: number | null };
function EyeIcon() { return <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true"><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></svg>; }
function AnnotationItem({ item, title, language, navigate, preview, section }: { section?: string; item: Annotation; title: string; language: Language; navigate: () => void; preview: () => void }) {
  const excerpt = useMemo(() => item.body !== null ? noteExcerpt(item.body) : null, [item.body]);
  const en = language === 'en';
  const colorLabel = item.color ? (en ? ['Yellow', 'Blue', 'Pink', 'Orange', 'Purple', 'Red', 'Green'] : ['Amarelo', 'Azul', 'Rosa', 'Laranja', 'Roxo', 'Vermelho', 'Verde'])[highlightColors.indexOf(item.color)] : (en ? 'Note' : 'Nota');
  return <li className="annotation-entry">
    <button className="annotation-location" onClick={navigate} aria-label={`${title} · ${colorLabel} · ${item.segments[0]?.exact ?? ''}`}>
      <span className="annotation-origin"><i className="annotation-color" style={{ background: item.color ? `var(--highlight-${item.color})` : 'transparent' }} aria-hidden="true"/>{title}</span>
      {section && <span>{section}</span>}
      <span>{item.segments.map((segment, index) => `${index && item.segments[index - 1].block !== segment.block ? ' ' : ''}${segment.exact}`).join('')}</span>
      <time dateTime={item.created_at}>{new Date(item.created_at).toLocaleDateString(en ? 'en-US' : 'pt-BR')}</time>
    </button>
    {excerpt && <div className="annotation-note"><span>{en ? 'Note: ' : 'Nota: '}{excerpt.text || (en ? 'Empty note' : 'Nota vazia')}</span>{excerpt.truncated && <button onClick={preview} aria-label={en ? 'Preview complete note' : 'Pré-visualizar nota completa'} title={en ? 'Preview complete note' : 'Pré-visualizar nota completa'}><EyeIcon/></button>}</div>}
  </li>;
}
export function AnnotationsPanel({ project, language, entries, close, documentId, headings }: { documentId: string; headings: { id: string; text: string }[]; project: string; language: Language; entries: TocEntry[]; close: () => void }) {
  const en = language === 'en';
  const router = useRouter();
  const [filter, setFilter] = useState<Filter>('all');
  const [data, setData] = useState<Collection | null>(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [unresolved, setUnresolved] = useState(false);
  const [retry, setRetry] = useState(0);
  const [preview, setPreview] = useState<Annotation | null>(null);
  const [popover, setPopover] = useState(false);
  const filters = useRef<HTMLDivElement>(null);
  const filterButton = useRef<HTMLButtonElement>(null);
  const previewFocus = useRef<HTMLElement | null>(null);
  const options: Filter[] = ['all', ...highlightColors, 'notes'];
  const names: Record<Filter, string> = { all: en ? 'All annotations' : 'Todas as anotações', notes: en ? 'Notes' : 'Notas', yellow: en ? 'Yellow' : 'Amarelo', blue: en ? 'Blue' : 'Azul', pink: en ? 'Pink' : 'Rosa', orange: en ? 'Orange' : 'Laranja', purple: en ? 'Purple' : 'Roxo', red: en ? 'Red' : 'Vermelho', green: en ? 'Green' : 'Verde' };
  useEffect(() => {
    const controller = new AbortController();
    void readerIdentity(project, language).then(() => fetch(`/api/annotations?${new URLSearchParams({ project, language, filter, page: String(page) })}`, { cache: 'no-store', signal: controller.signal })).then(async response => {
      if (!response.ok) throw Error();
      return response.json() as Promise<Collection>;
    }).then(value => {
      if (controller.signal.aborted) return;
      setData(previous => page === 1 || !previous ? value : { ...value, annotations: [...previous.annotations, ...value.annotations] });
      setLoading(false); setError(false);
    }, () => { if (!controller.signal.aborted) { setLoading(false); setError(true); } });
    return () => controller.abort();
  }, [project, language, filter, page, retry]);
  useEffect(() => {
    if (!popover) return;
    const outside = (event: PointerEvent) => { if (!filters.current?.contains(event.target as Node)) setPopover(false); };
    document.addEventListener('pointerdown', outside);
    const fit = () => {
      const menu = filters.current?.querySelector<HTMLElement>('[role="menu"]');
      if (menu) menu.style.maxHeight = `${Math.max(20, Math.min(480, innerHeight - menu.getBoundingClientRect().top - 16))}px`;
    };
    fit(); window.addEventListener('resize', fit);
    const frame = requestAnimationFrame(() => filters.current?.querySelector<HTMLElement>('[aria-checked="true"]')?.focus());
    return () => { cancelAnimationFrame(frame); window.removeEventListener('resize', fit); document.removeEventListener('pointerdown', outside); };
  }, [popover]);
  const choose = (value: Filter) => { setPopover(false); filterButton.current?.focus(); if (value !== filter) { setData(null); setLoading(true); setError(false); setPage(1); setFilter(value); } };
  function navigate(item: Annotation) {
    if (!entries.some(entry => entry.id === item.document && entry.href)) { setUnresolved(true); return; }
    const href = `${documentHref(project, item.document, language)}&annotation=${encodeURIComponent(item.id)}`;
    close(); router.push(href, { scroll: false });
    // Repeated navigation to an already-selected URL must still resolve the passage.
    window.dispatchEvent(new CustomEvent('reader-annotation-request', { detail: item.id }));
  }
  return <div className="annotations-library">
    <div className="annotation-filter" ref={filters} onKeyDown={event => {
      if (!popover) return;
      if (event.key === 'Escape') { event.preventDefault(); event.stopPropagation(); setPopover(false); filterButton.current?.focus(); }
      const buttons = Array.from(filters.current?.querySelectorAll<HTMLButtonElement>('[role="menuitemradio"]') ?? []);
      const index = buttons.indexOf(document.activeElement as HTMLButtonElement);
      const next = event.key === 'Home' ? 0 : event.key === 'End' ? buttons.length - 1 : event.key === 'ArrowDown' ? (index + 1) % buttons.length : event.key === 'ArrowUp' ? (index - 1 + buttons.length) % buttons.length : -1;
      if (next >= 0) { event.preventDefault(); buttons[next]?.focus(); }
      if (event.key === 'Tab') setPopover(false);
    }}>
      <button ref={filterButton} aria-label={en ? 'Filter annotations' : 'Filtrar anotações'} aria-expanded={popover} aria-haspopup="menu" onClick={() => setPopover(value => !value)}><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true"><path d="M3 7h18M3 17h18"/><circle cx="8" cy="7" r="3"/><circle cx="16" cy="17" r="3"/></svg></button>
      <span>{names[filter]}</span>
      {popover && <div className="annotation-filter-menu" role="menu" aria-label={en ? 'Annotation filters' : 'Filtros de anotações'}>{options.map(option => <button key={option} role="menuitemradio" aria-checked={filter === option} onClick={() => choose(option)}>{highlightColors.includes(option as HighlightColor) && <i className="annotation-color" style={{ background: `var(--highlight-${option})` }} aria-hidden="true"/>}{names[option]} <span>({data?.counts[option] ?? '…'})</span></button>)}</div>}
    </div>
    <p role="status">{loading ? (en ? 'Loading annotations…' : 'Carregando anotações…') : error ? (en ? 'Annotations unavailable.' : 'Anotações indisponíveis.') : !data?.annotations.length ? (filter === 'all' ? (en ? 'No highlights or notes in this project.' : 'Nenhum destaque ou nota neste projeto.') : filter === 'notes' ? (en ? 'No notes found.' : 'Nenhuma nota encontrada.') : (en ? 'No highlights in this color.' : 'Nenhum destaque nesta cor.')) : `${data.annotations.length} / ${data.counts[filter]}`}</p>
    {unresolved && <p role="alert">{en ? 'The source document is unavailable. The annotation is preserved.' : 'O documento de origem está indisponível. A anotação foi preservada.'}</p>}
    {error && <button onClick={() => { setError(false); setLoading(true); setRetry(value => value + 1); }}>{en ? 'Try again' : 'Tentar novamente'}</button>}
    <ul className="reader-panel-list annotation-list" aria-busy={loading}>{data?.annotations.map(item => <AnnotationItem key={item.id} item={item} section={item.document === documentId ? headings.find(heading => heading.id === item.segments[0]?.block.split('--')[0])?.text : undefined} title={entries.find(entry => entry.id === item.document)?.title ?? item.document} language={language} navigate={() => navigate(item)} preview={() => { previewFocus.current = document.activeElement as HTMLElement; setPreview(item); }}/>)}</ul>
    {data?.next_page && !error && <button disabled={loading} onClick={() => { setLoading(true); setPage(data.next_page!); }}>{en ? 'Load more' : 'Carregar mais'}</button>}
    {preview && <NotePreview source={preview.body ?? ''} language={language} context="annotations" close={() => { setPreview(null); requestAnimationFrame(() => previewFocus.current?.focus({ preventScroll: true })); }}/>}
  </div>;
}
