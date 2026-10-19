'use client';
import { useEffect, useRef, useState } from 'react';
import { ViewerDialog, ExpandIcon, MISSING_IMAGE } from './expandable-media';
import type { Language } from '../lib/i18n';

function HtmlFrame({ source, title }: { source: string; title: string }) {
  const frame = useRef<HTMLIFrameElement>(null);
  const [height, setHeight] = useState(160);
  useEffect(() => {
    const nonce = crypto.randomUUID();
    const missing = new URL(MISSING_IMAGE, location.origin).href;
    const receive = (event: MessageEvent) => {
      if (event.source === frame.current?.contentWindow && event.data?.nonce === nonce && Number.isFinite(event.data.height)) setHeight(Math.max(36, Math.min(1000, event.data.height)));
    };
    window.addEventListener('message', receive);
    // Only the bundled sizing/fallback script may execute. User scripts remain
    // disabled; the opaque origin has no storage or authenticated fetch access.
    frame.current!.srcdoc = `<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'nonce-${nonce}'; style-src 'unsafe-inline'; img-src https: http: data:; font-src https: data:; connect-src 'none'; frame-src 'none'; form-action 'none'; base-uri 'none'"><style>html,body{margin:0;color:#17334e;background:transparent;font:16px Georgia}img,svg{max-width:100%;height:auto}</style><script nonce="${nonce}">
      addEventListener('error', event => { const image=event.target;if(image.tagName==='IMG'&&!image.dataset.noteFailed){image.dataset.noteFailed='true';image.src=${JSON.stringify(missing)};image.alt='Image unavailable: '+image.alt;image.style.width='48px';image.style.height='36px';} },true);
      addEventListener('DOMContentLoaded',()=>{const report=()=>parent.postMessage({nonce:${JSON.stringify(nonce)},height:Math.ceil(document.body.getBoundingClientRect().height)},'*');new ResizeObserver(report).observe(document.body);report();});
    </script></head><body>${source}</body></html>`;
    return () => window.removeEventListener('message', receive);
  }, [source]);
  return <iframe ref={frame} title={title} sandbox="allow-scripts" referrerPolicy="no-referrer" className="note-html-frame" style={{ height }}/>;
}

/** Presentation is preserved; active embeds cannot acquire application privileges. */
export function NoteEmbed({ source, language }: { source: string; language: Language }) {
  const [open, setOpen] = useState(false);
  const en = language === 'en';
  const title = en ? 'Isolated HTML content' : 'Conteúdo HTML isolado';
  return <span className="note-html-embed"><HtmlFrame source={source} title={title}/><span className="media-controls"><button className="media-expand" aria-label={en ? 'Expand HTML' : 'Ampliar HTML'} onClick={() => setOpen(true)}><ExpandIcon/></button></span><small>{en ? 'Isolated preview. User scripts, embedded frames and network APIs are disabled.' : 'Prévia isolada. Scripts do conteúdo, frames incorporados e APIs de rede estão desativados.'}</small>{open && <ViewerDialog label={title} close={() => setOpen(false)}><button autoFocus onClick={() => setOpen(false)}>{en ? 'Close' : 'Fechar'}</button><HtmlFrame source={source} title={title}/></ViewerDialog>}</span>;
}
