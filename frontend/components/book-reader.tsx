'use client';
import { useEffect, useRef, useState, type ReactNode } from 'react';
import { paginateMeasured, type BookUnit } from '../lib/book-pagination';
import { contentPageId } from '../lib/manuscript';
import { ManuscriptDecorations } from './manuscript-decorations';
import { messages, type Language } from '../lib/i18n';
type Turn<T> = { direction: 1 | -1; from: T[][]; target: number };
/** One lifecycle and navigation engine; only CSS geometry and visible leaf count differ. */
export function BookReader<T extends BookUnit>({ units, renderUnit, project, language, title, header, location, locationRequest = 0, pageAction }: {
  units: readonly T[]; renderUnit: (unit: T) => ReactNode; project: string; language: Language; title: string; header?: ReactNode;
  location?: string; locationRequest?: number; pageAction?: (page: T[], physicalPage: number) => ReactNode;
}) {
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
  const count = mode === 'spread' ? 2 : 1;
  useEffect(() => {
    const node = measure.current;
    if (!node) return;
    let frame = 0; let disposed = false; let signature = '';
    measured.current = false;
    const calculate = () => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        if (disposed) return;
        // Keep the previous leaves while assets settle, but never publish their old total.
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
        const next = paginateMeasured(units, heights, page => nextMode === 'single-page' || page % 2 === 0 ? node.clientHeight : rightCapacity);
        const index = Math.max(0, next.findIndex(page => page.some(unit => unit.id === anchor.current)));
        if (timer.current) clearTimeout(timer.current);
        locked.current = false; setTurn(null); setMode(nextMode); setPages(next);
        setPosition(nextMode === 'spread' ? index - index % 2 : index);
        measured.current = true; setMeasurement({ units, language });
      });
    };
    const observer = new ResizeObserver(calculate);
    const mutations = new MutationObserver(calculate);
    mutations.observe(node, { subtree: true, childList: true, attributes: true, attributeFilter: ['data-measure-pending', 'src'] });
    observer.observe(node); if (measureRight.current) observer.observe(measureRight.current); Array.from(node.children).forEach(child => observer.observe(child));
    window.addEventListener('resize', calculate);
    node.addEventListener('load', calculate, true); node.addEventListener('error', calculate, true);
    document.fonts.addEventListener('loading', calculate);
    document.fonts.addEventListener('loadingdone', calculate);
    void document.fonts.ready.then(calculate); calculate();
    return () => { disposed = true; measured.current = false; cancelAnimationFrame(frame); observer.disconnect(); mutations.disconnect(); window.removeEventListener('resize', calculate); node.removeEventListener('load', calculate, true); node.removeEventListener('error', calculate, true); document.fonts.removeEventListener('loading', calculate); document.fonts.removeEventListener('loadingdone', calculate); if (timer.current) clearTimeout(timer.current); };
  }, [units, language]);
  const requested = useRef<{ location?: string; units: readonly T[]; request: number } | null>(null);
  useEffect(() => {
    if (!ready || !location || (requested.current?.location === location && requested.current.units === units && requested.current.request === locationRequest)) return;
    const index = pages.findIndex(page => page.some(unit => unit.id === location));
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
  function finish(target: number) {
    setPosition(target); anchor.current = pages[target]?.[0]?.id; setTurn(null); locked.current = false;
    if (timer.current) clearTimeout(timer.current);
    requestAnimationFrame(() => {
      if (focused.current && !focused.current.isConnected && document.activeElement === document.body) stage.current?.focus({ preventScroll: true });
      focused.current = null;
    });
  }
  function navigate(direction: 1 | -1) {
    if (locked.current || !ready || !measured.current) return;
    const target = position + direction * count;
    if (target < 0 || target >= pages.length) return;
    focused.current = document.activeElement instanceof HTMLElement && stage.current?.contains(document.activeElement) ? document.activeElement : null;
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) { finish(target); return; }
    locked.current = true; setTurn({ direction, from: pages.slice(position, position + count), target });
    timer.current = setTimeout(() => finish(target), 850);
  }
  const controls = <nav className="reader-controls" aria-label={language === 'en' ? 'Book pages' : 'Páginas do livro'}>
      <button aria-label={messages[language].previous} aria-disabled={!ready || !!turn || position === 0} onClick={() => navigate(-1)}>❮</button>
      <span aria-live="polite" aria-atomic="true">{ready ? `${messages[language].page} ${position + 1}${count === 2 && position + 1 < pages.length ? `–${position + 2}` : ''} ${messages[language].of} ${pages.length}` : language === 'en' ? 'Paginating…' : 'Paginando…'}</span>
      <button aria-label={messages[language].next} aria-disabled={!ready || !!turn || position + count >= pages.length} onClick={() => navigate(1)}>❯</button>
    </nav>;
  function leaf(page: T[] | undefined, key: string, side: 'left' | 'right', physicalPage = 0) {
    const identity = contentPageId((page ?? []).map(unit => unit.id));
    return <div className="reader-leaf paper manuscript-surface" key={key} data-page-id={identity}>
      <ManuscriptDecorations variant="reading" project={project} identity={identity}/>
      {side === 'left' && header}
      {page?.length && pageAction ? pageAction(page, physicalPage) : null}
      <div className="reader-body">{page?.map(unit => <div className="book-unit" data-unit-id={unit.id} key={unit.id}>{renderUnit(unit)}</div>)}</div>
      {(mode === 'single-page' || side === 'right') && controls}
    </div>;
  }
  const visible = turn ? turn.target : position;
  const front = turn ? turn.from[turn.direction === 1 && count === 2 ? 1 : 0] : undefined;
  const back = turn ? pages[turn.target + (turn.direction === -1 && count === 2 ? 1 : 0)] : undefined;
  const left = turn && count === 2 && turn.direction === 1 ? turn.from[0] : pages[visible];
  const right = turn && count === 2 && turn.direction === -1 ? turn.from[1] : pages[visible + 1];
  return <section className="reader" data-mode={mode} data-pagination={ready ? 'ready' : 'measuring'} aria-label={title} onKeyDown={event => {
    if (event.altKey || event.ctrlKey || event.metaKey || (event.target as HTMLElement).closest('input,textarea,select,[contenteditable]')) return;
    if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') { event.preventDefault(); navigate(event.key === 'ArrowRight' ? 1 : -1); }
  }} onTouchStart={event => { if (event.touches.length === 1 && !(event.target as HTMLElement).closest('a,button')) touch.current = { x: event.touches[0].clientX, y: event.touches[0].clientY }; }} onTouchEnd={event => {
    const start = touch.current; touch.current = null; if (!start || !event.changedTouches[0]) return;
    const dx = event.changedTouches[0].clientX - start.x; const dy = event.changedTouches[0].clientY - start.y;
    if (Math.abs(dx) > 65 && Math.abs(dx) > Math.abs(dy) * 2) navigate(dx < 0 ? 1 : -1);
  }}>
    <div className="reader-stage" ref={stage} tabIndex={-1} aria-busy={!ready || !!turn}>
      <div className="reader-pages">{leaf(left, 'left', 'left', visible + 1)}{mode === 'spread' && leaf(right, 'right', 'right', visible + 2)}</div>
      {turn && <div className={`turn-sheet turn-sheet--${turn.direction === 1 ? 'forward' : 'backward'}`} aria-hidden="true" inert onAnimationEnd={event => { if (event.target === event.currentTarget) finish(turn.target); }}>
        <div className="turn-face turn-front">{leaf(front, 'front', mode === 'spread' && turn.direction === 1 ? 'right' : 'left')}</div><div className="turn-face turn-back">{leaf(back, 'back', mode === 'spread' && turn.direction === -1 ? 'right' : 'left')}</div>
      </div>}
    </div>
    <div className="reader-measure" aria-hidden="true" inert>
      <div className="reader-leaf paper reader-probe reader-probe--left">{header}<div className="reader-body" ref={measure}>{units.map(unit => <div className="book-unit" key={unit.id}>{renderUnit(unit)}</div>)}</div><div className="reader-probe-controls">{controls}</div></div>
      <div className="reader-leaf paper reader-probe reader-probe--right"><div className="reader-body" ref={measureRight}/>{controls}</div>
    </div>

  </section>;
}
