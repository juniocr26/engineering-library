'use client';
import { useState, useSyncExternalStore } from 'react';
import { noteDemos, localizedDemoBody } from '../lib/note-demos';
import { textAnchor } from '../lib/text-anchors';
import type { Language } from '../lib/i18n';
export function NoteDemos({ project, documentId, language, csrf, changed }: { changed: () => Promise<void>; project: string; documentId: string; language: Language; csrf: string }) {
  const mounted = useSyncExternalStore(() => () => {}, () => true, () => false);
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const [manifest, setManifest] = useState<{ case: string; title: string; anchor: string; href: string }[]>([]);
  if (!mounted || project !== 'engineering-library' || process.env.NODE_ENV !== 'development' || typeof window === 'undefined' || !new URLSearchParams(window.location.search).has('noteDemos')) return null;
  const en = language === 'en';
  const supported = ['architecture/current-state.md', 'img/visual-components.md'].includes(documentId);
  const query = new URLSearchParams({ project, document: documentId, language });
  async function run(cleanup = false) {
    setBusy(true);
    try {
      if (cleanup) {
        const response = await fetch(`/api/note-demos?${query}`, { method: 'DELETE', headers: { 'X-Reader-CSRF': csrf } });
        if (!response.ok) throw Error('Cleanup failed');
        await changed(); window.dispatchEvent(new Event('reader-demonstrations-changed')); setManifest([]); setMessage(en ? 'Demonstrations removed for this reader throughout this project, in both languages.' : 'Demonstrações removidas deste leitor em todo o projeto, nos dois idiomas.'); return;
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
      await changed(); window.dispatchEvent(new Event('reader-demonstrations-changed')); setManifest(result); setMessage(en ? `${result.length} cases saved: 15 notes, 15 highlights, 3 bookmarks in this document and language. Open the annotation panels or a passage below.` : `${result.length} casos salvos: 15 notas, 15 destaques, 3 marcações neste documento e idioma. Abra os painéis de anotações ou um trecho abaixo.`);
    } catch (error) { await changed().catch(() => {}); window.dispatchEvent(new Event('reader-demonstrations-changed')); setMessage(String(error)); }
    finally { setBusy(false); }
  }
  return <details className="note-demo-tools"><summary>Development note demonstrations</summary><p>{en ? 'Seed current reader creates examples for this browser only, in the document and language shown. CLI demonstrations belong to a separate browser and do not populate this reader. Nothing is seeded automatically.' : 'Seed current reader cria exemplos somente para este navegador, no documento e idioma abertos. As demonstrações do CLI pertencem a outro navegador e não preenchem este leitor. Nada é criado automaticamente.'}</p><p>{en ? 'Open each document in both languages and seed it:' : 'Abra cada documento nos dois idiomas e execute o seed:'}</p><ul>{['en', 'pt-BR'].flatMap(lang => ['architecture/current-state.md', 'img/visual-components.md'].map(doc => <li key={`${lang}/${doc}`}><a href={`/projects/${project}/docs/${doc}?lang=${lang}&noteDemos=1`}>{lang} · {doc}</a></li>))}</ul><button disabled={busy || !csrf || !supported} onClick={() => void run()}>Seed current reader</button><button disabled={busy || !csrf} onClick={() => void run(true)}>Remove demonstration records</button><p role="status">{message}</p><ol>{manifest.map(item => <li key={item.case}><a href={item.href}>{item.case} — {item.title}</a> · {item.anchor}</li>)}</ol><button disabled={!manifest.length} onClick={() => { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([JSON.stringify({ project, document: documentId, language, cases: manifest }, null, 2)], { type: 'application/json' })); a.download = 'note-demonstrations.json'; a.click(); URL.revokeObjectURL(a.href); }}>Download manifest</button></details>;
}
