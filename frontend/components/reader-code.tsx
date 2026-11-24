'use client';
import { useEffect, useRef, useState } from 'react';
import { useHorizontalDrag } from './use-horizontal-drag';
import { useTableScroll } from './reader-table';
import { CodeCopy } from './code-copy';
import type { MarkdownUnit } from '../lib/markdown';

export function ReaderCode({ unit, language, query }: { unit: MarkdownUnit; language: 'en' | 'pt-BR'; query: string }) {
  const command = unit.command!;
  const all = command.value.split('\n');
  const part = unit.codePart ?? { start: 0, end: all.length };
  const viewport = useRef<HTMLDivElement>(null);
  const [overflow, setOverflow] = useState(false);
  const scroll = useTableScroll(`command/${unit.codeOrigin ?? unit.id}`);
  const { dragging, handlers } = useHorizontalDrag(overflow);
  const en = language === 'en';
  const help = en ? 'Drag the padding to scroll horizontally. Select text directly; use arrow keys to scroll.' : 'Arraste pelas margens para rolar horizontalmente. Selecione o texto diretamente; use as setas para rolar.';
  useEffect(() => {
    const node = viewport.current!;
    const update = () => { setOverflow(node.scrollWidth > node.clientWidth + 1); node.scrollLeft = scroll.get(); };
    const observer = new ResizeObserver(update);
    observer.observe(node); if (node.firstElementChild) observer.observe(node.firstElementChild);
    update(); return () => observer.disconnect();
  }, [scroll, command.value, part.start, part.end]);
  return <div className="reader-markdown reader-code-shell" data-highlight-unsupported>
    <div data-source-code={unit.codeOrigin ?? unit.id}>
      <div ref={viewport} className="reader-code" role="region" aria-label={en ? 'Code block' : 'Bloco de código'} tabIndex={0} title={overflow ? help : undefined} data-overflow={overflow} data-dragging={dragging} {...handlers} onScroll={event => scroll.set(event.currentTarget.scrollLeft)} style={part.maxHeight ? { maxHeight: part.maxHeight } : undefined}>
        <code>{all.slice(part.start, part.end).map((line, i) => {
          const at = query ? line.toLowerCase().indexOf(query.toLowerCase()) : -1;
          return <span className="reader-command-line" data-source-line={part.start + i} key={part.start + i}><span data-code-text>{at < 0 ? line || '\u200b' : <>{line.slice(0, at)}<mark>{line.slice(at, at + query.length)}</mark>{line.slice(at + query.length)}</>}</span></span>;
        })}</code>
      </div>
    </div>
    <div className="media-controls">
      {overflow && <span className="reader-table-hint" role="img" aria-label={help} title={help}>↔</span>}
      <CodeCopy text={command.value} en={en}/>
    </div>
  </div>;
}
