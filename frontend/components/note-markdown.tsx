'use client';
import { Component, memo, useState, type ReactNode } from 'react';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { noteRenderError, noteUrl, noteTreeLimits } from '../lib/note-policy';
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
  const error = noteRenderError(source);
  if (error) return <p role="alert">{error}</p>;
  return <NoteBoundary key={source}><div className="reader-markdown note-markdown"><Markdown skipHtml remarkPlugins={[remarkGfm, noteTreeLimits]} urlTransform={noteUrl} components={{
    a: ({ href, children }) => href ? <a href={href} target={href.startsWith('http') ? '_blank' : undefined} rel="noopener noreferrer">{children}</a> : <span>{children}</span>,
    img: ({ src, alt }) => src ? <ExpandableMedia src={String(src)} alt={alt ?? ''} language={language}/> : <span role="status">{language === 'en' ? 'Image source not approved' : 'Origem de imagem não aprovada'}: {alt}</span>,
    pre: ({ children }) => <div className="note-code-block">{children}</div>,
    code: ({ className, children }) => className === 'language-mermaid' ? <Diagram source={String(children).trim()} language={language} query=""/> : className || String(children).includes('\n') ? <NoteCode source={String(children)} grammar={className?.replace('language-', '') ?? ''} language={language}/> : <code>{children}</code>,
    table: ({ children }) => <NoteTable language={language}>{children}</NoteTable>,
  }}>{source}</Markdown></div></NoteBoundary>;
});
