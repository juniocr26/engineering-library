'use client';
import { Fragment, useMemo, type ReactNode } from 'react';
import { highlightedLines } from '../lib/syntax-highlight';
import { sourceLocation } from '../lib/source-links';
import type { MarkdownUnit } from '../lib/markdown';
function markedHtml(html: string, text: string, query: string): ReactNode {
  if (!query) return <span dangerouslySetInnerHTML={{ __html: html }}/>;
  // Highlight syntax tokens and search via text offsets, including matches crossing token boundaries.
  const starts: number[] = []; let at = 0;
  while ((at = text.toLowerCase().indexOf(query.toLowerCase(), at)) >= 0) { starts.push(at); at += query.length; }
  if (!starts.length) return <span dangerouslySetInnerHTML={{ __html: html }}/>;
  let position = 0;
  const marked = html.split(/(<[^>]+>)/).map(token => {
    if (token.startsWith('<')) return token;
    return token.split(/(&[a-z]+;|&#\d+;|&#x[a-f\d]+;|[^&])/i).filter(Boolean).map(character => {
      const match = starts.some(start => position >= start && position < start + query.length); position++;
      return match ? `<mark>${character}</mark>` : character;
    }).join('');
  }).join('');
  return <span dangerouslySetInnerHTML={{ __html: marked }}/>;
}
export function SourceCode({ unit, language, query, location }: { location?: string; unit: MarkdownUnit; language: 'en' | 'pt-BR'; query: string }) {
  const ref = unit.code!; const all = useMemo(() => ref.lines ?? [], [ref.lines]);
  const lines = useMemo(() => highlightedLines(all.join('\n'), ref.language), [all, ref.language]);
  const part = unit.codePart ?? { start: 0, end: all.length };
  const origin = unit.codeOrigin ?? unit.id; const first = ref.start ?? 1;
  const en = language === 'en';
  const reasons = { unapproved: en ? 'not approved for publication' : 'sem aprovação de publicação', missing: en ? 'file or snapshot unavailable' : 'arquivo ou snapshot indisponível', excluded: en ? 'excluded by source policy' : 'excluído pela política de fontes', 'revision-mismatch': en ? 'requested revision unavailable' : 'revisão solicitada indisponível', available: '' };
  if (ref.status !== 'available') return <p role="status" className="source-unavailable">{en ? 'Source unavailable' : 'Código indisponível'}: {ref.path} ({reasons[ref.status]}).</p>;
  return <section className={`source-code${part.start ? ' source-code--continuation' : ''}`} data-source-code={origin} aria-label={`${ref.path}, ${first + part.start}–${first + part.end - 1}`}>
    <div className="source-code-header" data-source-header><span>{ref.path}</span><span>{part.start ? (en ? 'continued · ' : 'continuação · ') : ''}{first + part.start}–{first + part.end - 1}</span></div>
    <div className="source-code-scroll" tabIndex={0} role="region" aria-label={en ? 'Source code, scroll horizontally' : 'Código-fonte, rolagem horizontal'} style={part.maxHeight ? { maxHeight: Math.max(1, part.maxHeight), overflowY: 'auto' } : undefined}>
      <pre><code>{all.slice(part.start, part.end).map((text, i) => <Fragment key={part.start + i}><span className="source-code-line" data-source-line={first + part.start + i} data-source-location={sourceLocation(ref, first + part.start + i)}><span className="source-code-number" aria-hidden="true">{first + part.start + i}</span><span>{markedHtml(lines[part.start + i], text, !location || sourceLocation(ref, first + part.start + i) === location ? query : '')}</span></span></Fragment>)}</code></pre>
    </div>
  </section>;
}
