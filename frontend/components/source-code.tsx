'use client';
import { Fragment, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { createPortal } from 'react-dom';
import { ExpandIcon, ViewerDialog } from './expandable-media';
import { useHorizontalDrag } from './use-horizontal-drag';
import { useTableScroll } from './reader-table';
import { highlightedLines } from '../lib/syntax-highlight';
import { sourceLocation } from '../lib/source-links';
import type { MarkdownUnit } from '../lib/markdown';
function markedHtml(html: string, text: string, query: string): ReactNode {
  if (!query) return <span dangerouslySetInnerHTML={{ __html: html }}/>;
  // Highlight syntax tokens and search via text offsets, including matches crossing token boundaries.
  const starts: number[] = []; let at = 0;
  while ((at = text.toLowerCase().indexOf(query.toLowerCase(), at)) >= 0) { starts.push(at); at += query.length; }
  if (!starts.length) return <span dangerouslySetInnerHTML={{ __html: html }}/>;
  let position = 0;
  const marked = html.split(/(<[^>]+>)/).map(token => {
    if (token.startsWith('<')) return token;
    return token.split(/(&[a-z]+;|&#\d+;|&#x[a-f\d]+;|[^&])/i).filter(Boolean).map(character => {
      const match = starts.some(start => position >= start && position < start + query.length); position++;
      return match ? `<mark>${character}</mark>` : character;
    }).join('');
  }).join('');
  return <span dangerouslySetInnerHTML={{ __html: marked }}/>;
}
export function SourceCode({ unit, language, query, location, collapse }: { collapse?: () => void; location?: string; unit: MarkdownUnit; language: 'en' | 'pt-BR'; query: string }) {
  const ref = unit.code!; const all = useMemo(() => ref.lines ?? [], [ref.lines]);
  const lines = useMemo(() => highlightedLines(all.join('\n'), ref.language), [all, ref.language]);
  const part = unit.codePart ?? { start: 0, end: all.length };
  const origin = unit.codeOrigin ?? unit.id; const first = ref.start ?? 1;
  const en = language === 'en';
  const viewport = useRef<HTMLDivElement>(null);
  const button = useRef<HTMLButtonElement>(null);
  const [overflow, setOverflow] = useState(false);
  const [open, setOpen] = useState(false);
  const scroll = useTableScroll(`code/${origin}`);
  const { dragging, handlers } = useHorizontalDrag(overflow);
  useEffect(() => {
    const node = viewport.current;
    if (!node) return;
    const update = () => { setOverflow(node.scrollWidth > node.clientWidth + 1); node.scrollLeft = scroll.get(); };
    const observer = new ResizeObserver(update);
    observer.observe(node); if (node.firstElementChild) observer.observe(node.firstElementChild);
    update(); return () => observer.disconnect();
  }, [scroll, part.start, part.end]);
  const content = (start: number, end: number) => <pre><code>{all.slice(start, end).map((text, i) => <Fragment key={start + i}><span className="source-code-line" data-source-line={first + start + i} data-source-location={sourceLocation(ref, first + start + i)}><span className="source-code-number" aria-hidden="true">{first + start + i}</span><span data-code-text>{markedHtml(lines[start + i], text, !location || sourceLocation(ref, first + start + i) === location ? query : '')}</span></span></Fragment>)}</code></pre>;
  const reasons = { unapproved: en ? 'not approved for publication' : 'sem aprovação de publicação', missing: en ? 'file or snapshot unavailable' : 'arquivo ou snapshot indisponível', excluded: en ? 'excluded by source policy' : 'excluído pela política de fontes', 'revision-mismatch': en ? 'requested revision unavailable' : 'revisão solicitada indisponível', available: '' };
  if (ref.status !== 'available') return <p role="status" className="source-unavailable">{en ? 'Source unavailable' : 'Código indisponível'}: {ref.path} ({reasons[ref.status]}).</p>;
  return <div className="source-code-shell"><section className={`source-code${part.start ? ' source-code--continuation' : ''}`} data-source-code={origin} aria-label={`${ref.path}, ${first + part.start}–${first + part.end - 1}`}>
    <div className="source-code-header" data-source-header><span>{ref.path}</span><span>{part.start ? (en ? 'continued · ' : 'continuação · ') : ''}{first + part.start}–{first + part.end - 1}</span>{collapse && <button type="button" className="source-code-collapse" aria-label={en ? 'Collapse code' : 'Recolher código'} onClick={collapse}>▴</button>}</div>
    <div ref={viewport} {...handlers} data-overflow={overflow} data-dragging={dragging} onScroll={event => scroll.set(event.currentTarget.scrollLeft)} className="source-code-scroll" tabIndex={0} role="region" aria-label={en ? 'Source code, scroll horizontally' : 'Código-fonte, rolagem horizontal'} style={part.maxHeight ? { maxHeight: Math.max(1, part.maxHeight), overflowY: 'auto' } : undefined}>
      {content(part.start, part.end)}
    </div>
  </section>
    <div className="media-controls">
      {overflow && <span className="reader-table-hint" role="img" aria-label={en ? 'Drag code horizontally' : 'Arrastar código horizontalmente'} title={en ? 'Drag the line numbers or empty space. Select text directly; use arrow keys to scroll.' : 'Arraste pelos números de linha ou espaço vazio. Selecione o texto diretamente; use as setas para rolar.'}>↔</span>}
      <button ref={button} type="button" className="media-expand" aria-label={en ? 'Expand code' : 'Ampliar código'} onClick={() => setOpen(true)}><ExpandIcon/></button>
    </div>
    {open && createPortal(<CodeViewer en={en} path={ref.path} close={() => { setOpen(false); requestAnimationFrame(() => button.current?.focus({ preventScroll: true })); }}>{content(0, all.length)}</CodeViewer>, document.body)}
  </div>;
}

export function CodeViewer({ children, en, path, close }: { children: ReactNode; en: boolean; path: string; close: () => void }) {
  const [zoom, setZoom] = useState(1);
  return <ViewerDialog label={path} close={close} className="code-viewer">
    <div className="media-viewer-toolbar">
      <button aria-label={en ? 'Zoom out' : 'Reduzir'} disabled={zoom <= .5} onClick={() => setZoom(Math.max(.5, zoom / 1.25))}>−</button>
      <output aria-live="polite">{Math.round(zoom * 100)}%</output>
      <button aria-label={en ? 'Zoom in' : 'Ampliar'} disabled={zoom >= 3} onClick={() => setZoom(Math.min(3, zoom * 1.25))}>+</button>
      <button aria-label={en ? 'Reset zoom' : 'Restaurar zoom'} onClick={() => setZoom(1)}>↺</button>
      <button aria-label={en ? 'Close viewer' : 'Fechar visualização'} autoFocus onClick={close}>×</button>
    </div>
    <p className="media-viewer-help">{path}</p>
    <div className="code-viewer-scroll" tabIndex={0} role="region" aria-label={en ? 'Source code, scroll horizontally and vertically' : 'Código-fonte, rolagem horizontal e vertical'}><div className="source-code" style={{ zoom }}>{children}</div></div>
  </ViewerDialog>;
}
