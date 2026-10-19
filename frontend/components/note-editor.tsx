'use client';
import { useEffect, useRef, useState } from 'react';
import { ViewerDialog } from './expandable-media';
import { NoteMarkdown } from './note-markdown';
import { NOTE_MAX_BYTES } from '../lib/note-policy';
import type { TextAnchor } from '../lib/text-anchors';
import type { Language } from '../lib/i18n';
export type SavedNote = { id: number; highlight_id: number | null; segments: TextAnchor[]; body: string };
export function NoteEditor({ note, highlightId, query, csrf, language, saved, removed, close }: { note?: SavedNote; highlightId?: number; query: string; csrf: string; language: Language; saved: (note: SavedNote) => void; removed: (id: number) => void; close: () => void }) {
  const [current, setCurrent] = useState(note);
  const [draft, setDraft] = useState(note?.body ?? '');
  const [preview, setPreview] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const editor = useRef<HTMLTextAreaElement>(null);
  const en = language === 'en';
  const dirty = draft !== (current?.body ?? '');
  const finish = () => { if (!dirty || confirm(en ? 'Discard unsaved changes?' : 'Descartar alterações não salvas?')) close(); };
  useEffect(() => { const prevent = (event: BeforeUnloadEvent) => { if (dirty) event.preventDefault(); }; window.addEventListener('beforeunload', prevent); return () => window.removeEventListener('beforeunload', prevent); }, [dirty]);
  async function mutate(remove = false) {
    if (busy) return;
    if (remove && (draft.trim() || current?.body.trim()) && !confirm(en ? 'Delete this note? The highlight will remain.' : 'Excluir esta nota? O destaque será preservado.')) return;
    setBusy(true); setMessage('');
    try {
      const response = await fetch(`/api/notes${current ? `/${current.id}` : ''}?${query}`, { method: remove ? 'DELETE' : current ? 'PATCH' : 'POST', headers: { 'Content-Type': 'application/json', 'X-Reader-CSRF': csrf }, body: remove ? undefined : JSON.stringify({ highlight_id: highlightId, body: draft }) });
      if (!response.ok) throw Error();
      if (remove) { removed(current!.id); close(); }
      else { const value = await response.json(); setCurrent(value); setDraft(value.body); saved(value); setMessage(en ? 'Note saved.' : 'Nota salva.'); }
    } catch { setMessage(en ? 'Could not save. Your draft is preserved. Maximum: 128 KiB.' : 'Não foi possível salvar. Seu rascunho foi preservado. Máximo: 128 KiB.'); }
    finally { setBusy(false); }
  }
  const bytes = new TextEncoder().encode(draft).length;
  return <ViewerDialog label={en ? 'Note editor' : 'Editor de nota'} close={() => { if (!busy) finish(); }} className="note-editor">
    <header><h2>{en ? 'Passage note' : 'Nota do trecho'}</h2><button disabled={busy} onClick={finish} aria-label={en ? 'Close note' : 'Fechar nota'}>×</button></header>
    <label htmlFor="note-draft">{en ? 'Markdown or plain text' : 'Markdown ou texto simples'}</label>
    <textarea id="note-draft" ref={editor} autoFocus value={draft} onChange={event => setDraft(event.target.value)} spellCheck/>
    <p role="status">{message || `${bytes.toLocaleString()} / 131.072 bytes`}</p>
    <footer><button disabled={busy || !current} onClick={() => void mutate(true)}>{en ? 'Delete note' : 'Excluir nota'}</button><button disabled={busy} onClick={() => setPreview(true)}>{en ? 'Preview' : 'Pré-visualizar'}</button><button disabled={busy || bytes > NOTE_MAX_BYTES} onClick={() => void mutate()}>{en ? 'Save' : 'Salvar'}</button></footer>
    {preview && <NotePreview source={draft} language={language} close={() => { setPreview(false); requestAnimationFrame(() => editor.current?.focus({ preventScroll: true })); }}/>}
  </ViewerDialog>;
}
function NotePreview({ source, language, close }: { source: string; language: Language; close: () => void }) {
  const [zoom, setZoom] = useState(1);
  const pan = useRef<{ x: number; y: number; left: number; top: number } | null>(null);
  const en = language === 'en';
  return <ViewerDialog label={en ? 'Note preview' : 'Prévia da nota'} close={close} className="note-preview">
    <div className="media-viewer-toolbar"><button aria-label={en ? 'Zoom out' : 'Reduzir'} onClick={() => setZoom(Math.max(.75, zoom / 1.25))}>−</button><output>{Math.round(zoom * 100)}%</output><button aria-label={en ? 'Zoom in' : 'Ampliar'} onClick={() => setZoom(Math.min(3, zoom * 1.25))}>+</button><button onClick={() => setZoom(1)}>{en ? 'Reset zoom' : 'Restaurar zoom'}</button><button autoFocus onClick={close}>{en ? 'Return to edit' : 'Voltar à edição'}</button></div>
    <div className="note-preview-scroll" tabIndex={0} onPointerDown={event => {
      if (zoom <= 1 || (event.target as Element).closest('a,button,table,pre') || event.pointerType !== 'mouse') return;
      pan.current = { x: event.clientX, y: event.clientY, left: event.currentTarget.scrollLeft, top: event.currentTarget.scrollTop }; event.currentTarget.setPointerCapture(event.pointerId);
    }} onPointerMove={event => { if (pan.current) { event.currentTarget.scrollLeft = pan.current.left + pan.current.x - event.clientX; event.currentTarget.scrollTop = pan.current.top + pan.current.y - event.clientY; } }} onPointerUp={() => { pan.current = null; }} onLostPointerCapture={() => { pan.current = null; }}>
      <article style={{ zoom }}><NoteMarkdown source={source} language={language}/></article>
    </div>
  </ViewerDialog>;
}
