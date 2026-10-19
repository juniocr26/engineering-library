/* eslint-disable @next/next/no-img-element */
'use client';

import { useEffect, useRef, useState, type ReactNode } from 'react';
import { createPortal } from 'react-dom';
import type { Language } from '../lib/i18n';

const labels = {
  en: { image: 'Expand image', diagram: 'Expand diagram', close: 'Close', in: 'Zoom in', out: 'Zoom out', reset: 'Reset zoom', failed: 'Unable to load image.', help: 'Drag to pan. Use the zoom buttons, mouse wheel or pinch gesture. Press Escape to close.' },
  'pt-BR': { image: 'Ampliar imagem', diagram: 'Ampliar diagrama', close: 'Fechar', in: 'Ampliar', out: 'Reduzir', reset: 'Restaurar zoom', failed: 'Não foi possível carregar a imagem.', help: 'Arraste para mover. Use os botões de zoom, a roda do mouse ou o gesto de pinça. Pressione Escape para fechar.' },
};

export const MISSING_IMAGE = '/assets/image-missing.svg';
export function MissingImage({ alt, message }: { alt: string; message: string }) {
  return <img className="missing-image" src={MISSING_IMAGE} width={48} height={36} alt={`${message}${alt ? ` ${alt}` : ''}`} title={alt || message}/>;
}

export function ExpandIcon() {
  return <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M8 3H3v5m0-5 7 7M16 3h5v5m0-5-7 7M3 16v5h5m-5 0 7-7m11 2v5h-5m5 0-7-7"/></svg>;
}

/** Shared native dialog lifecycle, focus containment and Escape behavior for all viewers. */
export function ViewerDialog({ label, close, children, className = '' }: { label: string; close: () => void; children: ReactNode; className?: string }) {
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const node = dialog.current!;
    node.showModal();
    const viewport = window.visualViewport;
    const resize = () => {
      node.style.setProperty('--viewer-visible-height', `${viewport?.height ?? innerHeight}px`);
      node.style.setProperty('--viewer-visible-top', `${viewport?.offsetTop ?? 0}px`);
    };
    resize();
    viewport?.addEventListener('resize', resize);
    viewport?.addEventListener('scroll', resize);
    return () => { viewport?.removeEventListener('resize', resize); viewport?.removeEventListener('scroll', resize); node.close(); };
  }, []);
  return <dialog ref={dialog} className={`media-viewer ${className}`} aria-label={label} aria-modal="true" onCancel={event => { event.preventDefault(); event.stopPropagation(); close(); }} onKeyDown={event => {
    if (event.target === event.currentTarget && ['ArrowDown', 'ArrowUp', 'PageDown', 'PageUp', 'Home', 'End', ' '].includes(event.key)) event.preventDefault();
    event.stopPropagation();
  }}>{children}</dialog>;
}

/** Shared multiplicative zoom limits for image and text viewers. */
export function viewerZoom(scale: number, factor: number, minimum = 1, maximum = 8) {
  return Math.max(minimum, Math.min(maximum, scale * factor));
}

/** Shared pointer delta/pinch math; each viewer keeps its own selection policy. */
export function viewerPointerMove(pointers: Map<number, { x: number; y: number }>, id: number, next: { x: number; y: number }) {
  const previous = pointers.get(id);
  if (!previous) return;
  const other = [...pointers.entries()].find(([key]) => key !== id)?.[1];
  pointers.set(id, next);
  if (other) {
    const before = Math.hypot(previous.x - other.x, previous.y - other.y);
    return { factor: before ? Math.hypot(next.x - other.x, next.y - other.y) / before : 1, x: 0, y: 0 };
  }
  return { factor: 1, x: next.x - previous.x, y: next.y - previous.y };
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

export function ExpandableMedia({ src, alt, svg, language, children, width, height, title }: { width?: number | string; height?: number | string; title?: string; src?: string; alt: string; svg?: string; language: Language; children?: ReactNode }) {
  const [open, setOpen] = useState(false);
  const [failedSource, setFailedSource] = useState<string>();
  const failed = !!src && failedSource === src;
  const button = useRef<HTMLButtonElement>(null);
  const text = labels[language];
  return <span className="expandable-media">
    {children ?? (failed || !src ? <MissingImage alt={alt} message={text.failed}/> : <img src={src} alt={alt} width={width} height={height} title={title} loading="eager" onError={() => setFailedSource(src)}/>)}
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
    setView(current => constrain(viewerZoom(current.scale, factor), current.x, current.y));
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
        const delta = viewerPointerMove(pointers.current, event.pointerId, { x: event.clientX, y: event.clientY });
        if (!delta) return;
        if (delta.factor !== 1) zoom(delta.factor);
        else setView(current => constrain(current.scale, current.x + delta.x, current.y + delta.y));
      }} onPointerUp={event => pointers.current.delete(event.pointerId)} onPointerCancel={event => pointers.current.delete(event.pointerId)} onLostPointerCapture={event => pointers.current.delete(event.pointerId)}>
      {failed ? <MissingImage alt={alt} message={text.failed}/> : <img ref={media} src={src} alt={alt} draggable={false} onError={() => setFailed(true)} style={{ transform: `translate(${view.x}px, ${view.y}px) scale(${view.scale})` }}/>}
    </div>
  </ViewerDialog>;
}
