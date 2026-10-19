'use client';
import { Component, Fragment, memo, useEffect, useState, type ReactNode } from 'react';
import { toJsxRuntime } from 'hast-util-to-jsx-runtime';
import { jsx, jsxs } from 'react/jsx-runtime';
import type { Root } from 'hast';
import type { Components } from 'react-markdown';
import { NoteEmbed } from './note-embed';
import { noteRenderError } from '../lib/note-policy';
import { highlightedLines } from '../lib/syntax-highlight';
import { Diagram } from './markdown-unit';
import { CodeViewer } from './source-code';
import { ExpandableMedia, ExpandIcon } from './expandable-media';
import { ReaderTable, useTableScroll } from './reader-table';
import type { Language } from '../lib/i18n';

class NoteBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() { return this.state.failed ? <p role="alert">Preview unavailable. Return to the editor to revise the Markdown.</p> : this.props.children; }
}
function NoteTable({ children, language }: { children: ReactNode; language: Language }) {
  const scroll = useTableScroll('note-table');
  return <ReaderTable language={language} scroll={scroll} canSplit={false} fullTable={() => <div className="reader-markdown"><table>{children}</table></div>}>{children}</ReaderTable>;
}
function NoteCode({ source, grammar, language }: { source: string; grammar: string; language: Language }) {
  const [open, setOpen] = useState(false);
  const content = <pre><code className={`language-${grammar}`} dangerouslySetInnerHTML={{ __html: highlightedLines(source, grammar).join('\n') }}/></pre>;
  return <><div className="reader-code source-code">{content}</div><div className="media-controls"><button className="media-expand" aria-label={language === 'en' ? 'Expand code' : 'Ampliar código'} onClick={() => setOpen(true)}><ExpandIcon/></button></div>{open && <CodeViewer en={language === 'en'} path={grammar || (language === 'en' ? 'Code' : 'Código')} close={() => setOpen(false)}>{content}</CodeViewer>}</>;
}
export const NoteMarkdown = memo(function NoteMarkdown({ source, language }: { source: string; language: Language }) {
  const [result, setResult] = useState<{ source: string; tree?: Root; error?: string } | null>(null);
  const [cancelled, setCancelled] = useState(false);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    if (cancelled || noteRenderError(source)) return;
    const worker = new Worker(new URL('../lib/note-worker.ts', import.meta.url));
    worker.onmessage = event => { setResult({ ...event.data, source }); worker.terminate(); };
    worker.onerror = () => { setResult({ source, error: 'Preview unavailable. The original source is preserved.' }); worker.terminate(); };
    worker.postMessage(source);
    return () => worker.terminate();
  }, [source, cancelled, revision]);
  const error = noteRenderError(source) || (result?.source === source ? result.error : undefined);
  if (error) return <p role="alert">{error}</p>;
  const components: Components = {
    a: ({ href, children }) => href ? <a href={href} target={href.startsWith('http') ? '_blank' : undefined} rel="noopener noreferrer">{children}</a> : <span>{children}</span>,
    img: ({ src, alt, width, height, title }) => <ExpandableMedia width={width} height={height} title={title} src={typeof src === 'string' ? src : undefined} alt={alt ?? ''} language={language}/>,
    pre: ({ children }) => <div className="note-code-block">{children}</div>,
    code: ({ className, children }) => className === 'language-mermaid' ? <Diagram source={String(children).trim()} language={language} query=""/> : className || String(children).includes('\n') ? <NoteCode source={String(children)} grammar={className?.replace('language-', '') ?? ''} language={language}/> : <code>{children}</code>,
    table: ({ children }) => <NoteTable language={language}>{children}</NoteTable>,
  };
  return <NoteBoundary key={source}><div className="reader-markdown note-markdown">{!(result?.source === source && result.tree) ? <p role="status">{cancelled ? (language === 'en' ? 'Preview stopped.' : 'Prévia interrompida.') : (language === 'en' ? 'Rendering note…' : 'Renderizando nota…')} <button onClick={() => { setResult(null); setCancelled(value => !value); setRevision(value => value + 1); }}>{cancelled ? (language === 'en' ? 'Retry' : 'Tentar novamente') : (language === 'en' ? 'Cancel rendering' : 'Cancelar renderização')}</button></p> : toJsxRuntime(result.tree, { Fragment, jsx, jsxs, passKeys: true, passNode: true, ignoreInvalidStyle: true, components: { ...components, 'note-embed': ({ source }: { source: string }) => <NoteEmbed source={source} language={language}/> } as Parameters<typeof toJsxRuntime>[1]['components'] })}</div></NoteBoundary>;
});
