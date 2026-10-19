'use client';
import { useRouter } from 'next/navigation';
import { Fragment, useEffect, useRef, useState, type ReactNode } from 'react';
import { paginateMeasured, type BookUnit } from '../lib/book-pagination';
import { containsLocation, type TableMeasurement } from '../lib/table-pagination';
import { contentPageId } from '../lib/manuscript';
import { TableScrollProvider } from './reader-table';
import { ManuscriptDecorations } from './manuscript-decorations';
import { messages, type Language } from '../lib/i18n';
type Turn<T> = { direction: 1 | -1; from: T[][]; target: number; href?: string };
/** One lifecycle and navigation engine; only CSS geometry and visible leaf count differ. */
export function BookReader<T extends BookUnit>({ units, renderUnit, project, language, title, header, location, locationRequest = 0, pageAction, previousChapter, nextChapter, previousIsContents, initialEnd = false }: {
  previousChapter?: string; nextChapter?: string; previousIsContents?: boolean; initialEnd?: boolean;
  units: readonly T[]; renderUnit: (unit: T) => ReactNode; project: string; language: Language; title: string; header?: ReactNode | ((action: ReactNode) => ReactNode);
  location?: string; locationRequest?: number; pageAction?: (page: T[], physicalPage: number) => ReactNode;
}) {
  const router = useRouter();
  const routed = useRef(false);
  const [departing, setDeparting] = useState(false);
  const endPending = useRef(initialEnd);
  const [pages, setPages] = useState<T[][]>([[...units]]);
  const [mode, setMode] = useState<'spread' | 'single-page'>('single-page');
  const [position, setPosition] = useState(0);
  const [turn, setTurn] = useState<Turn<T> | null>(null);
  const [measurement, setMeasurement] = useState<{ units: readonly T[]; language: Language } | null>(null);
  const ready = measurement?.units === units && measurement.language === language;
  const measured = useRef(false);
  const measure = useRef<HTMLDivElement>(null);
  const measureRight = useRef<HTMLDivElement>(null);
  const stage = useRef<HTMLDivElement>(null);
  const focused = useRef<HTMLElement | null>(null);
  const anchor = useRef(units[0]?.id);
  const locked = useRef(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const touch = useRef<{ x: number; y: number } | null>(null);
  useEffect(() => {
    if (previousChapter) router.prefetch(previousChapter);
    if (nextChapter) router.prefetch(nextChapter);
  }, [router, previousChapter, nextChapter]);
  const count = mode === 'spread' ? 2 : 1;
  useEffect(() => {
    const node = measure.current;
    if (!node) return;
    let frame = 0; let disposed = false; let signature = '';
    let rowSignature = ''; let tableMeasurements = new Map<number, TableMeasurement>();
    measured.current = false;
    const historyLocation = window.history.state?.bookLocation;
    if (historyLocation?.url === window.location.href && units.some(unit => unit.id === historyLocation.anchor || historyLocation.anchor?.startsWith(`${unit.id}--row-`))) {
      anchor.current = historyLocation.anchor;
      endPending.current = false;
    }
    const calculate = () => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        if (disposed || routed.current) return;
        // Do not publish physical page totals until the destination assets settle.
        if (document.fonts.status === 'loading' || node.querySelector('[data-measure-pending="true"]') || Array.from(node.querySelectorAll('img')).some(image => !image.complete)) {
          measured.current = false; setMeasurement(null); return;
        }
        const nextMode = matchMedia('(min-width: 921px)').matches ? 'spread' : 'single-page';
        const heights = Array.from(node.children).map(child => child.getBoundingClientRect().height);
        const rightCapacity = measureRight.current?.clientHeight ?? node.clientHeight;
        if (node.clientHeight <= 0 || (nextMode === 'spread' && rightCapacity <= 0)) {
          measured.current = false; setMeasurement(null); return;
        }
        const nextSignature = JSON.stringify([nextMode, node.clientWidth, node.clientHeight, rightCapacity, heights]);
        // Control updates and identical observer notifications must not restart a turn.
        if (signature === nextSignature && measured.current) return;
        signature = nextSignature;
        const nextRowSignature = JSON.stringify([node.clientWidth, heights]);
        if (rowSignature !== nextRowSignature) {
          tableMeasurements = new Map<number, TableMeasurement>();
          rowSignature = nextRowSignature;
          Array.from(node.children).forEach((child, index) => {
            const table = child.querySelector('table');
            if (!table) return;
            const rows = Array.from(table.tBodies).flatMap(body => Array.from(body.rows));
            const header = table.tHead?.getBoundingClientRect().height ?? 0;
            const rowHeights = rows.map(row => row.getBoundingClientRect().height);
            tableMeasurements.set(index, { rows: rowHeights, header, overhead: Math.max(0, heights[index] - header - rowHeights.reduce((a, b) => a + b, 0)) + 2,
              widths: Array.from(table.rows[0]?.cells ?? []).map(cell => cell.getBoundingClientRect().width),
              safe: table.dataset.rowPagination === 'true' && !!table.tHead && !table.querySelector('[rowspan], [colspan]') });
          });
        }
        const next = paginateMeasured(units, heights, page => nextMode === 'single-page' || page % 2 === 0 ? node.clientHeight : rightCapacity, tableMeasurements);
        const index = endPending.current ? next.length - 1 : Math.max(0, next.findIndex(page => page.some(unit => containsLocation(unit, anchor.current))));
        endPending.current = false;
        anchor.current = next[index]?.[0]?.id;
        if (timer.current) clearTimeout(timer.current);
        locked.current = false; setTurn(null); setMode(nextMode); setPages(next);
        setPosition(nextMode === 'spread' ? index - index % 2 : index);
        measured.current = true; setMeasurement({ units, language });
      });
    };
    const invalidate = () => { signature = ''; rowSignature = ''; calculate(); };
    const observer = new ResizeObserver(calculate);
    const mutations = new MutationObserver(calculate);
    mutations.observe(node, { subtree: true, childList: true, attributes: true, attributeFilter: ['data-measure-pending', 'src'] });
    observer.observe(node); if (measureRight.current) observer.observe(measureRight.current); Array.from(node.children).forEach(child => observer.observe(child));
    window.addEventListener('resize', calculate);
    node.addEventListener('load', invalidate, true); node.addEventListener('error', invalidate, true);
    document.fonts.addEventListener('loading', invalidate);
    document.fonts.addEventListener('loadingdone', invalidate);
    void document.fonts.ready.then(calculate); calculate();
    return () => { disposed = true; measured.current = false; cancelAnimationFrame(frame); observer.disconnect(); mutations.disconnect(); window.removeEventListener('resize', calculate); node.removeEventListener('load', invalidate, true); node.removeEventListener('error', invalidate, true); document.fonts.removeEventListener('loading', invalidate); document.fonts.removeEventListener('loadingdone', invalidate); if (timer.current) clearTimeout(timer.current); };
  }, [units, language]);
  const requested = useRef<{ location?: string; units: readonly T[]; request: number } | null>(null);
  useEffect(() => {
    if (!ready || !location || (requested.current?.location === location && requested.current.units === units && requested.current.request === locationRequest)) return;
    const index = pages.findIndex(page => page.some(unit => containsLocation(unit, location)));
    if (index < 0) return;
    let scrollFrame = 0;
    const frame = requestAnimationFrame(() => {
      requested.current = { location, units, request: locationRequest };
      if (timer.current) clearTimeout(timer.current);
      locked.current = false; setTurn(null); anchor.current = location;
      setPosition(mode === 'spread' ? index - index % 2 : index);
      scrollFrame = requestAnimationFrame(() => {
        const block = Array.from(stage.current?.querySelectorAll<HTMLElement>('[data-unit-id]') ?? []).find(node => node.dataset.unitId === location);
        if (block?.parentElement) block.parentElement.scrollTop = block.offsetTop;
      });
    });
    return () => { cancelAnimationFrame(frame); cancelAnimationFrame(scrollFrame); };
  }, [ready, location, locationRequest, units, pages, mode]);
  function finish(target: number, href?: string) {
    if (href) {
      if (routed.current) return;
      routed.current = true;
      setDeparting(true);
      locked.current = true;
      if (timer.current) clearTimeout(timer.current);
      router.push(href, { scroll: false });
      return;
    }
    window.history.replaceState({ ...window.history.state, bookLocation: { url: window.location.href, anchor: pages[target]?.[0]?.id } }, '');
    setPosition(target); anchor.current = pages[target]?.[0]?.id; setTurn(null); locked.current = false;
    if (timer.current) clearTimeout(timer.current);
    requestAnimationFrame(() => {
      if (focused.current && !focused.current.isConnected && document.activeElement === document.body) stage.current?.focus({ preventScroll: true });
      focused.current = null;
    });
  }
  function navigate(direction: 1 | -1) {
    if (locked.current || !ready || !measured.current) return;
    const candidate = position + direction * count;
    const boundary = candidate < 0 || candidate >= pages.length;
    const href = boundary ? (direction === 1 ? nextChapter : previousChapter) : undefined;
    if (boundary && !href) return;
    const target = boundary ? position : candidate;
    if (href) window.history.replaceState({ ...window.history.state, bookLocation: { url: window.location.href, anchor: pages[position]?.[0]?.id } }, '');
    focused.current = document.activeElement instanceof HTMLElement && stage.current?.contains(document.activeElement) ? document.activeElement : null;
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) { finish(target, href); return; }
    locked.current = true; setTurn({ direction, from: pages.slice(position, position + count), target, href });
    // Move focus out before its page becomes inert and hidden from assistive technology.
    if (focused.current) stage.current?.focus({ preventScroll: true });
    timer.current = setTimeout(() => finish(target, href), 850);
  }
  const previousBoundary = position === 0 && !!previousChapter;
  const nextBoundary = position + count >= pages.length && !!nextChapter;
  const previousLabel = previousBoundary ? (previousIsContents ? (language === 'en' ? 'Back to Table of Contents' : 'Voltar ao sumário') : (language === 'en' ? 'Previous chapter' : 'Capítulo anterior')) : messages[language].previous;
  const nextLabel = nextBoundary ? (language === 'en' ? 'Next chapter' : 'Próximo capítulo') : messages[language].next;
  function boundaryIcon(direction: 1 | -1) {
    return <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true"><path d={direction === 1 ? 'M5 4v16M9 5l10 7-10 7Z' : 'M19 4v16M15 5 5 12l10 7Z'}/></svg>;
  }
  const controls = <nav className="reader-controls" aria-label={language === 'en' ? 'Book pages' : 'Páginas do livro'}>
      <button title={previousLabel} aria-label={previousLabel} aria-disabled={!ready || !!turn || departing || (position === 0 && !previousChapter)} onClick={() => navigate(-1)}>{previousBoundary ? boundaryIcon(-1) : '❮'}</button>
      <span aria-live="polite" aria-atomic="true">{ready ? `${messages[language].page} ${position + 1}${count === 2 && position + 1 < pages.length ? `–${position + 2}` : ''} ${messages[language].of} ${pages.length}` : language === 'en' ? 'Paginating…' : 'Paginando…'}</span>
      <button title={nextLabel} aria-label={nextLabel} aria-disabled={!ready || !!turn || departing || (position + count >= pages.length && !nextChapter)} onClick={() => navigate(1)}>{nextBoundary ? boundaryIcon(1) : '❯'}</button>
    </nav>;
  function leaf(page: T[] | undefined, key: string, side: 'left' | 'right', physicalPage = 0, concealed = false) {
    const identity = contentPageId((page ?? []).map(unit => unit.id));
    return <div className="reader-leaf paper manuscript-surface" key={key} data-page-controls={pageAction && (side !== 'left' || typeof header !== 'function') ? 'standalone' : undefined} data-page-id={identity} data-content-concealed={concealed || undefined} aria-hidden={concealed || undefined} inert={concealed || undefined}>
      <ManuscriptDecorations variant="reading" project={project} identity={identity}/>
      {/* Give the externally owned header its own stable sibling boundary. */}
      {side === 'left' && <Fragment key="header">{typeof header === 'function' ? header(page?.length && pageAction ? pageAction(page, physicalPage) : null) : header}</Fragment>}
      {(side !== 'left' || typeof header !== 'function') && page?.length && pageAction ? pageAction(page, physicalPage) : null}
      <div className="reader-body">{!ready && <p role="status">{language === 'en' ? 'Paginating…' : 'Paginando…'}</p>}{page?.map(unit => <div className="book-unit" data-unit-id={unit.id} key={unit.id}>{renderUnit(unit)}</div>)}</div>
      {(mode === 'single-page' || side === 'right') && controls}
    </div>;
  }
  const visible = turn ? turn.target : position;
  const front = turn ? turn.from[turn.direction === 1 && count === 2 ? 1 : 0] : undefined;
  const back = turn ? pages[turn.target + (turn.direction === -1 && count === 2 ? 1 : 0)] : undefined;
  const left = turn && count === 2 && turn.direction === 1 ? turn.from[0] : pages[visible];
  const right = turn && count === 2 && turn.direction === -1 ? turn.from[1] : pages[visible + 1];
  return <TableScrollProvider><section className="reader" data-mode={mode} data-pagination={ready ? 'ready' : 'measuring'} aria-label={title} onKeyDown={event => {
    if (event.altKey || event.ctrlKey || event.metaKey || (event.target as HTMLElement).closest('input,textarea,select,[contenteditable],.reader-table,dialog')) return;
    if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') { event.preventDefault(); navigate(event.key === 'ArrowRight' ? 1 : -1); }
  }} onTouchStart={event => { if (event.touches.length === 1 && !(event.target as HTMLElement).closest('a,button,.reader-table,dialog')) touch.current = { x: event.touches[0].clientX, y: event.touches[0].clientY }; }} onTouchEnd={event => {
    const start = touch.current; touch.current = null; if (!start || !event.changedTouches[0]) return;
    const dx = event.changedTouches[0].clientX - start.x; const dy = event.changedTouches[0].clientY - start.y;
    if (Math.abs(dx) > 65 && Math.abs(dx) > Math.abs(dy) * 2) navigate(dx < 0 ? 1 : -1);
  }}>
    <div className="reader-stage" ref={stage} tabIndex={-1} aria-busy={!ready || !!turn || departing}>
      <div className="reader-pages">{leaf(ready ? left : undefined, 'left', 'left', visible + 1, !!turn && (count === 1 || turn.direction === -1))}{mode === 'spread' && leaf(ready ? right : undefined, 'right', 'right', visible + 2, !!turn && turn.direction === 1)}</div>
      {turn && <div className={`turn-sheet turn-sheet--${turn.direction === 1 ? 'forward' : 'backward'}`} aria-hidden="true" inert onAnimationEnd={event => { if (event.target === event.currentTarget) finish(turn.target, turn.href); }}>
        <div className="turn-face turn-front">{leaf(front, 'front', mode === 'spread' && turn.direction === 1 ? 'right' : 'left', 0, true)}</div><div className="turn-face turn-back">{leaf(back, 'back', mode === 'spread' && turn.direction === -1 ? 'right' : 'left', 0, true)}</div>
      </div>}
    </div>
    <div className="reader-measure" aria-hidden="true" inert>
      <div className="reader-leaf paper reader-probe reader-probe--left" data-page-controls={pageAction && typeof header !== 'function' ? 'standalone' : undefined}><Fragment key="header">{typeof header === 'function' ? header(null) : header}</Fragment><div className="reader-body" ref={measure}>{units.map(unit => <div className="book-unit" key={unit.id}>{renderUnit(unit)}</div>)}</div><div className="reader-probe-controls">{controls}</div></div>
      <div className="reader-leaf paper reader-probe reader-probe--right" data-page-controls={pageAction ? 'standalone' : undefined}><div className="reader-body" ref={measureRight}/>{controls}</div>
    </div>

  </section></TableScrollProvider>;
}
