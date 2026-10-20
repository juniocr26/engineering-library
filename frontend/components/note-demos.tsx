'use client';
import { useState, useSyncExternalStore } from 'react';
import { noteDemos, localizedDemoBody } from '../lib/note-demos';
import { textAnchor } from '../lib/text-anchors';
import type { Language } from '../lib/i18n';
export function NoteDemos({ project, documentId, language, csrf, changed }: { changed: () => void; project: string; documentId: string; language: Language; csrf: string }) {
  const mounted = useSyncExternalStore(() => () => {}, () => true, () => false);
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const [manifest, setManifest] = useState<{ case: string; title: string; anchor: string; href: string }[]>([]);
  if (!mounted || project !== 'engineering-library' || process.env.NODE_ENV !== 'development' || typeof window === 'undefined' || !new URLSearchParams(window.location.search).has('noteDemos')) return null;
  const query = new URLSearchParams({ project, document: documentId, language });
  async function run(cleanup = false) {
    setBusy(true);
    try {
      if (cleanup) {
        const response = await fetch(`/api/note-demos?${query}`, { method: 'DELETE', headers: { 'X-Reader-CSRF': csrf } });
        if (!response.ok) throw Error('Cleanup failed');
        changed(); setMessage('Demonstrations removed.'); return;
      }
      // The measurement surface includes every real logical unit, even off-page.
      const blocks = Array.from(document.querySelectorAll<HTMLElement>('.reader-measure [data-highlight-block], .reader-measurement [data-highlight-block], [data-measurement] [data-highlight-block]'));
      const candidates = blocks.length ? blocks : Array.from(document.querySelectorAll<HTMLElement>('[data-highlight-block]'));
      const unique = [...new Map(candidates.filter(block => !block.dataset.highlightUnsupported && (block.textContent ?? '').length > 8).map(block => [block.dataset.highlightBlock!, block])).values()];
      const entries = noteDemos;
      if (unique.length < entries.length) throw Error('This document needs more prose blocks. Use architecture/current-state.md.');
      const result = [];
      for (let i = 0; i < entries.length; i++) {
        const block = unique[i]; const text = block.textContent ?? '';
        const segment = textAnchor(block.dataset.highlightBlock!, text, 0, Math.min(text.length, 40));
        const id = String(i + 1).padStart(2, '0');
        const response = await fetch(`/api/note-demos?${query}`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Reader-CSRF': csrf }, body: JSON.stringify({ demo_key: `visual-${language}-${documentId.replace(/[^a-z0-9]/g, '-')}-${id}`, segments: [segment], body: localizedDemoBody(entries[i][1], language), color: ['yellow', 'blue', 'pink', 'orange', 'purple', 'red', 'green'][i % 7], remove_color: i === 14 }) });
        if (!response.ok) throw Error(`Case ${id}: ${response.status}`);
        result.push({ case: id, title: entries[i][0], anchor: segment.block, href: `${location.pathname}?lang=${language}&noteDemos=1#${encodeURIComponent(segment.block)}` });
      }
      for (const [index, kind] of ['bookmark', 'bookmark', 'bookmark', 'highlight'].entries()) {
        const block = unique[[0, Math.floor(unique.length / 2), unique.length - 1, Math.min(16, unique.length - 1)][index]];
        const text = block.textContent ?? '';
        const segment = textAnchor(block.dataset.highlightBlock!, text, 0, Math.min(text.length, 40));
        const response = await fetch(`/api/note-demos?${query}`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Reader-CSRF': csrf }, body: JSON.stringify({ demo_key: `visual-${language}-${documentId.replace(/[^a-z0-9]/g, '-')}-${kind}-${index}`, kind, color: 'yellow', segments: [segment], body: '' }) });
        if (!response.ok) throw Error(`${kind}: ${response.status}`);
        result.push({ case: `${kind}-${index}`, title: kind, anchor: segment.block, href: `${location.pathname}?lang=${language}&noteDemos=1#${encodeURIComponent(segment.block)}` });
      }
      changed(); setManifest(result); setMessage(`${result.length} cases saved. Open a passage below; click its ✎ indicator.`);
    } catch (error) { setMessage(String(error)); }
    finally { setBusy(false); }
  }
  return <details className="note-demo-tools"><summary>Development note demonstrations</summary><button disabled={busy || !csrf} onClick={() => void run()}>Seed current reader</button><button disabled={busy || !csrf} onClick={() => void run(true)}>Remove demonstration records</button><p role="status">{message}</p><ol>{manifest.map(item => <li key={item.case}><a href={item.href}>{item.case} — {item.title}</a> · {item.anchor}</li>)}</ol><button disabled={!manifest.length} onClick={() => { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([JSON.stringify({ project, document: documentId, language, cases: manifest }, null, 2)], { type: 'application/json' })); a.download = 'note-demonstrations.json'; a.click(); URL.revokeObjectURL(a.href); }}>Download manifest</button></details>;
}
