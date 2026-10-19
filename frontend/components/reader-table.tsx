'use client';
import { createContext, useContext, useEffect, useId, useMemo, useRef, useState, type ReactNode } from 'react';
import { createPortal } from 'react-dom';
import { ExpandIcon, ViewerDialog } from './expandable-media';
import type { Language } from '../lib/i18n';
import type { TablePart } from '../lib/table-pagination';

const ScrollContext = createContext<Map<string, { left: number }> | null>(null);
export function TableScrollProvider({ children }: { children: ReactNode }) {
  const [cache] = useState(() => new Map<string, { left: number }>());
  useEffect(() => { const reset = () => cache.forEach(value => { value.left = 0; }); window.addEventListener('resize', reset); return () => window.removeEventListener('resize', reset); }, [cache]);
  return <ScrollContext.Provider value={cache}>{children}</ScrollContext.Provider>;
}
export function useTableScroll(key: string) {
  const cache = useContext(ScrollContext);
  const [local] = useState(() => new Map<string, { left: number }>());
  return useMemo(() => ({ get: () => (cache ?? local).get(key)?.left ?? 0, set: (left: number) => { (cache ?? local).set(key, { left }); } }), [cache, local, key]);
}

/** Native scrolling remains available to touch, wheel, keyboard and assistive technology. */
export function ReaderTable({ children, fullTable, part, language, scroll, canSplit }: { children: ReactNode; canSplit: boolean; fullTable: () => ReactNode; part?: TablePart; language: Language; scroll: { get: () => number; set: (left: number) => void } }) {
  const helpId = useId();
  const viewport = useRef<HTMLDivElement>(null);
  const button = useRef<HTMLButtonElement>(null);
  const drag = useRef<{ x: number; left: number; active: boolean } | null>(null);
  const [overflow, setOverflow] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [open, setOpen] = useState(false);
  const en = language === 'en';
  const help = en ? 'Scroll for more columns. Drag horizontally or use arrow keys.' : 'Role para ver mais colunas. Arraste horizontalmente ou use as setas.';
  useEffect(() => {
    const node = viewport.current!;
    const update = () => { setOverflow(node.scrollWidth > node.clientWidth + 1); node.scrollLeft = scroll.get(); };
    const observer = new ResizeObserver(update); observer.observe(node); observer.observe(node.querySelector('table')!); update();
    return () => observer.disconnect();
  }, [scroll]);
  return <div className="reader-table-shell" style={part?.maxHeight ? { height: part.maxHeight } : undefined}>
    <button ref={button} className="media-expand" type="button" aria-label={en ? 'Expand table' : 'Ampliar tabela'} onClick={event => { event.stopPropagation(); setOpen(true); }}><ExpandIcon/></button>
    <div ref={viewport} className="reader-table" role="region" aria-describedby={helpId} aria-label={en ? 'Documentation table' : 'Tabela da documentação'} tabIndex={0} data-overflow={overflow} data-dragging={dragging}
      style={part?.maxHeight ? { maxHeight: part.maxHeight } : undefined}
      onScroll={event => { scroll.set(event.currentTarget.scrollLeft); }}
      onPointerDown={event => { if (overflow && event.pointerType === 'mouse' && event.button === 0 && !(event.target as HTMLElement).closest('a,button,input')) drag.current = { x: event.clientX, left: event.currentTarget.scrollLeft, active: false }; }}
      onPointerMove={event => { const current = drag.current; if (!current) return; if (!current.active && Math.abs(event.clientX - current.x) > 6) { current.active = true; setDragging(true); event.currentTarget.setPointerCapture(event.pointerId); } if (current.active) { event.preventDefault(); event.currentTarget.scrollLeft = current.left + current.x - event.clientX; } }}
      onPointerLeave={() => { if (!drag.current?.active) drag.current = null; }}
      onPointerUp={() => { drag.current = null; setDragging(false); }} onPointerCancel={() => { drag.current = null; setDragging(false); }} onLostPointerCapture={() => { drag.current = null; setDragging(false); }} onKeyDown={event => event.stopPropagation()}>
      <table data-row-pagination={canSplit} style={part?.widths.length ? { width: part.widths.reduce((a, b) => a + b, 0), tableLayout: 'fixed' } : undefined}>
        {part?.widths.length ? <colgroup>{part.widths.map((width, index) => <col key={index} style={{ width }}/>)}</colgroup> : null}{children}
      </table>
    </div>
    {overflow && <span className="reader-table-hint" aria-hidden="true">↔</span>}
    <span id={helpId} className="sr-only">{overflow ? help : ''}{part?.maxHeight ? (en ? ' Scroll vertically to read the complete row or expand the table.' : ' Role verticalmente para ler a linha completa ou amplie a tabela.') : ''}</span>
    {open && createPortal(<TableViewer language={language} close={() => { setOpen(false); requestAnimationFrame(() => button.current?.focus({ preventScroll: true })); }}>{fullTable()}</TableViewer>, document.body)}
  </div>;
}
function TableViewer({ children, language, close }: { children: ReactNode; language: Language; close: () => void }) {
  const [zoom, setZoom] = useState(1);
  const en = language === 'en';
  return <ViewerDialog label={en ? 'Complete table' : 'Tabela completa'} close={close} className="table-viewer">
    <div className="media-viewer-toolbar">
      <button aria-label={en ? 'Zoom out' : 'Reduzir'} disabled={zoom <= .5} onClick={() => setZoom(Math.max(.5, zoom / 1.25))}>−</button>
      <output aria-live="polite">{Math.round(zoom * 100)}%</output>
      <button aria-label={en ? 'Zoom in' : 'Ampliar'} disabled={zoom >= 3} onClick={() => setZoom(Math.min(3, zoom * 1.25))}>+</button>
      <button aria-label={en ? 'Reset zoom' : 'Restaurar zoom'} onClick={() => setZoom(1)}>↺</button>
      <button aria-label={en ? 'Close' : 'Fechar'} autoFocus onClick={close}>×</button>
    </div>
    <p className="media-viewer-help">{en ? 'Scroll horizontally and vertically. Press Escape to close.' : 'Role horizontalmente e verticalmente. Pressione Escape para fechar.'}</p>
    <div className="table-viewer-scroll" tabIndex={0} role="region" aria-label={en ? 'Scrollable table' : 'Tabela rolável'}><div style={{ zoom }}>{children}</div></div>
  </ViewerDialog>;
}
