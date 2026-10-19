/* eslint-disable @next/next/no-img-element */
'use client';

import { useEffect, useRef, useState, type ReactNode } from 'react';
import { createPortal } from 'react-dom';
import type { Language } from '../lib/i18n';

const labels = {
  en: { image: 'Expand image', diagram: 'Expand diagram', close: 'Close', in: 'Zoom in', out: 'Zoom out', reset: 'Reset zoom', failed: 'Unable to load image.', help: 'Drag to pan. Use the zoom buttons, mouse wheel or pinch gesture. Press Escape to close.' },
  'pt-BR': { image: 'Ampliar imagem', diagram: 'Ampliar diagrama', close: 'Fechar', in: 'Ampliar', out: 'Reduzir', reset: 'Restaurar zoom', failed: 'Não foi possível carregar a imagem.', help: 'Arraste para mover. Use os botões de zoom, a roda do mouse ou o gesto de pinça. Pressione Escape para fechar.' },
};

export function ExpandIcon() {
  return <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M8 3H3v5m0-5 7 7M16 3h5v5m0-5-7 7M3 16v5h5m-5 0 7-7m11 2v5h-5m5 0-7-7"/></svg>;
}

/** Shared native dialog lifecycle, focus containment and Escape behavior for all viewers. */
export function ViewerDialog({ label, close, children, className = '' }: { label: string; close: () => void; children: ReactNode; className?: string }) {
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => { const node = dialog.current!; node.showModal(); return () => node.close(); }, []);
  return <dialog ref={dialog} className={`media-viewer ${className}`} aria-label={label} aria-modal="true" onCancel={event => { event.preventDefault(); event.stopPropagation(); close(); }} onKeyDown={event => {
    if (event.target === event.currentTarget && ['ArrowDown', 'ArrowUp', 'PageDown', 'PageUp', 'Home', 'End', ' '].includes(event.key)) event.preventDefault();
    event.stopPropagation();
  }}>{children}</dialog>;
}

function diagramUrl(svg: string) {
  const document = new DOMParser().parseFromString(svg, 'image/svg+xml');
  const root = document.documentElement;
  const box = root.getAttribute('viewBox')?.trim().split(/[\s,]+/).map(Number);
  if (box?.length === 4 && box[2] > 0 && box[3] > 0) {
    root.setAttribute('width', String(box[2]));
    root.setAttribute('height', String(box[3]));
    root.style.maxWidth = 'none';
  }
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(new XMLSerializer().serializeToString(root))}`;
}

export function ExpandableMedia({ src, alt, svg, language, children }: { src?: string; alt: string; svg?: string; language: Language; children?: ReactNode }) {
  const [open, setOpen] = useState(false);
  const [failed, setFailed] = useState(false);
  const button = useRef<HTMLButtonElement>(null);
  const text = labels[language];
  return <span className="expandable-media">
    {children ?? (failed || !src ? <span role="status">{text.failed} {alt}</span> : <img src={src} alt={alt} loading="eager" onError={() => setFailed(true)}/>)}
    {(svg || (src && !failed)) && <span className="media-controls"><button ref={button} type="button" className="media-expand" aria-label={svg ? text.diagram : text.image} onClick={event => { event.preventDefault(); event.stopPropagation(); setOpen(true); }}><ExpandIcon/></button></span>}
    {open && createPortal(<FullscreenMediaViewer src={svg ? diagramUrl(svg) : src!} alt={alt} language={language} close={() => { setOpen(false); requestAnimationFrame(() => button.current?.focus({ preventScroll: true })); }}/>, document.body)}
  </span>;
}

function FullscreenMediaViewer({ src, alt, language, close }: { src: string; alt: string; language: Language; close: () => void }) {
  const stage = useRef<HTMLDivElement>(null);
  const media = useRef<HTMLImageElement>(null);
  const pointers = useRef(new Map<number, { x: number; y: number }>());
  const [failed, setFailed] = useState(false);
  const [view, setView] = useState({ scale: 1, x: 0, y: 0 });
  const text = labels[language];
  function constrain(scale: number, x: number, y: number) {
    const bounds = stage.current;
    const image = media.current;
    const limitX = Math.max(0, ((image?.offsetWidth ?? 0) * scale - (bounds?.clientWidth ?? 0)) / 2);
    const limitY = Math.max(0, ((image?.offsetHeight ?? 0) * scale - (bounds?.clientHeight ?? 0)) / 2);
    return { scale, x: Math.max(-limitX, Math.min(limitX, x)), y: Math.max(-limitY, Math.min(limitY, y)) };
  }
  function zoom(factor: number) {
    setView(current => constrain(Math.max(1, Math.min(8, current.scale * factor)), current.x, current.y));
  }
  useEffect(() => {
    const node = stage.current!.closest('dialog')!;
    const preventScroll = (event: Event) => event.preventDefault();
    // Keep the document's scrollbar and measurements unchanged while blocking scrolling.
    node.addEventListener('wheel', preventScroll, { passive: false });
    node.addEventListener('touchmove', preventScroll, { passive: false });
    const reset = () => setView({ scale: 1, x: 0, y: 0 });
    window.addEventListener('resize', reset);
    return () => {
      node.removeEventListener('wheel', preventScroll);
      node.removeEventListener('touchmove', preventScroll);
      window.removeEventListener('resize', reset);
    };
  }, []);
  return <ViewerDialog label={alt || text.image} close={close}>
    <div className="media-viewer-toolbar">
      <button type="button" aria-label={text.out} disabled={view.scale === 1} onClick={() => zoom(1 / 1.25)}>−</button>
      <output aria-live="polite">{Math.round(view.scale * 100)}%</output>
      <button type="button" aria-label={text.in} disabled={view.scale === 8} onClick={() => zoom(1.25)}>+</button>
      <button type="button" aria-label={text.reset} onClick={() => setView({ scale: 1, x: 0, y: 0 })}>↺</button>
      <button type="button" aria-label={text.close} autoFocus onClick={close}>×</button>
    </div>
    <p className="media-viewer-help">{text.help}</p>
    <div ref={stage} className="media-viewer-stage" data-zoom={view.scale} onWheel={event => zoom(Math.exp(-event.deltaY * .002))}
      onPointerDown={event => { if (event.pointerType === 'mouse' && event.button !== 0) return; event.currentTarget.setPointerCapture(event.pointerId); pointers.current.set(event.pointerId, { x: event.clientX, y: event.clientY }); }}
      onPointerMove={event => {
        const previous = pointers.current.get(event.pointerId);
        if (!previous) return;
        const next = { x: event.clientX, y: event.clientY };
        const other = [...pointers.current.entries()].find(([id]) => id !== event.pointerId)?.[1];
        if (other) {
          const before = Math.hypot(previous.x - other.x, previous.y - other.y);
          const after = Math.hypot(next.x - other.x, next.y - other.y);
          if (before > 0) zoom(after / before);
        } else setView(current => constrain(current.scale, current.x + next.x - previous.x, current.y + next.y - previous.y));
        pointers.current.set(event.pointerId, next);
      }} onPointerUp={event => pointers.current.delete(event.pointerId)} onPointerCancel={event => pointers.current.delete(event.pointerId)} onLostPointerCapture={event => pointers.current.delete(event.pointerId)}>
      {failed ? <p role="status">{text.failed}</p> : <img ref={media} src={src} alt={alt} draggable={false} onError={() => setFailed(true)} style={{ transform: `translate(${view.x}px, ${view.y}px) scale(${view.scale})` }}/>}
    </div>
  </ViewerDialog>;
}
