'use client';
import { createPortal } from 'react-dom';
import { readerIdentity } from '../lib/reader-identity';
import { useEffect, useRef, useState, type RefObject, type ReactNode } from 'react';
import { highlightColors, resolveTextAnchor, toolbarPosition, type HighlightColor, type SavedHighlight, type TextAnchor } from '../lib/text-anchors';
import { eligibleRanges, selectedAnchors, passageText } from '../lib/highlight-dom';
import type { Language } from '../lib/i18n';

type Registry = { set: (name: string, value: unknown) => void; delete: (name: string) => void };
type HighlightWindow = Window & { Highlight?: new (...ranges: Range[]) => unknown };

export function TextHighlights({ project, document: documentId, language, children }: { project: string; document: string; language: Language; children: ReactNode }) {
  const root = useRef<HTMLDivElement>(null);
  return <div ref={root} className="reader-highlights">{children}<HighlightSession key={`${project}/${documentId}/${language}`} root={root} project={project} documentId={documentId} language={language}/></div>;
}
function HighlightSession({ project, documentId, language, root }: { project: string; documentId: string; language: Language; root: RefObject<HTMLDivElement | null> }) {
  const [saved, setSaved] = useState<SavedHighlight[]>([]);
  const [csrf, setCsrf] = useState('');
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const pending = useRef(false);
  const [tool, setTool] = useState<{ segments: TextAnchor[]; text: string; left: number; top: number; id?: number; color?: HighlightColor } | null>(null);
  const en = language === 'en';
  const query = new URLSearchParams({ project, document: documentId, language }).toString();
  useEffect(() => {
    const controller = new AbortController();
    void readerIdentity(project, language).then(() => fetch(`/api/highlights?${query}`, { signal: controller.signal, cache: 'no-store' })).then(async response => { if (!response.ok) throw Error(); return response.json(); }).then(data => { if (!controller.signal.aborted) { setSaved(data.highlights); setCsrf(data.csrf_token); } }, () => { if (!controller.signal.aborted) setMessage(en ? 'Highlights unavailable. Reload to retry.' : 'Destaques indisponíveis. Recarregue para tentar novamente.'); });
    return () => controller.abort();
  }, [query, en, project, language]);
  useEffect(() => {
    const surface = root.current;
    const registry = (CSS as unknown as { highlights?: Registry }).highlights;
    const Constructor = (window as HighlightWindow).Highlight;
    if (!surface || !registry || !Constructor) return;
    let frame = 0;
    const paint = () => {
      const ranges = new Map(highlightColors.map(color => [color, [] as Range[]]));
      let unresolved = false;
      surface.querySelectorAll<HTMLElement>('.reader-pages [data-highlight-block]').forEach(block => {
        if (block.closest('[inert]')) return;
        for (const item of saved) for (const segment of item.segments) {
          if (segment.block !== block.dataset.highlightBlock) continue;
          const resolved = resolveTextAnchor(segment, block.textContent ?? '');
          if (!resolved) { unresolved = true; continue; }
          ranges.get(item.color)?.push(...eligibleRanges(block, ...resolved));
        }
      });
      for (const [color, values] of ranges) registry.set(`reader-${color}`, Object.assign(new Constructor(...values) as object, { priority: highlightColors.indexOf(color) }));
      // Report missing logical blocks too; off-page blocks remain in the measurement surface.
      for (const item of saved) for (const segment of item.segments) {
        const blocks = Array.from(surface.querySelectorAll<HTMLElement>('[data-highlight-block]')).filter(block => block.dataset.highlightBlock === segment.block);
        if (!blocks.some(block => resolveTextAnchor(segment, block.textContent ?? ''))) unresolved = true;
      }
      if (unresolved) setMessage(en ? 'Some saved passages changed and could not be restored safely.' : 'Alguns trechos salvos mudaram e não puderam ser restaurados com segurança.');
    };
    const schedule = () => { cancelAnimationFrame(frame); frame = requestAnimationFrame(paint); };
    const observer = new MutationObserver(schedule); observer.observe(surface, { subtree: true, childList: true, attributes: true, attributeFilter: ['inert', 'data-pagination', 'open', 'hidden', 'aria-hidden'] });
    schedule();
    return () => { observer.disconnect(); cancelAnimationFrame(frame); for (const color of highlightColors) registry.delete(`reader-${color}`); };
  }, [saved, en, root]);
  useEffect(() => {
    const surface = root.current;
    if (!surface) return;
    let timer: ReturnType<typeof setTimeout>;
    const capture = () => {
      const selection = window.getSelection();
      if (!selection || selection.isCollapsed || !selection.rangeCount) { setTool(null); return; }
      const range = selection.getRangeAt(0);
      const element = (node: Node) => node instanceof Element ? node : node.parentElement;
      const first = element(range.startContainer)?.closest<HTMLElement>('[data-highlight-block]');
      const last = element(range.endContainer)?.closest<HTMLElement>('[data-highlight-block]');
      if (!first || !last || !surface.contains(first) || !surface.contains(last) || !first.closest('.reader-pages') || !last.closest('.reader-pages') || first.closest('[inert]') || last.closest('[inert]')) {
        setTool(null);
        if (element(range.startContainer)?.closest('.reader-pages .reader-body') && element(range.endContainer)?.closest('.reader-pages .reader-body')) setMessage(en ? 'Select prose, headings or lists without code or media.' : 'Selecione texto, títulos ou listas sem código ou mídia.');
        return;
      }
      const blocks = Array.from(surface.querySelectorAll<HTMLElement>('.reader-pages [data-highlight-block]')).filter(block => !block.closest('[inert]') && range.intersectsNode(block));
      const segments = blocks.flatMap(block => selectedAnchors(block, range));
      if (segments.length > 32 || segments.some(part => part.exact.length > 8000)) {
        setTool(null); setMessage(en ? 'Selection is too large. Select a shorter passage.' : 'Seleção muito extensa. Selecione um trecho menor.'); return;
      }
      if (!segments.length || !segments.some(part => part.exact.trim())) { setTool(null); return; }
      if (!(CSS as unknown as { highlights?: Registry }).highlights) { setMessage(en ? 'This browser does not support text highlights.' : 'Este navegador não suporta destaques de texto.'); return; }
      const existing = saved.find(item => item.segments.length === segments.length && item.segments.every((part, index) => part.block === segments[index].block && part.start === segments[index].start && part.end === segments[index].end && part.exact === segments[index].exact));
      setTool({ segments, text: passageText(segments), id: existing?.id, color: existing?.color, ...toolbarPosition(range.getBoundingClientRect(), innerWidth, innerHeight) });
    };
    const changed = () => { clearTimeout(timer); const selection = window.getSelection(); setTool(previous => selection?.type === 'Caret' && previous?.id ? previous : null); if (selection && !selection.isCollapsed) timer = setTimeout(capture, 180); };
    const completed = (event: PointerEvent) => {
      if ((event.target as Element).closest?.('[role="toolbar"]')) return;
      if (!surface.contains(event.target as Node)) { clearTimeout(timer); setTool(null); return; }
      clearTimeout(timer); if (!window.getSelection()?.isCollapsed) timer = setTimeout(capture, 0);
    };
    const outside = (event: PointerEvent) => { if (!(event.target as Element).closest?.('[role="toolbar"]')) { clearTimeout(timer); setTool(null); } };
    const key = (event: KeyboardEvent) => { if (event.key === 'Escape') { clearTimeout(timer); setTool(null); window.getSelection()?.removeAllRanges(); } };
    const dismiss = () => setTool(null);
    const copySelection = (event: ClipboardEvent) => {
      const selection = window.getSelection();
      if (!event.clipboardData || !selection?.rangeCount || selection.isCollapsed) return;
      const range = selection.getRangeAt(0);
      if (!surface.contains(range.startContainer) || !surface.contains(range.endContainer)) return;
      const blocks = Array.from(surface.querySelectorAll<HTMLElement>('.reader-pages [data-highlight-block]')).filter(block => !block.closest('[inert]') && range.intersectsNode(block));
      const segments = blocks.flatMap(block => selectedAnchors(block, range));
      if (!segments.length) return;
      event.clipboardData.setData('text/plain', passageText(segments));
      event.preventDefault();
    };
    surface.addEventListener('copy', copySelection);
    document.addEventListener('pointerdown', outside); document.addEventListener('pointerup', completed); document.addEventListener('selectionchange', changed); document.addEventListener('keydown', key);
    window.addEventListener('resize', dismiss); window.addEventListener('scroll', dismiss, true);
    return () => { clearTimeout(timer); surface.removeEventListener('copy', copySelection); document.removeEventListener('pointerdown', outside); document.removeEventListener('pointerup', completed); document.removeEventListener('selectionchange', changed); document.removeEventListener('keydown', key); window.removeEventListener('resize', dismiss); window.removeEventListener('scroll', dismiss, true); };
  }, [en, root, saved]);
  async function mutate(color?: HighlightColor, remove = false) {
    if (!tool || pending.current || !csrf) return;
    pending.current = true; setBusy(true);
    try {
      const response = await fetch(`/api/highlights${tool.id ? `/${tool.id}` : ''}?${query}`, { method: remove ? 'DELETE' : tool.id ? 'PATCH' : 'POST', headers: { 'Content-Type': 'application/json', 'X-Reader-CSRF': csrf }, body: remove ? undefined : JSON.stringify({ color, segments: tool.segments }) });
      if (!response.ok) throw Error();
      if (remove) setSaved(previous => previous.filter(item => item.id !== tool.id));
      else { const item = await response.json(); setSaved(previous => [...previous.filter(old => old.id !== item.id), item]); }
      setTool(null); setMessage(''); window.getSelection()?.removeAllRanges();
    } catch { setMessage(en ? 'Could not save. Your highlights are unchanged; try again.' : 'Não foi possível salvar. Seus destaques foram preservados; tente novamente.'); }
    finally { pending.current = false; setBusy(false); }
  }
  async function copy() {
    if (!tool) return;
    try {
      await navigator.clipboard.writeText(tool.text);
      setTool(null); window.getSelection()?.removeAllRanges();
    } catch { setMessage(en ? 'Copy failed.' : 'Falha ao copiar.'); }
  }
  useEffect(() => {
    const surface = root.current;
    const click = (raw: Event) => {
      const event = raw as MouseEvent;
      if ((event.target as Element).closest('a,button,[role="toolbar"]') || !window.getSelection()?.isCollapsed) return;
      const block = (event.target as Element).closest<HTMLElement>('.reader-pages [data-highlight-block]');
      if (!block || block.closest('[inert]')) { setTool(null); return; }
      const candidates = saved.flatMap(item => item.segments.filter(segment => segment.block === block.dataset.highlightBlock).flatMap(segment => {
        const resolved = resolveTextAnchor(segment, block.textContent ?? '');
        return resolved ? eligibleRanges(block, ...resolved).map(range => ({ id: item.id, color: item.color, range })) : [];
      })).sort((a, b) => highlightColors.indexOf(b.color) - highlightColors.indexOf(a.color) || b.id - a.id);
      const hit = candidates.find(({ range }) => Array.from(range.getClientRects()).some(rect => event.clientX >= rect.left && event.clientX <= rect.right && event.clientY >= rect.top && event.clientY <= rect.bottom));
      const item = saved.find(item => item.id === hit?.id);
      if (item && hit) setTool({ ...item, text: passageText(item.segments), ...toolbarPosition(hit.range.getBoundingClientRect(), innerWidth, innerHeight) }); else setTool(null);
    };
    surface?.addEventListener('click', click);
    return () => surface?.removeEventListener('click', click);
  }, [saved, root]);
  return <>
    {message && <p className="reader-notice" role="status">{message}</p>}
    {tool && createPortal(<div role="toolbar" aria-label={en ? 'Text highlights' : 'Destaques de texto'} className="reader-selection-toolbar" style={{ left: tool.left, top: tool.top }} onPointerDown={event => event.preventDefault()}>
      {highlightColors.map((color, index) => <button type="button" key={color} aria-label={(en ? ['Yellow', 'Blue', 'Pink', 'Orange', 'Purple', 'Red', 'Green'] : ['Amarelo', 'Azul', 'Rosa', 'Laranja', 'Roxo', 'Vermelho', 'Verde'])[index]} aria-pressed={tool.color === color} style={{ backgroundColor: `var(--highlight-${color})` }} disabled={busy || !csrf} onClick={() => void mutate(color, tool.id !== undefined && tool.color === color)}/>)}
      <button type="button" aria-label={en ? 'Copy' : 'Copiar'} onClick={() => void copy()}>⧉</button>
      <button type="button" disabled aria-label={en ? 'Add note (available in Phase 2)' : 'Adicionar nota (disponível na fase 2)'} title={en ? 'Notes will be available in Phase 2' : 'Notas estarão disponíveis na fase 2'}><svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true"><path d="M13 5H5v15h14v-8M11 13l1-4 7-7 3 3-7 7-4 1Z"/></svg></button>
    </div>, document.body)}
  </>;
}
