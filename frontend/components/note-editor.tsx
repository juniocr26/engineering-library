'use client';
import { useEffect, useRef, useState } from 'react';
import { ViewerDialog, viewerZoom, viewerPointerMove } from './expandable-media';
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
  const pending = useRef(false);
  const editor = useRef<HTMLTextAreaElement>(null);
  const en = language === 'en';
  const dirty = draft !== (current?.body ?? '');
  const finish = () => { if (!dirty || confirm(en ? 'Discard unsaved changes?' : 'Descartar alterações não salvas?')) close(); };
  useEffect(() => { const prevent = (event: BeforeUnloadEvent) => { if (dirty) event.preventDefault(); }; window.addEventListener('beforeunload', prevent); return () => window.removeEventListener('beforeunload', prevent); }, [dirty]);
  async function mutate(remove = false) {
    if (pending.current) return;
    if (remove && (draft.trim() || current?.body.trim()) && !confirm(en ? 'Delete this note? The highlight will remain.' : 'Excluir esta nota? O destaque será preservado.')) return;
    pending.current = true; setBusy(true); setMessage('');
    try {
      const response = await fetch(`/api/notes${current ? `/${current.id}` : ''}?${query}`, { method: remove ? 'DELETE' : current ? 'PATCH' : 'POST', headers: { 'Content-Type': 'application/json', 'X-Reader-CSRF': csrf }, body: remove ? undefined : JSON.stringify({ highlight_id: highlightId, body: draft }) });
      if (!response.ok) throw Error();
      if (remove) { removed(current!.id); close(); }
      else { const value = await response.json(); setCurrent(value); setDraft(value.body); saved(value); setMessage(current ? (en ? 'Note updated successfully.' : 'Nota atualizada com sucesso.') : (en ? 'Note saved successfully.' : 'Nota salva com sucesso.')); }
    } catch { setMessage(remove ? (en ? 'Could not delete the note. Try again.' : 'Não foi possível excluir a nota. Tente novamente.') : en ? 'Could not save. Your draft is preserved. Maximum: 128 KiB.' : 'Não foi possível salvar. Seu rascunho foi preservado. Máximo: 128 KiB.'); }
    finally { pending.current = false; setBusy(false); }
  }
  const bytes = new TextEncoder().encode(draft).length;
  return <ViewerDialog label={en ? 'Note editor' : 'Editor de nota'} close={() => { if (!busy) finish(); }} className="note-editor">
    <header><h2>{en ? 'Passage note' : 'Nota do trecho'}</h2><button disabled={busy} onClick={finish} aria-label={en ? 'Close note' : 'Fechar nota'}>×</button></header>
    <label htmlFor="note-draft">{en ? 'Markdown or plain text' : 'Markdown ou texto simples'}</label>
    <textarea id="note-draft" ref={editor} autoFocus readOnly={busy} value={draft} onChange={event => setDraft(event.target.value)} spellCheck/>
    <p role="status">{message || `${bytes.toLocaleString()} / 131.072 bytes`}</p>
    <footer><button disabled={busy || !current} onClick={() => void mutate(true)}>{en ? 'Delete note' : 'Excluir nota'}</button><button disabled={busy} onClick={() => setPreview(true)}>{en ? 'Preview' : 'Pré-visualizar'}</button><button disabled={busy || bytes > NOTE_MAX_BYTES} onClick={() => void mutate()}>{en ? 'Save' : 'Salvar'}</button></footer>
    {preview && <NotePreview source={draft} language={language} close={() => { setPreview(false); requestAnimationFrame(() => editor.current?.focus({ preventScroll: true })); }}/>}
  </ViewerDialog>;
}
function NotePreview({ source, language, close }: { source: string; language: Language; close: () => void }) {
  const [zoom, setZoom] = useState(1);
  const [pageWidth, setPageWidth] = useState<number>();
  const [panMode, setPanMode] = useState(false);
  const [dragging, setDragging] = useState(false);
  const scroll = useRef<HTMLDivElement>(null);
  const pointers = useRef(new Map<number, { x: number; y: number }>());
  const en = language === 'en';
  useEffect(() => {
    const node = scroll.current!;
    const resize = new ResizeObserver(() => setPageWidth(node.clientWidth));
    resize.observe(node);
    return () => resize.disconnect();
  }, []);
  const changeZoom = (factor: number) => setZoom(value => viewerZoom(value, factor, .75, 5));
  useEffect(() => {
    const node = scroll.current!;
    const wheel = (event: WheelEvent) => {
      if (node.closest('dialog') !== Array.from(document.querySelectorAll('dialog[open]')).at(-1)) return;
      if (event.ctrlKey || event.metaKey || panMode) { event.preventDefault(); changeZoom(Math.exp(-event.deltaY * .002)); }
    };
    node.addEventListener('wheel', wheel, { passive: false });
    return () => node.removeEventListener('wheel', wheel);
  }, [panMode]);
  const release = (id: number) => { pointers.current.delete(id); setDragging(false); };
  return <ViewerDialog label={en ? 'Note preview' : 'Prévia da nota'} close={close} className="note-preview">
    <div className="media-viewer-toolbar"><button aria-label={en ? 'Zoom out' : 'Reduzir'} disabled={zoom === .75} onClick={() => changeZoom(1 / 1.25)}>−</button><output aria-live="polite">{Math.round(zoom * 100)}%</output><button aria-label={en ? 'Zoom in' : 'Ampliar'} disabled={zoom === 5} onClick={() => changeZoom(1.25)}>+</button><button onClick={() => { setZoom(1); scroll.current?.scrollTo(0, 0); }}>{en ? 'Reset zoom' : 'Restaurar zoom'}</button><button aria-pressed={panMode} onClick={() => setPanMode(value => !value)}>{en ? 'Pan mode' : 'Modo arrastar'}</button><button autoFocus onClick={close}>{en ? 'Return to edit' : 'Voltar à edição'}</button></div>
    <p className="note-preview-help">{en ? 'Select text to copy. Enable pan mode to drag or pinch; Ctrl + wheel also zooms.' : 'Selecione texto para copiar. Ative o modo arrastar para mover ou usar pinça; Ctrl + roda também amplia.'}</p>
    <div ref={scroll} className="note-preview-scroll" tabIndex={0} data-pan={panMode} data-dragging={dragging} data-zoom={zoom} aria-label={en ? 'Scrollable note preview' : 'Prévia rolável da nota'} onPointerDown={event => {
      if (!panMode || event.button !== 0 || (event.target as Element).closest('a,button,table,pre')) return;
      event.preventDefault(); event.currentTarget.setPointerCapture(event.pointerId);
      pointers.current.set(event.pointerId, { x: event.clientX, y: event.clientY }); setDragging(true);
    }} onPointerMove={event => {
      const delta = viewerPointerMove(pointers.current, event.pointerId, { x: event.clientX, y: event.clientY });
      if (!delta) return;
      if (delta.factor !== 1) changeZoom(delta.factor);
      else { event.currentTarget.scrollLeft -= delta.x; event.currentTarget.scrollTop -= delta.y; }
    }} onPointerUp={event => release(event.pointerId)} onPointerCancel={event => release(event.pointerId)} onLostPointerCapture={event => release(event.pointerId)}>
      <article style={{ zoom, width: pageWidth }}><NoteMarkdown source={source} language={language}/></article>
    </div>
  </ViewerDialog>;
}
